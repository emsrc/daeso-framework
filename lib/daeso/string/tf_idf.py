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
tf*idf weights (term frequencyâinverse document frequency)

@book{SaltonMcGill:1983,
    Address = {New York},
    Author = {Gerard Salton and Michael McGill},
    Publisher = {McGraw-Hill, Inc.},
    Title = {Introduction to Modern Information Retrieval},
    Year = 1983}
"""

# TODO:
# - proper doc strings
# - option to return sparse weight vector (zero's filtered)


__authors__ = "Erwin Marsi <e.marsi@gmail.com>"


import math


def idf(terms_per_doc, normalized=False):
    """
    Description
    
        calculates idf (inverse document frequency)
        weights for terms in a collection of documents
    
    1st argument: doc_terms_collection
    
        A collection of document terms in the form a list of lists where
        each embedded list specifies the terms in a particular document.
    
    Return value
    
        The idf term weights in the form of a list of lists where each
        embedded list contains the weights of the corresponding terms in
        doc_terms_collection.
        
    Examples
    
        doc_terms_collection = [ ["t1", "t2", "t1", "t3"],
                                 ["t4", "t1", "t2", "t2"] ]
                                 
        tf_idf(doc_terms_collection) == [
TODO
             ]
        
    Notes
    
        The input consists of document terms (tokens) rather than documents,
        so you can do your own preprocessing (removing stopwords, stemming,
        etc.)
    
        The implementation is not very efficient and probably not suitable for
        processing large document collections.
    """
    # TODO: reimplemnet
    # reusing the function for tf*idf calculation introduces ovrhead here

    all_terms, term_freq_per_doc = calculate_term_frequencies(terms_per_doc)
    doc_freq = calculate_document_frequencies(term_freq_per_doc)

    docs_count = float(len(terms_per_doc))
    weights_per_doc = []
    
    if normalized:
        # note that the minimal value of idf is zero (term occurs in all docs)
        # and its maximum value is log(docs_count/1) = log(docs_count),
        # so we can normalize idf by simply dividing by logs(docs_count) 
        norm = math.log(docs_count)
    else:
        norm = 1
    
    # using list comprehensions might speed this up     
    for i in range(len(terms_per_doc)):
        doc_weights = []
        
        for term in all_terms:
            # doc_freq can never be zero or larger than docs_count
            idf = math.log(docs_count / doc_freq[term])
            idf = idf / norm
            doc_weights.append(idf)
            
        weights_per_doc.append(doc_weights)

    return all_terms, weights_per_doc


def tf_idf(terms_per_doc, normalized=False, indicator=False):
    """
    Description
    
        calculates tf*idf (term frequency–inverse document frequency)
        weights for terms in a collection of documents
    
    1st argument: doc_terms_collection
    
        A collection of document terms in the form a list of lists where
        each embedded list specifies the terms in a particular document.
    
    Return value
    
        The tf*idf term weights in the form of a list of lists where each
        embedded list contains the weights of the corresponding terms in
        doc_terms_collection.
        
    Examples
    
        doc_terms_collection = [ ["t1", "t2", "t1", "t3"],
                                 ["t4", "t1", "t2", "t2"] ]
                                 
        tf_idf(doc_terms_collection) == [
           [ -0.20273255405408222, -0.10136627702704111, 
             -0.20273255405408222, 0.17328679513998632 ], 
           [ 0.17328679513998632, -0.10136627702704111, 
             -0.20273255405408222, -0.20273255405408222] ]
        
    Notes
    
        The input consists of document terms (tokens) rather than documents,
        so you can do your own preprocessing (removing stopwords, stemming,
        etc.)
    
        The implementation is not very efficient and probably not suitable for
        processing large document collections.
    """
    all_terms, term_freq_per_doc = calculate_term_frequencies(terms_per_doc)
    doc_freq = calculate_document_frequencies(term_freq_per_doc)

    docs_count = float(len(terms_per_doc))
    weights_per_doc = []
    
    if normalized:
        # Note that the minimal value of idf is zero (term occurs in all docs)
        # and its maximum value is log(docs_count/1) = log(docs_count).
        # so we can normalize idf by simply dividing by logs(docs_count) 
        norm = math.log(docs_count)
    else:
        norm = 1
        
    # using list comprehensions might speed this up     
    for doc_terms, doc_term_freq in zip(terms_per_doc, term_freq_per_doc):
        doc_weights = []
        
        for term in all_terms:
            if indicator:
                tf = float(term in doc_terms)
            else:
                try:
                    tf = doc_term_freq.get(term, 0) / float(len(doc_terms))
                except ZeroDivisionError:
                    # this happens with empty documents 
                    tf = 0.0
            # doc_freq can never be zero 
            
            idf = (math.log(docs_count / doc_freq[term])) / norm
            doc_weights.append(tf * idf)
            
        weights_per_doc.append(doc_weights)

    return all_terms, weights_per_doc


def calculate_document_frequencies(term_freq_per_doc):
    """
    returns a table that for each term counts in how many of the *documents*
    it occurred
    """
    # this is the "df" in "tf*idf"
    doc_freq = {}
    
    for term_freq in term_freq_per_doc:
        for term in term_freq:
            try:
                doc_freq[term] += 1
            except KeyError:
                doc_freq[term] = 1
                
    return doc_freq
    
    
def calculate_term_frequencies(terms_per_doc):
    """
    takes terms per document, in the form of a list of document term lists,
    and produces term counts per document, in the form of a list of dicts
    where keys are terms and values are counts (per document)
    """
    # this is "tf" in "tf*idf" - it is like "sort | uniq -c"
    terms = {}
    term_freq_per_doc = []
    
    for doc_terms in terms_per_doc:
        docs_term_freq = {}
        
        for term in doc_terms:
            terms[term] = True
                
            try:
                docs_term_freq[term] += 1
            except KeyError:
                docs_term_freq[term] = 1
                
        term_freq_per_doc.append(docs_term_freq)
    
    terms = terms.keys()
    terms.sort()
    
    return terms, term_freq_per_doc
        
        
        
        
        
        
        
        
        