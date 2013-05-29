# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2013 by Erwin Marsi and TST-Centrale
#
# This file is part of the DAESO Framework.
#
# The DAESO Framework is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# The DAESO Framework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
automatic text alignment in parallel text corpora
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"


# TODO:
# - doc
# - clean up daeso.string
# - unittests
# - rewrite HitaextDoc class 

import string
from math import sqrt

from daeso.pair import Pair
from daeso.ptc.ielemtree import IndexElemTree
from daeso.string import similar as sim
from daeso.string.ngram import n_gram_strings
from daeso_nl.string.stopword import remove_stopwords
from daeso.string.tf_idf import tf_idf



class TextAlignerBase(object):
    """
    Abstract base class for text alignment in parallel/comparable text corpora.
    
    Focus tags specify the tags of elements which are candidates for automatic
    alignment. For example, in sentence alignment the source and target focus
    tags are typically "s" (sentence).
    
    Scope tags specify the tags of elements which limit the scope of automatic
    alignments. Scope elements must be already aligned in the input corpus.
    Source focus elements within the subtree of a certain source scope element
    will only be aligned to target focus elements within the subtree of the
    aligned target scope element. For example, in sentence alignment the scope
    tags are typically "p" (paragraph). Focus element outside of the scope of
    aligned scope elements will remain unaligned.
    
    Ignore tags specify the tags of elements which are ignored during
    alignment. Focus element within the subtree the subtree of an ignored
    element will remain unaligned.
    """
    
    def __init__(self, focus_tags, scope_tags=None, ignore_tags=None):
        """
        Create a new TextAligner instance
        
        @param focus_tags: a pair of soure and target focus tags
        
        @keyword scope_tags: a pair of source and target scope tag lists;
        defaults to the labels of the roots of the source and target document
        trees.
        
        @keyword ignore_tags: a pair of source and target ignore tag lists
        """
        self.focus_tags = focus_tags
        self.scope_tags = scope_tags
        self.ignore_tags = ignore_tags or Pair([],[])
        

    def align_corpus(self, corpus, doc_trees=None, clear=True):
        """
        Align a parallel text corpus
        
        @param corpus: parallel text corpus instance (HitaextDoc)
        
        @keyword doc_trees: pair of source and target document trees; only
        useful in experiments to prevent repeatedly rereading of the document
        trees
        
        @keyword clear: if true all existing alignments involving elements
        with focus tags are removed
        
        Alignments are added to the <alignment> section of the corpus.
        """
        if clear:
            clear_alignments(corpus, self.focus_tags)
            
        if not doc_trees:
            doc_trees = Pair(
                get_doc_tree(corpus, "from", self.ignore_tags.source),
                get_doc_tree(corpus, "to", self.ignore_tags.target))
            
            # copy alignments from <aligment> section in corpus
            # to "_alignments" attribute on elements
            corpus.inject_alignments(doc_trees.source, 
                                     doc_trees.target)
        
        if self.scope_tags:
            scope_tags = self.scope_tags
        else:
            # when scope is not specified, assume that scope tag is root tag,
            # and that roots are aligned
            source_root = doc_trees.source.getroot()
            target_root = doc_trees.target.getroot()
            scope_tags = Pair([source_root.tag], [target_root.tag])
            source_root.set("_alignments", [target_root])
            
        # TODO: semantics not entirely clear. 
        # - what happens if scope tags are embedded?
        # - What happens if scope elements are aligned 1-to-n?
        for source_scope_elem in doc_trees.source.getiterator():
            if source_scope_elem.tag not in scope_tags.source:
                continue
            
            for target_scope_elem in source_scope_elem.get("_alignments"):
                if target_scope_elem.tag not in scope_tags.target:
                    continue

                scope_elems = Pair(source_scope_elem, target_scope_elem)
                self._align_within_scope(doc_trees,
                                         scope_elems)
    
        # finally copy alignment from "_alignments" attribute on elements
        # to <aligment> section in corpus
        corpus.extract_alignments(doc_trees.source, 
                                  doc_trees.target)
        
    
    # private
    
    def _align_within_scope(self, doc_trees, scope_elems):
        """
        align focus elements within scope elements
        """
        raise NotImplementedError("must be provided by subclass")
            
    
    
class TextAligner(TextAlignerBase):
    """
    Abstract class for text alignment in parallel/comparable text corpora.
    
    This class is more committed to a particular processing flow for automatic
    alignment than the TextAlignerBase class. It assumes the following steps:
    
    1. determine focus elements
    2. extract terms
    3. weight terms
    4. score similarity
    5. filter scores
    6. create alignments
    """
    
    def __init__(self, focus_tags, scope_tags=None, ignore_tags=None,
                 term_func=None, weight_func=None, sim_func=None, 
                 filter_func=None):
        """
        Create a new TextAligner instance
        
        @param focus_tags: a pair of soure and target focus tags
        
        @keyword scope_tags: a pair of source and target scope tag lists;
        defaults to the labels of the roots of the source and target document
        trees.
        
        @keyword ignore_tags: a pair of source and target ignore tag lists
        
        @keyword term_func: term extraction function
        
        @keyword weight_func: term weighting function
        
        @keyword sim_func: similarity function
        
        @keyword filter_func: score filtering function
        
        """
        TextAlignerBase.__init__(self, focus_tags, scope_tags, ignore_tags)
        self.term_func = term_func or word_n_gram_factory(1)
        self.weight_func = weight_func or no_weight
        self.sim_func =  sim_func or equals_sim
        self.filter_func = filter_func or no_filter
    
        
    def _align_within_scope(self, doc_trees, scope_elems):
        """
        align focus elements within scope elements
        """
        focus_elem_lists = self._determine_focus_elems(scope_elems)
        if focus_elem_lists.source and focus_elem_lists.target:
            self._extract_terms(doc_trees, focus_elem_lists)
            self._weight_terms(focus_elem_lists)
            scores = self._score_sim(focus_elem_lists)
            scores = self._filter_scores(scores)
            self._create_alignments(scores)
        
        
    def _determine_focus_elems(self, scope_elems):
        source_list = [ 
            elem
            for elem in scope_elems.source.findall(".//" + 
                                                   self.focus_tags.source)
            if not elem.get("_ignore") ]
        
        target_list = [ 
            elem
            for elem in scope_elems.target.findall(".//" + 
                                                   self.focus_tags.target)
            if not elem.get("_ignore") ]
        
        return Pair(source_list, target_list)
    
    
    def _extract_terms(self, doc_trees, focus_elem_lists):
        for doc_tree, focus_elem_list in zip(doc_trees, focus_elem_lists):
            for focus_elem in focus_elem_list:
                text = doc_tree.get_elem_text(focus_elem)
                terms = self.term_func(text)
                focus_elem.set("_terms", terms)
            
            
    def _weight_terms(self, focus_elem_lists):
        all_elem = focus_elem_lists.source + focus_elem_lists.target
        terms_per_elem = [ elem.get("_terms")
                           for elem in all_elem ]
        
        weights_per_elem = self.weight_func(terms_per_elem)
        
        for focus_elem, weights in zip(all_elem, weights_per_elem):
            focus_elem.set("_weights", weights)
            
                
                
    def _score_sim(self, focus_elem_lists):
        scores = []
        
        for source_focus_elem in focus_elem_lists.source:
            for target_focus_elem in focus_elem_lists.target:
                sim = self.sim_func(
                    source_focus_elem.get("_terms"),
                    target_focus_elem.get("_terms"),
                    source_focus_elem.get("_weights"),
                    target_focus_elem.get("_weights"))
                focus_elems = Pair(source_focus_elem, target_focus_elem)
                scores.append((sim, focus_elems))
                
        return scores
    
    
    def _filter_scores(self, scores):
        return self.filter_func(scores)
    
    
    def _create_alignments(self, align_scores):
        """
        add alignment to _alignments attribute on source focus elements
        """
        for score, focus_elems in align_scores:
            source_alignments = focus_elems.source.get("_alignments")
            
            if focus_elems.target not in source_alignments:
                source_alignments.append(focus_elems.target)



#-------------------------------------------------------------------------------
# support functions
#-------------------------------------------------------------------------------
       
def get_doc_tree(corpus, side, ignore_tags):
    doc_fn = corpus.get_filename(side)
    tree = IndexElemTree(filename=doc_fn)
    # among other things, the update will insert a "_ignore" attribute on
    # all elements in the subtree of an element with an ignored tag
    tree.update(ignoreTags=ignore_tags)
    return tree


def clear_alignments(corpus, focus_tags):
    corpus.alignment[:] = [ link
                            for link in corpus.alignment 
                            if ( link.get("from_tag") != focus_tags.source and 
                                 link.get("to_tag") != focus_tags.target) ]
    
#-------------------------------------------------------------------------------
# term extraction functions
#-------------------------------------------------------------------------------
    

def word_n_gram_factory(n):
    def func(text):
        return n_gram_strings(text.split(), n)
    
    func.__name__ = "word_%d_gram" % n
    return func
    

def char_n_gram_factory(n):
    def func(text):
        return n_gram_strings(list(text), n)
    
    func.__name__ = "char_%d_gram" % n
    return func



def preproc_word_n_gram_factory(n):
    def func(text):
        # the ignore_case ignores case when removing stopwords,
        # but does not return the tokens lower cased!!!
        text = [ token.lower()
                 for token in text.split()
                 if text not in string.punctuation ]
        return n_gram_strings(text, n)
    
    func.__name__ = "preproc_word_%d_gram" % n
    return func


def preproc_stopword_word_n_gram_factory(n):
    def func(text):
        # the ignore_case ignores case when removing stopwords,
        # but does not return the tokens lower cased!!!
        text = remove_stopwords(text.lower().split(), 
                                ignore_case=True, 
                                remove_punc=True)
        return n_gram_strings(text, n)
    
    func.__name__ = "preproc_word_%d_gram" % n
    return func


def preproc_char_n_gram_factory(n):
    def func(text):
        # the ignore_case ignores case when removing stopwords,
        # but does not return the tokens lower cased!!!
        text = remove_stopwords(text.lower().split(), 
                                ignore_case=True, 
                                remove_punc=True)
        return n_gram_strings(list(text), n)
    
    func.__name__ = "preproc_char_%d_gram" % n
    return func


#-------------------------------------------------------------------------------
# weighting functions
#-------------------------------------------------------------------------------

def no_weight(terms_per_elem):
    return [None for i in range(len(terms_per_elem))]
    

def tf_idf_indicator_weight(terms_per_elem):
    # consider the pair of documents as a combined collection 
    # of N-single sentence documents
    # tf is either 1 or 0, depending on wether the term occurs in the sentence
    terms, weights = tf_idf(terms_per_elem, normalized=True, indicator=True)
    return weights

        
        
#-------------------------------------------------------------------------------
# similarity functions
#-------------------------------------------------------------------------------

def equals_sim(source_terms, target_terms, *args):
    return float(source_terms == target_terms)


def jaccard_sim(source_terms, target_terms, *args):
    return sim.jaccard(source_terms, target_terms)

def dice_sim(source_terms, target_terms, *args):
    return sim.dice(source_terms, target_terms)

def cosine_sim(source_terms, target_terms, *args):
    return sim.cosine(source_terms, target_terms)

def tanimoto_sim(source_terms, target_terms, *args):
    return sim.tanimoto(source_terms, target_terms)

def type_match_sim(source_terms, target_terms, *args):
    return sim.type_match(source_terms, target_terms)

def overlap_min_sim(source_terms, target_terms, *args):
    return sim.overlap_min(source_terms, target_terms)

def overlap_max_sim(source_terms, target_terms, *args):
    return sim.overlap_max(source_terms, target_terms)


def weighted_cosine_sim(source_terms, target_terms,
                        source_weights, target_weights):
    dot_prod = sum([w1 * w2 
                    for w1,w2 in zip(source_weights, target_weights)])
    v1_len = sum([w ** 2 for w in source_weights])
    v2_len = sum([w ** 2 for w in target_weights])
    
    try:
        return dot_prod / sqrt(v1_len * v2_len)
    except ZeroDivisionError:
        return 0.0

#-------------------------------------------------------------------------------
# filter functions
#-------------------------------------------------------------------------------

def no_filter(scores):
    return scores


def threshold_filter_factory(threshold):
    def func(scores):
        return [ score
                 for score in scores
                 if score[0] > threshold ]
    
    func.__name__ = "threshold_filter_%d" % threshold
    return func
    

def no_cross_filter_factory(threshold):
    def func(scores):
        # sort scores in descending order
        scores.sort(reverse=True)
        align_indices = []
        filtered_scores = []
        
        # Prevent crossing alignments. This relies on the "_n" attribute which
        # is added by IndexElemTree
        for score, focus_elems in scores:
            if score < threshold:
                break
            
            source_n = focus_elems.source.get("_n")
            target_n = focus_elems.target.get("_n")
            
            for i, j in align_indices:
                if i < source_n and j > target_n:
                    break
                if i > source_n and j < target_n:
                    break
            else:
                align_indices.append((source_n, target_n))
                filtered_scores.append((score, focus_elems))
                
        return filtered_scores

    func.__name__ = "no_cross_filter_%d" % threshold
    return func
    


    