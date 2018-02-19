#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Vincent CABELI
"""

import sys
import os
import numpy as np
from TSS import TSS
# -------------------
# useful function



#==============================================================================#

class Gene:

    def __init__(self, *args, **kwargs):
        """ Possible kwargs arguments: name, left, right, orientation,
        annotations_list
        """
        self.name = kwargs.get('name')
        self.left = kwargs.get('left')
        self.right = kwargs.get('right')
        self.strand = kwargs.get('orientation')
        if self.strand:
            self.start = self.left
            self.end = self.right
            self.orientation= 1
        else:
            self.start = self.right
            self.end = self.left
            self.orientation= -1

            annotations_general = kwargs.get('annotations_general')
            head=kwargs.get('head')
            if annotations_general:
                self.name = self.orientation= annotations_general[0]
                self.left = int(annotations_general[2])
                self.right = int(annotations_general[3])
                self.middle = (self.left+self.right)/2
                self.length = int(self.right-self.left)+1
                self.strand=annotations_general[1]
                if annotations_general[1]=='+':
                    self.strand= True
                    self.orientation= 1
                    self.start = self.left
                    self.end = self.right
                else:
                    self.strand=False
                    self.orientation = -1
                    self.start = self.right
                    self.end = self.left
                self.opt=dict(zip(head, annotations_general[4]))
        """
        # old version
        annotations_list = kwargs.get('annotations_list')
        if annotations_list:
            self.number = float(annotations_list[0])
            self.name = annotations_list[1]
            self.left = int(annotations_list[3])
            self.right = int(annotations_list[4])
            self.middle = (self.left+self.right)/2
            self.strand = annotations_list[2]
            self.length = int(annotations_list[5])
            self.orientation = annotations_list[6] == "1"
            self.leading = annotations_list[7]
            self.replichore = annotations_list[8]
            self.operon = annotations_list[11]
            self.symbol = annotations_list[12]
            self.gene_id = annotations_list[9]
            self.cog_id = annotations_list[13]
        """

        annotations_list_gff = kwargs.get('annotations_list_gff')
        if annotations_list_gff:
            self.left = int(annotations_list_gff[3])
            self.right = int(annotations_list_gff[4])
            self.middle = (self.left+self.right)/2
            self.length = int(self.right-self.left)+1
            self.source=annotations_list_gff[1]
            if annotations_list_gff[6]=='+':
                self.strand= True
                self.orientation= 1
            else:
                self.strand= False
                self.orientation =-1
            for k in annotations_list_gff[8]:
                if k == 'locus_tag':
                    self.gene_id = annotations_list_gff[8][k]
                if k == 'ID':
                    self.id = annotations_list_gff[8][k]
                if k == 'gene':
                    self.symbol = annotations_list_gff[8][k]
                if k == 'Parent':
                    self.replichore = annotations_list_gff[8][k]
                if k == 'Name':
                    self.name = annotations_list_gff[8][k]
        if self.strand:
            self.start = self.left
            self.end = self.right
        else:
            self.start = self.right
            self.end = self.left

    def add_expression_data(self, conditions, expression_values):
        """ Adds expression in the form of a dictionnary where the keys
        correspond to the different conditions. The conditions and expression
        values are passed as lists.
        """
        self.expression = dict(zip(conditions, expression_values))
        self.mean_expression = np.mean(self.expression.values())


    def add_single_expression(self, condition, expression_value):
        if not hasattr(self, 'expression'):
            self.expression = {}
        self.expression[condition] = expression_value

    def add_single_rpkm(self, condition, expression_value):
        if not hasattr(self, 'rpkm'):
            self.rpkm = {}
        self.rpkm[condition] = expression_value


    def set_mean_expression(self, expression_value=None):
        if expression_value:
            self.mean_expression = expression_value
        else:
            self.mean_expression = np.mean(self.expression.values())


    def set_model_parameters(self, k_on, p_off, condition):
        """ Sets the gene's k_on and p_off parameters. p_off is the probability
        that the polymerase that transcribed the previous gene does not
        transcribe this one as well (readthrough). k_on is the quantity of new
        polymerases binding to and transcribing this gene.
        """
        if not hasattr(self, 'model_parameters'):
            self.model_parameters = {}
        self.model_parameters[condition] = (k_on, p_off)


    def add_fc_data(self, conditions, fold_change_values):
        """ Adds fold change expression data in the form of a dictionnary in the
        same way as the expression data.
        """
        self.fold_change = dict(zip(conditions, fold_change_values))

    def __eq__(self, other):
        return (self.name == other.name) and \
               (self.left == other.left) and \
               (self.right == other.right) and \
               (self.orientation == other.orientation)

    def add_id_TSS(self, id_TSS):
        if not hasattr(self,'id_TSS'):
            self.id_TSS=[]
        if not (id_TSS in self.id_TSS):
            self.id_TSS.append(id_TSS)

    def add_fc(self,fc_value, condition, *args, **kwargs):
        if not hasattr(self,'all_fc'):
            self.all_fc={}
        if not hasattr(self,'all_pval'):
            self.all_pval={}
        self.all_fc[condition]=fc_value
        p_value = kwargs.get('p_value')
        if p_value:
            self.all_pval[condition]=p_value

    def add_left_neighbour(self, neighbour):
        self.left_neighbour = neighbour

    def add_right_neighbour(self, neighbour):
        self.right_neighbour = neighbour

    def add_id_operon(self, operon):
        if not hasattr(self,'id_operon'):
            self.id_operon=[]
        if not(operon in self.id_operon):
            self.id_operon.append(operon)



    def add_list_expression(self):
        self.list_expression=[]
        if hasattr(self,'expression'):
            for i in self.expression:
                self.list_expression.append(self.expression[i])
