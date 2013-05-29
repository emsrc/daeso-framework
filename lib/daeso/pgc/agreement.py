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
analyse inter-annotator agreement
"""

# Even though it works, this is all a little messy, as it reuses old code from
# the previous approach to calculating agreement. However, since this code
# will be rarely used - except at the end of a corpus development cycle -
# cleaning it up has low priority.


__authors__ = "Erwin Marsi <e.marsi@gmail.com>"


import sys
import math
import pickle

from daeso.pgc.corpus import ParallelGraphCorpus, LOAD_SPARSE, LOAD_NONE
from daeso.pgc.evaluate import AlignEval, AlignCounts


def run_eval(corpus_fns, annotators, pickle_fn=None, words_only=False):
    """
    Runs an evaluation of inter-annotator agreement. Takes as imput a list of
    filenames of annotated parallel graph corpora (with differces in node node
    alignment only), and a list of annotator names. Returns a tuple with the
    outputs from the functions cross_evaluate and tableize. Optionally pickles
    to a file.
    """
    align_eval = cross_evaluate(corpus_fns, annotators, words_only=words_only)
    align_eval.write()
    
    tables = tableize(align_eval)
    write_tables(tables)
    
    if pickle_fn:
        pickle.dump((align_eval, tables), open(pickle_fn, "wb"))
        
    return align_eval, tables


def write_tables(tables):
    for rel, val in tables.items():
        print 80 * "="
        print "Agreement on relation", rel
        print 80 * "=" + "\n"
        
        for measure, table in val.items():
            table.write(header=measure.upper(), percent=True)
        
    
def tableize(align_eval, pickle_fn=None):
    """
    Creates tables and calculates overall statistics. Takes as input an
    AlignEval object resulting from a call to "cross_evaluate". Returns a dict
    mapping relation names to measures to AnalysesTable objects. Optionally
    pickles to a file.
    """
    annotators = dict(align_eval.names).keys()
    annotators.sort()
    relations = align_eval.keys()
    measures = AlignCounts.measure_keys 
    tables = {}
    
    for rel in relations:
        tables[rel] = {}
        
        for m in measures:
            tables[rel][m] = am = AnalysesTable(annotators)
            
            for (true_annot, pred_annot), align_count in zip(align_eval.names, 
                                                             align_eval[rel]):
                am[true_annot][pred_annot] = align_count.measures[m]
                
            am.calculate_statistics()
            
    if pickle_fn:
        pickle.dump(tables, open(pickle_fn, "wb"))
        
    return tables
           
    

def cross_evaluate(corpus_fns, annotators=None, pickle_fn=None,
                   words_only=False):
    """
    Performs a cross evaluation of each annotator against each of the other
    ones. Returns an AlignEval object. Optionally pickles to a file.
    """
    if annotators:
        assert len(annotators) == len(corpus_fns)
    else:
        annotators = ["A%d" % (i+1) 
                      for i in range(len(corpus_fns))]
        
    corpora = read_corpora(corpus_fns, words_only)
    align_eval = AlignEval()
    
    for true_corp, true_annot in zip(corpora, annotators):
        for pred_corp, pred_annot in zip(corpora, annotators):
            if true_annot != pred_annot:
                name = (true_annot, pred_annot)
                align_eval.add(true_corp, pred_corp, name)

    align_eval.run_eval()
        
    if pickle_fn:
        pickle.dump(align_eval, open(pickle_fn, "wb"))
        
    return align_eval


def read_corpora(corpus_fns, words_only):
    corpora = []
    
    if words_only:
        graph_loading = LOAD_SPARSE
    else:
        graph_loading = LOAD_NONE
        
    for fn in corpus_fns:
        corpus = ParallelGraphCorpus(inf=fn, graph_loading=graph_loading)
    
        if words_only:
            # Remove any alignments involving a non-terminal node.
            # This is a bit of a hack, and inefficient also. However, I don't
            # want to complicate align_eval.add, or introduce a WordAlignEval
            # class, for an option that will be rarely used
            for graph_pair in corpus:
                graphs = graph_pair.get_graphs()
                
                for nodes, relation in graph_pair.alignments():
                    if ( graphs.source.node_is_non_terminal(nodes.source) or
                         graphs.target.node_is_non_terminal(nodes.target) ):
                        graph_pair.del_align(nodes)
    
        corpora.append(corpus)
    return corpora


        
class AnalysesTable(dict):
    """
    A square matrix to store evaluation results when multiple predictions
    are compared against each other.
    Provides calculation of column means and standard deviations,
    as well as overall mean and standard deviation.
    """

    def __init__(self, labels):
        dict.__init__(self)
        self.labels = labels

        # The matrix is implemnented as a dict of dicts,
        # without initialisation of the cells.
        # As a matter of fact, the values on diagonal are never used.
        # Two more rows are added to contain the mean and SD values.
        # These also have one more column to hold the overall mean
        # and overall SD respectively
        for label in self.labels + ["mean", "SD"]:
            self[label] = dict()


    def calculate_statistics(self):
        self.calculate_av()
        self.calculate_sd()


    def calculate_av(self):
        """
        calculate average, skipping values on the diagonal
        """
        overall_sum = 0.0
        col_n = len(self.labels) - 1

        # The matrix may be symmetrical, but we do not count on it
        for col_label in self.labels:
            col_sum = 0.0

            for row_label in self.labels:
                if col_label != row_label:
                    col_sum += self[row_label][col_label]

            self["mean"][col_label] = col_sum / col_n

            overall_sum += col_sum

        overall_n = len(self.labels) * col_n
        self["mean"]["overall"] = overall_sum / overall_n


    def calculate_sd(self):
        """
        calculate sample standard deviation, skipping values on the diagonal
        """
        overall_dev = 0.0
        col_n = len(self.labels) - 1
        overall_av = self["mean"]["overall"] 

        for col_label in self.labels:
            col_dev = 0.0
            col_av = self["mean"][col_label] 

            for row_label in self.labels:
                if col_label != row_label:
                    col_dev += (self[row_label][col_label] - col_av) ** 2
                    overall_dev += (self[row_label][col_label] - overall_av) ** 2

            try:
                self["SD"][col_label] =  math.sqrt(col_dev / (col_n - 1))
            except ZeroDivisionError:
                # for a 2 x 2 matrix, col_n -1 == 0, so sample SD is undefined
                self["SD"][col_label] = 0.0

        overall_n = len(self.labels) * col_n
        self["SD"]["overall"] = math.sqrt(overall_dev / (overall_n - 1)) 
        
        
    def write(self, formatter=None, **kwargs):
        if not formatter:
            formatter = FormatAnalysesMatrix(self)
            
        formatter.write(**kwargs)
        

        
class FormatAnalysesMatrix(object):
    """
    Formats a matrix of analyses for printing
    """
    def __init__(self, analysis_matrix):
        self.matrix = analysis_matrix


    def write(self, out=sys.stdout, percent=False, header=None):
        if percent:
            factor = 100
            float_format = "%12.2f"
        else:
            factor = 1
            float_format = "%12.4f"
            
        col_width = 12
        no_of_cols = len(self.matrix.labels) + 2
        separator = no_of_cols * col_width * "-"

        if header:
            out.write(header + "\n\n")

        out.write(col_width * " ")

        for col_label in self.matrix.labels + ["overall"]:
            out.write("%11s:" % col_label)

        out.write("\n" + separator + "\n")

        for row_label in self.matrix.labels:

            out.write("%11s:" % row_label)

            for col_label in self.matrix.labels:
                if row_label != col_label:
                    out.write(float_format % (self.matrix[row_label][col_label] * factor))
                else:
                    out.write(col_width * " ")

            out.write("\n")

        out.write(separator + "\n")

        for row_label in ["mean", "SD"]:

            out.write("%11s:" % row_label)

            for col_label in self.matrix.labels:
                out.write(float_format % (self.matrix[row_label][col_label] * factor))

            out.write(float_format % (self.matrix[row_label]["overall"] * factor))

            out.write("\n")

        out.write("\n\n")

