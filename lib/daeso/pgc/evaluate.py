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
Evaluation of alignment by comparing a corpus containing predicted alignments with
a reference corpus containing true alignments.


EVALUATION OF ALIGNMENT

An (unlabeled) alignment consists of a set of node pairs <n,m> where n is a
node of the source tree and m is a noe of the target tree. Given a set of true
and predicted alignments

    A_true = { <n1,m1>, <n2,m2>, ... }
    A_pred = { <n1',m1'>, <n2',m2'>, ... }

the recall, precision and F-score are defined as 


              | intersection(A_true, A_pred) |
    recall = ----------------------------------
                        | A_true |                


                        
                 | intersection(A_true, A_pred) |
    precision = ----------------------------------
                         | A_pred |   


              2
         (beta  + 1) * prec * rec
    F =  ------------------------
                2 
       	    beta  * prec + rec
            
            
where 0 <= beta <= 1.


As a shorthand, the following three counts are used:

    True ;= | A_true |
    Pred := | A_pred |
    Common := | intersection(A_true, A_pred) |
    
hence recall=Common/True and precision=Common/Pred. 
    
Whenever True or Pred is zero, the recall and precision respectively are
technically undefined. For convenience, however, the implementation returns
zero. The same goes for the F score when both precision and recall equals
zero.


EVALUATION OF LABELED ALIGNMENT

A labeled alignment consists of a set of tuples <n,m, l> where n is a node of
the source tree, m is a node of the target tree, and l is the relation label.
Given a set of true and predicted alignments

    A_true = { <n1,m1, l1>, <n2,m2,l2>, ... }
    A_pred = { <n1',m1',l1'>, <n2',m2',l2'>, ... }

the micro recall, precision and F-score are defined the same as above.

The score on a particular label is calculated by first restrictng A_true and
A_pred to only those tuples with that label, disregarding all tuples with
other labels, and then again calculating precision, recall and F score in the
above way.

The overall macro recall, precision and F-score are calculating by taking the
average over the scores on each relation label. In contrast to the micro
scores, the macro scores ignores the fact that the distribution of the labels
may be skewed.

MULTIPLE CORPORA

For multiple corpora, first counts and scores are calculated for each separate
corpus, and then average scores are calculated. The macro avarage is the
avarage over all separate score. The micro avarage is calculated by first
summing the counts of True, Pred and Common respectively, and then computing
precision, recall and F-score over these summed counts.
"""

__authors__ = "Erwin Marsi <e.marsi@gmail.com>"

from sys import stdout
from math import sqrt

from daeso.utils.report import header

# TODO
# - confusion matrix / list?
# - option to restrict eval to word/terminal alignment
# - factorisation & clean up
# - on hindsight, much of the table stuff should be done in Numpy... 

__all__ = [ "AlignEval" ]


class AlignEval(dict):   
    """
    Alignment Evaluation
    
    This class can be used to evaluate labeled alignments by a pairwise
    comparison of corpora containing predicted alignments with gold standard
    corpora containing true alignments.
    
    The printed output contains evaluation from three different perspectives:
    1. alignment proper, irrespective of the relation labels
    2. alignment per relation
    3. alignment over all relations
    
    The alignment quality is measured in terms of precision, recall and F score.
    
    The default way to use AlignEval os as follows:
    
    >>> from daeso.pgc.eval import AlignEval
    >>> align_eval = AlignEval()
    >>> align_eval.add(true_corpus_1, pred_corpus_1, "name1")
    >>> align_eval.add(true_corpus_2, pred_corpus_2, "name2")
    >>> ...
    >>> align_eval.run_eval()
    >>> align_eval.write()
    
    
    AlignEval is basically a dict object where the keys are the relations and
    the values are AlignCountsTable instances, which represent the counts and
    evaluation measures for all alignments with this relation. In addition,
    AlignEval contains the overall count and measure statistics. 

    To access the overall count statistics use
    
        inst.count_stats[count][stat]
    
    where count is any of "true", "pred", "common"
    and stat is any of "mean".
    
    To access the overall measure statistics use 
        
        inst.measure_stats[measure][method][stat]
        
    where measure is any of "prec", "rec", "f",
    method is any of "macro", "micro",
    and stat is any of "mean".
    
    To access counts and measures per relation use 
    
        inst[relation]
    
    where relation is any of "equals", "restates", "specifies", "generalizes",
    "intersects", or AlignEval.anyrel. This returns the AlignCountsTable
    instance for this relation. As an example, to retrieve the micro mean F
    score on the relation "restates", use
    
        inst["restates"].measure_stats["f"]["micro"]["mean"]
    
    See the doc for AlignCountsTable for full information.
    
    """
    count_stat_keys = "sum" # var and sd over relations doesn't make sense
    measure_stat_keys = "mean", # var and sd over relations might make sense
    measure_stat_methods = "macro", "micro"
    relations = "equals", "restates", "specifies", "generalizes", "intersects"
    any_rel = "__any_rel__"  # special relation to store counts irrespective of relation  
    
    def __init__(self, relations=relations):
        dict.__init__(self)
        self.relations = relations
        self.names = []
        
        self[AlignEval.any_rel] = AlignCountsTable()
        
        for rel in relations:
            self[rel] = AlignCountsTable()
            
        self.count_stats = {}
        
        for k in AlignCounts.count_keys:
            self.count_stats[k] = {}
            
        self.measure_stats = {}
        
        for k in AlignCounts.measure_keys:
            self.measure_stats[k] = {}
            for m in self.measure_stat_methods:
                self.measure_stats[k][m] = {}


    def add(self, true_pgc, pred_pgc, name=None):
        """
        Add alignment counts from true and predicted parallel graph corpus,
        optionally tagging it with a (file)name
        """
        # this is not sufficient (e.g. graphs or relations can differ), 
        # but at least it prevents evident mistakes 
        assert len(true_pgc) == len(pred_pgc)
        
        if not name:
            name = "part%d" % (len(self[AlignEval.any_rel]) + 1)
            
        self.names.append(name)
        
        # Append a new AlignCounts instance to the AlignCountTable for each
        # relation, in other words, a new row to the table
        for table in self.values():
            table.append(AlignCounts())            
        
        for true_graph_pair, pred_graph_pair in zip(true_pgc, pred_pgc):
            # count true and common alignments per relation
            true_align_count = 0
            
            for nodes, true_rel in true_graph_pair.alignments_iter():
                true_align_count += 1
                self[true_rel][-1].counts["true"] += 1
                
                pred_rel = pred_graph_pair.get_align(nodes) 

                if pred_rel:
                    # same alignment, possibly different label
                    self[AlignEval.any_rel][-1].counts["common"] += 1

                    if pred_rel == true_rel:
                        # same alignment and same label
                        self[true_rel][-1].counts["common"] += 1

            # count overall true alignments
            self[AlignEval.any_rel][-1].counts["true"] += true_align_count

            # count predicted alignments per relation
            pred_align_count = 0
            
            for nodes, pred_rel in pred_graph_pair.alignments_iter():
                pred_align_count += 1
                self[pred_rel][-1].counts["pred"] += 1

            # count overall predicted alignments
            self[AlignEval.any_rel][-1].counts["pred"] += pred_align_count


    def run_eval(self):
        """
	calculate evaluation measures and statistics
	"""
        self._eval_align_count_tables()
        self._calc_count_sums()
        self._calc_measure_macro_mean()
        self._calc_measure_micro_mean()

        
    def _calc_count_sums(self):
        for k in AlignCounts.count_keys:
            self.count_stats[k]["sum"] = sum([ self[rel].count_stats[k]["sum"]
                                               for rel in self.relations ])
        
        
    def _eval_align_count_tables(self):
        for table in self.values():
            table.run_eval()


    def _calc_measure_macro_mean(self):
        n = len(self.relations)
        
        for m in AlignCounts.measure_keys:
            # I take the relation's micro mean here, because otherwise
            # the overall micro and macro mean are likely to be more different 
            sum_ = sum([ self[rel].measure_stats[m]["micro"]["mean"]
                         for rel, align_counts in zip(self.relations, self) ])
            
            self.measure_stats[m]["macro"]["mean"] = sum_ / n
            
        
    def _calc_measure_micro_mean(self):
        align_counts_sum = AlignCounts()
        
        for c in AlignCounts.count_keys:
            align_counts_sum.counts[c] = self.count_stats[c]["sum"]
        
        align_counts_sum.run_eval()
        
        for m in AlignCounts.measure_keys:
            self.measure_stats[m]["micro"]["mean"] = align_counts_sum.measures[m]
    
            
    def write(self, out=stdout):
        """
        write full evaluation 
	"""
        if isinstance(out, basestring):
            out = open(out, "w")
            
        self.write_alignment_only(out)
        self.write_alignment_per_relation(out)
        self.write_alignment_overall(out)
        
        
    def write_alignment_only(self, out=stdout):
        """
        write evaluation of alignment only, irrespective of relation labels
        """
        header("Alignment only (regardlless of relation)", out)
        self[AlignEval.any_rel].write(self.names, out=out)
        
        
    def write_alignment_per_relation(self, out=stdout):
        """
        write evaluation of alignment for each relation separtately
        """
        header("Alignment per relation", out)
        
        for rel in self.relations:
            self[rel].write(self.names, out=out, heading=rel.upper())

            
    def write_alignment_overall(self, out=stdout, percent=True):  
        """
        write evaluation summary of alignment over all relations
        """
        width = 14
        separator = 4 * width * "-" + "\n"
        
        header("Alignment over all relations", out)
        
        # write counts
        
        out.write("Relation:".ljust(width))
        
        for c in AlignCounts.count_keys:
            c = c.capitalize() + ":"
            out.write(c.rjust(width))
            
        out.write('\n' + separator)
        
        for rel, align_counts in zip(self.relations, self):
            out.write(rel.ljust(width))
            
            for c in AlignCounts.count_keys:
                s = str(self[rel].count_stats[c]["sum"])
                out.write(s.rjust(width))            
            out.write('\n')

        out.write(separator)
        
        out.write("Sum:".ljust(width))
        
        for k in AlignCounts.count_keys:
            s = str(self.count_stats[k]["sum"])
            out.write(s.rjust(width))           
            
        out.write('\n\n\n')
        
        # write measures
        
        out.write("Relation:".ljust(width))
        
        for c in AlignCounts.measure_keys:
            c = c.capitalize() + ":"
            out.write(c.rjust(width))
            
        out.write('\n' + separator)
        
        for rel, align_counts in zip(self.relations, self):
            out.write(rel.ljust(width))
            
            for m in AlignCounts.measure_keys:
                # repport the relation's micro mean here
                value = self[rel].measure_stats[m]["micro"]["mean"]
                if percent: value *= 100
                s = "%.2f" % value
                out.write(s.rjust(width))            
            out.write('\n')

        out.write(separator)

        for method in self.measure_stat_methods:
            for stat in self.measure_stat_keys:
                s = method.capitalize()+ " " + stat.capitalize() + ":"
                out.write(s.ljust(width))
                
                for m in AlignCounts.measure_keys:
                    value = self.measure_stats[m][method][stat]
                    if percent: value *= 100
                    s = "%.2f" % value
                    out.write(s.rjust(width))           
                out.write('\n')

        out.write('\n\n')
            
            

##class WordAlignEval(AlignEval):
    ##"""
    ##Word Alignment Evaluation
    
    ##A variant of AlignEval that restricts the evaluation to those true and
    ##predicted alignments where at least one the two nodes involved is a
    ##word/terminal.
    ##"""
            
    ##def get_alignments(self, graph_pair):
        ##"""
        ##restrict alignments to those alignments where at least one the two nodes
        ##involved is a word/terminal
        ##"""
        ### cheating a little, because this returns a dict rather than a GraphPair
        ##align = {}
        ##from_graph, to_graph = graph_pair.get_graphs()
        
        ##for node_ids, relation  in graph_pair.items():
            ##from_node, to_node = graph_pair.get_nodes(node_ids)
            
            ##if from_graph.is_terminal(from_node) or to_graph.is_terminal(to_node):
                ##align[node_ids] = relation
                
        ##return align
        
    
        
class AlignCountsTable(list):
    """
    Alignment Counts Table
    
    This class represents the counts and measures for a particular relation
    over all corpora. It is basically a list of AlignCount instances.

    To access the overall count statistics use
    
        inst.count_stats[count][stat]
    
    where count is any of "true", "pred", "common"
    and stat is any of "mean", "var", "sd".
    
    To access the overall measure statistics use 
        
        inst.measure_stats[measure][method][stat]
        
    where measure is any of "prec", "rec", "f",
    method is any of "macro", "micro",
    and stat is any of "mean", "var", "sd".
    
    To access the counts and measures for the n-th pair of corpora use
    
        inst[n]
        
    which returns an AlignCounts instance. See the doc for AlignCounts for
    further information.
    
    """
    count_stat_keys = "sum", "mean", "var", "sd"
    measure_stat_keys = "mean", "var", "sd",
    measure_stat_methods = "macro", "micro"
    
    def __init__(self):
        list.__init__(self)
        
        self.count_stats = {}

        for k in AlignCounts.count_keys:
            self.count_stats[k] = {}
            
        self.measure_stats = {}
            
        for k in AlignCounts.measure_keys:
            self.measure_stats[k] = {}
            for m in self.measure_stat_methods:
                self.measure_stats[k][m] = {}
        
                
    def run_eval(self):
        self._eval_align_counts()
        self._eval_count_stats()
        self._eval_measure_stats()
        
    
    def _eval_align_counts(self):
        for align_counts in self:
            align_counts.run_eval()
            
            
    def _eval_count_stats(self):
        self._calc_counts_sum_and_mean()
        self._calc_counts_var_and_sd()
        
    
    def _calc_counts_sum_and_mean(self):
        n = float(len(self))
        
        for c in AlignCounts.count_keys:
            self.count_stats[c]["sum"] = sum([ align_counts.counts[c]
                                               for align_counts in self ])
        
            self.count_stats[c]["mean"] = self.count_stats[c]["sum"] / n
            
            
    def _calc_counts_var_and_sd(self):
        n = float(len(self))
        
        for c in AlignCounts.count_keys:
            mean = self.count_stats[c]["mean"] 
            sum_of_diff = 0.0
            
            for align_counts in self:
                value = align_counts.counts[c]
                sum_of_diff += (value - mean) ** 2
                
            try:
                self.count_stats[c]["var"] = var = sum_of_diff / (n - 1)
            except ZeroDivisionError:
                # for n = 1, variance is undefined
                self.count_stats[c]["var"] = var = 0.0
            
            self.count_stats[c]["sd"] = sqrt(var)
            
            
    def _eval_measure_stats(self):
        self._calc_measure_macro_mean()
        self._calc_measure_macro_var_and_sd()
        self._calc_measure_micro_mean()
        self._calc_measure_micro_var_and_sd()
        
        
    def _calc_measure_macro_mean(self):
        n = float(len(self))
        
        for m in AlignCounts.measure_keys:
            sum_ = sum([ align_counts.measures[m]
                         for align_counts in self ])
        
            self.measure_stats[m]["macro"]["mean"] = sum_ / n
            
            
    def _calc_measure_macro_var_and_sd(self):
        n = float(len(self))
        
        for m in AlignCounts.measure_keys:
            mean = self.measure_stats[m]["macro"]["mean"] 
            sum_of_diff = 0.0
            
            for align_counts in self:
                value = align_counts.measures[m]
                sum_of_diff += (value - mean) ** 2
                
            try:
                self.measure_stats[m]["macro"]["var"] = var = sum_of_diff / (n - 1)
            except ZeroDivisionError:
                # for n = 1, variance is undefined
                self.measure_stats[m]["macro"]["var"] = var = 0.0
            
            self.measure_stats[m]["macro"]["sd"] = sqrt(var)
        
            
    def _calc_measure_micro_mean(self):
        align_counts_sum = AlignCounts()
        
        for c in AlignCounts.count_keys:
            align_counts_sum.counts[c] = self.count_stats[c]["sum"]
            
        align_counts_sum.run_eval()
        
        for m in AlignCounts.measure_keys:
            self.measure_stats[m]["micro"]["mean"] = align_counts_sum.measures[m]
            
            
    def _calc_measure_micro_var_and_sd(self):
        n = float(len(self))
        
        for m in AlignCounts.measure_keys:
            mean = self.measure_stats[m]["micro"]["mean"] 
            sum_of_diff = 0.0
            
            for align_counts in self:
                value = align_counts.measures[m]
                sum_of_diff += (value - mean) ** 2
                
            try:
                self.measure_stats[m]["micro"]["var"] = var = sum_of_diff / (n - 1)
            except ZeroDivisionError:
                # for n = 1, variance is undefined
                self.measure_stats[m]["micro"]["var"] = var = 0.0
            
            self.measure_stats[m]["micro"]["sd"] = sqrt(var)
            
            
    def write(self, names, out=stdout, percent=True, heading=""):
        width = 14
        namespace = max([len(n) for n in names]) + 4
        namespace = max(namespace, width)
        
        cols = len(AlignCounts.count_keys)
        separator = (namespace + cols * width) * '-' + '\n'
        
        if heading: out.write(heading + "\n\n")
        
        # write count stats
        
        out.write("Name:".ljust(namespace))
        
        for c in AlignCounts.count_keys:
            c = c.capitalize() + ":"
            out.write(c.rjust(width))
            
        out.write('\n' + separator)
        
        for name, align_counts in zip(names, self):
            out.write(str(name).ljust(namespace))
            
            for c in AlignCounts.count_keys:
                s = str(align_counts.counts[c])
                out.write(s.rjust(width))            
            out.write('\n')

        out.write(separator)
        
        for stat in self.count_stat_keys:
            name = stat.capitalize() + ":"
            out.write(name.ljust(namespace))
            
            for c in AlignCounts.count_keys:
                if stat == "sum":
                    s = str(self.count_stats[c][stat])
                else:
                    s = "%.2f" % self.count_stats[c][stat]
                out.write(s.rjust(width))           
            out.write('\n')

        out.write('\n\n')
        
        # write measure stats
                
        out.write("Name:".ljust(namespace))
        
        for m in AlignCounts.measure_keys:
            m = m.capitalize() + ":"
            out.write(m.rjust(width))
            
        out.write('\n' + separator)
        
        for name, align_counts in zip(names, self):
            out.write(str(name).ljust(namespace))
            
            for m in AlignCounts.measure_keys:
                value = align_counts.measures[m]
                if percent: value *= 100
                s = "%.2f" % value
                out.write(s.rjust(width))           
            out.write('\n')
                
        out.write(separator)
        
        for method in self.measure_stat_methods:
            for stat in self.measure_stat_keys:
                name = method.capitalize()+ " " + stat.capitalize() + ":"
                out.write(name.ljust(namespace))
                
                for m in AlignCounts.measure_keys:
                    value = self.measure_stats[m][method][stat]
                    if percent: value *= 100
                    s = "%.2f" % value
                    out.write(s.rjust(width))           
                out.write('\n')
                
        out.write('\n\n')
        
        


class AlignCounts(object):
    """
    A class for counting true, predicted and common alignments ,and for 
    evaluating alignment counts in terms of precison, recall and F-score.
    """
    count_keys = "true", "pred", "common"
    measure_keys = "prec", "rec", "f"
    beta = 1           

    def __init__(self):
        self.counts = dict.fromkeys(self.count_keys, 0)
        self.measures = {}

        
    def run_eval(self, beta=beta):
        self._calc_precision()
        self._calc_recall()
        self._calc_f_score(beta)

        
    def _calc_precision(self):
        """
	calculates precision on alignment defined as the number
	of common alignments divided by the number of predicted alignments 
	"""
        try:
            self.measures["prec"] = ( self.counts["common"] / 
                                      float(self.counts["pred"]) )
        except ZeroDivisionError:
            # no predicted alignments
            # for convenience return zero rather than None (nan)
            self.measures["prec"] = 0
             

    def _calc_recall(self):
        """
	calculates precision on alignment defined as the number
	of common alignments divided by the number of true alignments 
	"""
        try:
            self.measures["rec"] = ( self.counts["common"] / 
                                     float(self.counts["true"]) )
        except ZeroDivisionError:
            # no true alignments
            # for convenience return zero rather than None (nan)
            self.measures["rec"] = 0


    def _calc_f_score(self, beta=beta):
        """
	calculates F-score on alignment defined as
        
                   2
              (beta  + 1) * prec * rec
         F =  ------------------------
                     2 
		 beta  * prec + rec
	"""
        assert 0 <= beta <= 1
        
        try:
            self.measures["f"] = ( ( (beta ** 2 + 1) * 
                                     self.measures["prec"] * 
                                     self.measures["rec"] ) / 
                                   ( (beta ** 2) * 
                                     self.measures["prec"] + 
                                     self.measures["rec"] ) )
        except ZeroDivisionError:
            # if either precision or recall is zero, F is undefined
            # for convenience return zero rather than None (nan)
            self.measures["f"] = 0
            
            
                
                


