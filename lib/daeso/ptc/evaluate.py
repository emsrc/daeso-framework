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
evaluation of text alignment in parallel text corpora
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"

# TODO:
# - unittests

import os
from daeso.ptc.document import HitaextDoc

    
def eval_alignment(filename_pairs, tag, labels=None): 
    """
    Print an evaluation of the alignment w.r.t. tag 
    
    @param corpus_pairs: list of filename pairs consisting of a true and a
    predicted parallel text corpus
    
    @param tag: only alignments involving this tag are considered
    
    @keyword label_pairs: list of string labels
    """
    overall_true = overall_pred = overall_common = 0
    
    print ( "    #true:    #pred:  #common:    ratio:"
            "     prec:      rec:  f-score:   label:" )
    print 128 * "-"
    
    if not labels:
        labels = [ os.path.basename(pair[1]) 
                   for pair in filename_pairs ]
    
    for (true_fn, pred_fn), label in zip(filename_pairs, labels):
        true_corpus = HitaextDoc(file=true_fn)
        pred_corpus = HitaextDoc(file=pred_fn)
        n_true, n_pred, n_common = count_alignment(true_corpus, 
                                                   pred_corpus,
                                                   tag)
        overall_true += n_true
        overall_pred += n_pred
        overall_common += n_common
        ratio, prec, rec, f = compute_scores(n_true, n_pred, n_common)
        print "%10d%10d%10d%10.2f%10.2f%10.2f%10.2f   %s" % (
            n_true,
            n_pred,
            n_common,
            ratio,
            prec, 
            rec,
            f,
            label)

    ratio, prec, rec, f = compute_scores(overall_true, 
                                         overall_pred, 
                                         overall_common)
    print 128 * "-"
    print "%10d%10d%10d%10.2f%10.2f%10.2f%10.2f" % (
        overall_true,
        overall_pred,
        overall_common,
        ratio,
        prec, 
        rec,
        f)


def get_alignment(corpus, tag):
    alignments = set()
    
    for link_elem in corpus.get_alignments():
        if ( link_elem.get('from_tag') == tag and 
             link_elem.get('to_tag') == tag ):
            alignments.add((
                link_elem.get('from_id'),
                link_elem.get('to_id')))
            
    return alignments


def count_alignment(true_corpus, pred_corpus, tag):
    # count per file, because we cannot collect alignments over multiple files
    # without id clashes
    true_alignments = get_alignment(true_corpus, tag)
    pred_alignments = get_alignment(pred_corpus, tag)
    
    return (
        len(true_alignments),
        len(pred_alignments),
        len(true_alignments & pred_alignments))

    
def compute_scores(n_true, n_pred, n_common):
    try:
        ratio = n_pred / float(n_true)
    except ZeroDivisionError:
        ratio = 0.0 
    
    try:
        recall = n_common / float(n_true)
    except ZeroDivisionError:
        recall = 0.0
        
    try:
        precision = n_common / float(n_pred)
    except ZeroDivisionError:
        precision = 0.0
        
    try:
        f = (2 * precision * recall ) / (precision + recall)
    except ZeroDivisionError:
        f = 0.0
        
    return ratio, precision, recall, f


