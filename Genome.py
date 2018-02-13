#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import numpy as np
import pandas as pd
import inspect as inspect
import math
import matplotlib.pyplot as plt
import operator
from useful_function import *
from itertools import groupby
from globvar import *
from Gene import Gene
from TSS import TSS
from TU import TU
from Operon import Operon
from Terminator import Terminator
from domain_phuc import Domain



#==============================================================================#

# -------------------
# useful function


def annotations_parser(annotations_filename, tag_column=1):
    """ Returns a dictionary of Gene objects which has the shape
    {gene_tag_name:gene_object}, where the tag name column can be specified.
    """
    genes_dict = {}
    with open(annotations_filename, 'r') as f:
        header = next(f)
        for line in f:
            line = line.strip('\n')
            line = line.split(',')
            try:
                if (line[tag_column] in genes_dict):
                    print("Warning! Overwriting value for gene " + \
                         line[tag_column])
                # if key already exists this will overwrite the value
                genes_dict[line[tag_column]] = Gene(annotations_list=line)
            except (IndexError, ValueError):
                print("Annotations : could not read line " + ','.join(line))
    return genes_dict

def annotations_parser_general_old(annotations_filename,separator,tag_column,strand_column,left_column,         right_column,start_line):
    genes_dict = {}
    with open(annotations_filename, 'r') as f:
        i=1
        j=0
        while i < start_line:
            header=next(f)
            i+=1
        for line in f:
            list=[]
            line=line.strip()
            if      separator == '\\t':
                line=line.split('\t')
            else:
                line=line.split(separator)
            list.append(line[tag_column])
            if line[strand_column]=="complement":
                list.append('-')
            elif line[strand_column]=="forward":
                list.append('+')
            elif line[strand_column]== "1":
                list.append('+')
            elif line[strand_column]== "-1":
                list.append('-')
            else:
                list.append(line[strand_column])
            list.append(line[left_column])
            list.append(line[right_column])
            if line[tag_column] in genes_dict:
                print("Warning! Overwriting value for gene ")
                print(line[tag_column])
            genes_dict[line[tag_column]]=Gene(annotations_general=list)

    return genes_dict


def annotations_parser_general(annotations_filename,separator,tag_column,strand_column,left_column,right_column,start_line):
    genes_dict = {}
    with open(annotations_filename, 'r') as f:
        i=1
        j=0
        head=next(f)
        headl=head.strip()
        if separator == '\\t':
            headl=headl.split('\t')
        else:
            headl=headl.split(separator)
        i=2
        while i < start_line:
            header=next(f)
            i+=1
        for line in f:
            list=[]
            line=line.strip()
            if      separator == '\\t':
                line=line.split('\t')
            else:
                line=line.split(separator)
            list.append(line[tag_column])
            if line[strand_column]=="complement":
                list.append('-')
            elif line[strand_column]=="forward":
                list.append('+')
            elif line[strand_column]== "1":
                list.append('+')
            elif line[strand_column]== "-1":
                list.append('-')
            else:
                list.append(line[strand_column])
            list.append(line[left_column])
            list.append(line[right_column])
            list.append(line)
            if line[tag_column] in genes_dict:
                print("Warning! Overwriting value for gene ")
                print(line[tag_column])
            genes_dict[line[tag_column]]=Gene(annotations_general=list, head=headl)

    return genes_dict



def annotations_parser_gff(annotations_filename):
    genes_dict = {}
    under_dict={}
    my_file = open(annotations_filename, "r")
    for line in my_file.readlines():
        if line[0]!= '#':
            if line != '\n':
                line=line.split('\t')
                underline=line[8]
                underline=underline.split(';')
                for x in underline:
                    x=x.strip()
                    x=x.split('=')
                    under_dict[x[0]]=x[1]
                line[8]=under_dict
                under_dict={}
                try:
                    if('locus_tag' in line[8]):
                        if(line[8]['locus_tag'] in genes_dict):
                            print("Warning! Overwriting value for gene ")
                            print(line[8]['locus_tag'])
                            if('gene_biotype' in line[8]):
                                print(line[8]['gene_biotype'])
                        genes_dict[line[8]['locus_tag']]= Gene(annotations_list_gff=line)
                except (IndexError, ValueError):
                    print("Annotations : could not read line ")
    return genes_dict

def add_operon(dict_genes,file):
    dict_operon={}
    under_dict={}
    i = 1
    my_file = open(file, "r")
    for line in my_file.readlines():
        if line[0]!= '#':
            line=line.strip()
            line=line.split('\t')
            dict_operon[i]=Operon(int(line[3]),int(line[4]),line[6])
            underline=line[8]
            underline=underline.split(';')
            for x in underline:
                x=x.split('=')
                under_dict[x[0]]=x[1]
            for x in under_dict:
                if 'Genes' in x:
                    dict_operon[i].add_genes(under_dict[x])
                if 'ID' in x:
                    dict_operon[i].add_ID(under_dict[x])
            for x in dict_operon[i].genes:
                if x in list(dict_genes.keys()):
                    dict_genes[x].add_id_operon(i)
                else:
                    print(x+" not in annotation")
            i+=1
            under_dict={}
    return dict_operon

def add_terminator(file):
    dict_terminator={}
    under_dict={}
    my_file = open(file, "r")
    for line in my_file.readlines():
        if line[0]!= '#':
            line=line.strip()
            line=line.split('\t')
            underline=line[8]
            underline=underline.split(';')
            for x in underline:
                x=x.split('=')
                under_dict[x[0]]=x[1]
            for x in under_dict:
                if 'ID' in x:
                    dict_terminator[int(under_dict[x])]=Terminator(int(line[3]),int(line[4]),line[6], int(under_dict[x]), under_dict)
    return dict_terminator


def feature_table_parser(table_filename):
    """ Returns a dictionary of Gene objects which has the shape
    {gene_tag_name:gene_object}, where the tag name column can be specified.
    """
    genes_dict = {}
    with open(table_filename, 'r') as f:
        next(f)
        for line in f:
            line = line.strip('\n')
            line = line.split('\t')
            if len(line) != 3:
                continue
            elif line[2] == 'gene':
                start = int(line[0].strip('<').strip('>'))
                end = int(line[1].strip('<').strip('>'))
                orientation = (start < end)
                while 'locus_tag' not in line :
                    line = next(f)
                    line = line.strip('\n')
                    line = line.split('\t')
                if 'gene' in line:
                    continue
                if line[-1] in genes_dict:
                    print("Warning! Overwriting value for gene " + \
                         line[-1])
                # if key already exists this will overwrite the value
                genes_dict[line[-1]] = Gene(name = line[-1],
                                           left = min(start,end),
                                           right = max(start, end),
                                           orientation = orientation)
    return genes_dict


def add_expression_to_genes(genes_dict, expression_filename, tag_col, first_expression_col, is_log):
    """ Adds expression data to Gene objects by parsing a file with as many
    columns as there are different conditions in the experiment, plus one for
    the gene names (first column).
    """
    with open(expression_filename, 'r') as f:
        header=next(f)
        header=header.strip()
        header=header.split('\t')
        header=header[first_expression_col:]
        for line in f:
            line=line.strip()
            line = line.split('\t')
            try:
                if is_log == 'no':
                    genes_dict[line[tag_col]].add_expression_data(header,[math.log(float(i),2) for i in line[first_expression_col:]])
                else:
                    genes_dict[line[tag_col]].add_expression_data(header,[float(i) for i in line[first_expression_col:]])
            except KeyError:
                if line[tag_col] == 'none':
                    print("expressions without locus tag")
                else:
                    print(line[tag_col] + " this locus not in annotation")
        return genes_dict


def add_single_expression_to_genes(genes_dict, expression_filename):
    """ Adds expression data to Gene objects by parsing a file with as many
    columns as there are different conditions in the experiment, plus one for
    the gene names (first column).
    """
    condition = expression_filename[expression_filename.rfind('/')+1:
                                    expression_filename.rfind('/')+3]
    with open(expression_filename, 'r') as f:
        header = next(f)
        header = header.strip('\n').split(',')
        header = header[1:]
        for line in f:
            line = line.strip('\n')
            line = line.split(',')
            try:
                genes_dict[line[0]].add_single_expression(
                    #log2(x+1)
                    condition, np.log2(float(line[1])+1))
            except KeyError:
                print("Expressions : Could not find gene " + line[0])
                #genes_dict[line[0]] = Gene(name=line[0], left=int(line[2]),
                #                          right=int(line[3]),
                #                          orientation=(line[4]=='+'))
                #genes_dict[line[0]].add_single_expression(
                #    expression_filename[i:i+3], float(line[1]))
    return genes_dict



def add_single_rpkm_to_genes(genes_dict, expression_filename, condition, TSS_column, start_line, separator,tag_column):
    """ Adds rpkm data to Gene objects by parsing a file with two columns:
    gene name and value
    """
    with open(expression_filename, 'r') as f:
        i=1
        while i != start_line:
            header=next(f)
            i+=1
        for line in f:
            line = line.strip('\n')
            if separator == '\\t':
                line = line.split('\t')
            else:
                line=line.split(separator)
            try:
                genes_dict[line[tag_column]].add_single_rpkm(
                    #log2(x+1)
                    condition, float(line[TSS_column]))
            except:
                if line[tag_column] not in list(genes_dict.keys()):
                    # the rpkm value corresponds to an un-annoted gene
                    print("rpkm : gene " + line[tag_column] + " not in annotation")
                else:
                    # the rpkm value cannot be converted
                    genes_dict[line[tag_column]].add_single_rpkm(condition, float("NaN"))
    # look if some genes are not in rpkm file: add nan
    for g in list(genes_dict.keys()):
        if isinstance(genes_dict[g],Gene):
            if not hasattr(genes_dict[g], 'rpkm'):
                genes_dict[g].add_single_rpkm(condition, float("NaN"))
    return genes_dict


def set_mean_expression(genes_dict, expression_filename):
    with open(expression_filename, 'r') as f:
        header = next(f)
        header = header.strip('\n').split(',')
        header = header[1:]
        for line in f:
            line = line.strip('\n')
            line = line.split(',')
            try:
                genes_dict[line[0]].set_mean_expression(line[1])
            except KeyError:
                print("Expressions : Could not find gene " + line[0])
    return genes_dict



def filter_TSS_old(xxx_todo_changeme,filt,win):
    (plus,minus) = xxx_todo_changeme
    isreal=np.any(plus[:,1:]>=filt,axis=1)
    plus=plus[isreal]
    ordre=np.argsort(plus[:,0])
    plus=plus[ordre]
    print(len(plus))
    # --- group together close ones
    finplus=[]
    if isinstance(win,int):
        for ip,p in enumerate(plus[:-1]):
            if (plus[ip+1,0]-p[0])<win:
                if np.mean(p[1:])<np.mean(plus[ip+1,1:]):
                    # replace position of TSS to group them
                    ind=plus[ip+1,0]
                else:
                    ind=plus[ip,0]
                finplus.append(ind)
        if plus[-1,0]!=ind:
            finplus.append(ind)
                #line=p+plus[ip+1]
                #line[0]=ind
                #finplus.append(line)
            #plus=np.array(finplus)
    else:
        finplus=plus[:,0]
    # ---------------------------------
    # -------- - strand
    isreal=np.any(minus[:,1:]>=filt,axis=1)
    minus=minus[isreal]
    ordre=np.argsort(minus[:,0])
    minus=minus[ordre]
    # ---- group together close ones
    finminus=[]
    if isinstance(win,int):
        for ip,p in enumerate(minus[:-1]):
            if (minus[ip+1,0]-p[0])<win:
                #print p
                if np.mean(p[1:])<np.mean(minus[ip+1,1:]):
                    # replace position of TSS to group them
                    ind=minus[ip+1,0]
                else:
                    ind=minus[ip,0]
                finminus.append(ind)
        if minus[-1,0]!=ind:
            finminus.append(ind)
                #line=p+plus[ip+1]
                #line[0]=ind
                #finplus.append(line)
                #plus=np.array(finplus)
    else:
        finminus=minus[:,0]
    return np.array(finplus),np.array(finminus)

def filter_TSS(xxx_todo_changeme1,filt,win):
    (plus,minus) = xxx_todo_changeme1
    isreal=np.any(plus[:,1:]>=filt,axis=1)
    plus=plus[isreal]
    ordre=np.argsort(plus[:,0])
    plus=plus[ordre]
    # --- group together close ones
    dftrue=plus[1:,0]-plus[:-1,0]<win
    a=[(k,len(list(g))) for k,g in groupby(dftrue)]
    # ind is the first index
    ind=0
    if a[0][0]:
        pluslist=[]
    else:
        pluslist=[plus[0,0]]
    for k,l in a:
        if k:
            # l separations are small
            # between index ind and index ind+l+1
            pluslist.append(plus[ind+np.argmax(np.mean(plus[ind:(ind+l+1),1:],axis=1)),0])
            ind+=l
        else:
            if l>1:
                pluslist+=plus[(ind+1):(ind+l),0].tolist()
            ind+=l
    # -------- minus strand$
    isreal=np.any(minus[:,1:]>=filt,axis=1)
    plus=minus[isreal]
    ordre=np.argsort(plus[:,0])
    plus=plus[ordre]
    # --- group together close ones
    dftrue=abs(plus[1:,0]-plus[:-1,0])<win
    a=[(k,len(list(g))) for k,g in groupby(dftrue)]
    # ind is the first index
    ind=0
    if a[0][0]:
        minuslist=[]
    else:
        minuslist=[plus[0,0]]
    for k,l in a:
        if k:
            # l separations are small
            # between index ind and index ind+l+1
            minuslist.append(plus[ind+np.argmax(np.mean(plus[ind:(ind+l+1),1:],axis=1)),0])
            ind+=l
        else:
            if l>1:
                minuslist+=plus[(ind+1):(ind+l),0].tolist()
            ind+=l
    return np.array(pluslist),np.array(minuslist)



def add_fc_to_genes(genes_dict, fc_filename):
    """ Adds expression data to Gene objects by parsing a file with as many
    columns as there are different conditions in the experiment, plus one for
    the gene names (first column).
    """
    with open(fc_filename, 'r') as f:
        header = next(f)
        header = header.strip('\n').split(',')
        header = header[1:]
        for line in f:
            line = line.strip('\n')
            line = line.split(',')
            try:
                genes_dict[line[0]].add_fc_data(header,
                    [float(i) for i in line[1:]])
            except KeyError:
                print("Fold change : Could not find gene " + line[0])
    return genes_dict

def add_single_fc_to_genes(genes_dict, filename, condition, tag_col, fc_col, separator, start_line, n, *args, **kwargs):
    p_val_col= kwargs.get('p_value')
    list=[]
    with open(filename, 'r') as f:
        i=1
        while i < start_line:
            header=next(f)
            i+=1
        for line in f:
            line = line.strip('\n')
            if separator == '\\t':
                line = line.split('\t')
            else:
                line=line.split(separator)
            try:
                if p_val_col:
                    if n==0:
                        genes_dict[line[tag_col]].add_fc(float(line[fc_col]),p_value=float(line[p_val_col]))
                    genes_dict[line[tag_col]].add_full_fc(float(line[fc_col]),condition)
                else:
                    if n ==0:
                        genes_dict[line[tag_col]].add_fc(float(line[fc_col]))
                    genes_dict[line[tag_col]].add_full_fc(float(line[fc_col]),condition)
                list.append(line[tag_col])
            except:
                if line[tag_col] not in list(genes_dict.keys()):
                    if line[tag_col] != '':
                        print(line[tag_col] + " not in annotation ")
                    else:
                        print("fc without locus")
    f.close()
    return list



def domain_parser(genes_dict, domain_filename):
    """ Creates a list of domains from a dictionnary of Gene objects and a text
    file.
    """
    domains = []
    with open(domain_filename, 'r') as f:
        for line in f:
            line = line.strip('\n')
            line = line.split(',')
            try:
                genes_list = [genes_dict[gene_name] for gene_name in line]
                domains.append(Domain(genes_list))
            except KeyError:
                print("Domains : Could not find gene " + line)
    return domains


def operon_domains(genes_dict):
    """ Creates a list of domains from the operon attribute of Gene objects.
    """
    domains = []
    genes = list(genes_dict.values())
    operons_list = [x.operon for x in list(genes_dict.values())]
    operons_list = np.unique(operons_list)
    for operon in operons_list:
        operon_genes = [genes[i] for i in np.where([x.operon==operon
            for x in genes])[0]]
        domains.append(Domain(operon_genes))
    return domains


def load_seq(filename):
    seq=str()
    my_file = open(filename, "r")
    for i in my_file.readlines():
        line=i.strip() #Removes \n
        if line != '':#Inspect if empty line
            if line[0]!=">":
                seq+=line
    my_file.close
    return seq


def load_single_TSS(genes_dict,TSS_dict, filename, TSS_column, start_line , separator, condition, strand, dic_plus, dic_minus, *args, **kwargs):
    sig = kwargs.get('sig')
    tag_column = kwargs.get('tag_column')
    if TSS_dict == {}:
        indice = 1
    else:
        indice = list(TSS_dict.keys())
        indice=len(indice) +1
    with open(filename, 'r') as f:
        i=1
        while i < start_line:
            header=next(f)
            i+=1
        for line in f:
            line = line.strip('\n')
            if separator == '\\t':
                line = line.split('\t')
            else:
                line=line.split(separator)
            try:
                if line[strand] == '+':
                    if not (line[TSS_column] in list(dic_plus.keys())):
                        TSS_dict[indice] = TSS(pos=int(line[TSS_column]),id=indice)
                        TSS_dict[indice].add_condition(condition)
                        TSS_dict[indice].add_strand(line[strand])
                        if sig:
                            if 'Sig' in line[sig]:
                                TSS_dict[indice].add_sig(line[int(sig)])
                        dic_plus[line[TSS_column]]=indice
                        indice +=1
                    else:
                        if not (condition in TSS_dict[dic_plus[line[TSS_column]]].condition):
                            TSS_dict[dic_plus[line[TSS_column]]].add_condition(condition)
                else:
                    if not (line[TSS_column] in list(dic_minus.keys())):
                        TSS_dict[indice] = TSS(pos=int(line[TSS_column]),id=indice)
                        TSS_dict[indice].add_condition(condition)
                        TSS_dict[indice].add_strand(line[strand])
                        if sig:
                            if 'Sig' in line[sig]:
                                TSS_dict[indice].add_sig(line[int(sig)])
                        dic_minus[line[TSS_column]]=indice
                        indice +=1
                    else:
                        if not (condition in TSS_dict[dic_minus[line[TSS_column]]].condition):
                            TSS_dict[dic_minus[line[TSS_column]]].add_condition(condition)
            except:
                pass
            try:
                if len(line[tag_column].split(',')):
                    for tag in line[tag_column].strip().replace(' ','').split(','):
                        try:
                            if line[strand] == '+':
                                if tag !='':
                                    TSS_dict[dic_plus[line[TSS_column]]].add_genes(tag,condition)
                                genes_dict[tag].add_id_TSS(dic_plus[line[TSS_column]])
                            else:
                                if tag !='':
                                    TSS_dict[dic_minus[line[TSS_column]]].add_genes(tag,condition)
                                genes_dict[tag].add_id_TSS(dic_minus[line[TSS_column]])

                        except:
                            if tag not in list(genes_dict.keys()):
                                if tag != '':
                                    print(tag + " not in annotations")
                else:
                    try:
                        if line[strand] == '+':
                            TSS_dict[dic_plus[line[TSS_column]]].add_genes(line[tag_column],condition)
                            genes_dict[tag_column].add_id_TSS(dic_plus[line[TSS_column]])
                        else:
                            TSS_dict[dic_plus[line[TSS_column]]].add_genes(line[tag_column],condition)
                            genes_dict[tag_column].add_id_TSS(dic_minus[line[TSS_column]])
                    except:
                        if line[tag_column] not in list(genes_dict.keys()):
                            if line[tag_column] != '':
                                print(line[tag_column] + " not in annotations")
            except:
                pass

    return genes_dict


def proportion_of(dict, list_genes, composition, seq_plus, seq_minus):
    dict_proportion={}
    dict_proportion['plus']=0.0
    dict_proportion['minus']=0.0
    activated=0
    repressed=0
    for i in list_genes:
        if dict[i].relax_log_fc > 0.0:
            if dict[i].strand:
                dict_proportion['plus']+= float(seq_plus[int(dict[i].left):int(dict[i].right)].count(composition))/float(dict[i].length)
            else:
                dict_proportion['plus']+= float(seq_minus[int(dict[i].left):int(dict[i].right)].count(composition))/float(dict[i].length)
            activated +=1
        if dict[i].relax_log_fc < 0.0:
            if dict[i].strand:
                dict_proportion['minus']+= float(seq_plus[int(dict[i].left):int(dict[i].right)].count(composition))/float(dict[i].length)
            else:
                dict_proportion['minus']+= float(seq_minus[int(dict[i].left):int(dict[i].right)].count(composition))/float(dict[i].length)
            repressed+=1
    if activated !=0:
        dict_proportion['plus']=dict_proportion['plus']/float(activated)
    else:
        dict_proportion['plus']=0.0
    if repressed !=0:
        dict_proportion['minus']=dict_proportion['minus']/float(repressed)
    else:
        dict_proportion['minus']=0.0
    return dict_proportion

def add_neighbour(dict_genes,list):
    for i in range(len(list)):
        if i != 0:
            dict_genes[list[i][1]].add_left_neighbour(list[i-1][1])
        if i != len(list)-1:
            dict_genes[list[i][1]].add_right_neighbour(list[i+1][1])
    return dict_genes

# ----------------------




class Genome:

    def __init__(self, *args, **kwargs):
        """ Possible kwargs arguments: name, seq, length,
        """
        self.name = kwargs.get('name')
        self.length = kwargs.get('length')
        self.genes=kwargs.get('genes')
        self.TSS_complete = {}
        self.TSS_plus={}
        self.TSS_minus={}

    def load_seq(self):
        self.seq=load_seq(basedir+"data/"+self.name+"/sequence.fasta")
        self.seq_reverse=''
        if(self.length):
            if(self.length != len(self.seq)):
                print("Warning not the same length, the new sequence will be removed")
                self.seq=''
        self.length=len(self.seq)
        l=self.seq[::-1]
        l=l.replace('A','t')
        l=l.replace('T','a')
        l=l.replace('C','g')
        l=l.replace('G','c')
        l=l.replace('a','A')
        l=l.replace('t','T')
        l=l.replace('c','C')
        l=l.replace('g','G')
        self.seq_reverse=l

    def give_proportion_of(self,*args, **kwargs):
        self.load_fc()
        self.load_seq()
        composition = kwargs.get('composition')
        if composition:
            values=[0.0,0.0]
            for i in composition:
                values[0]+=proportion_of(self.genes, self.list_genes_fc, i, self.seq, self.seq_reverse)['plus']
                values[1]+=proportion_of(self.genes, self.list_genes_fc, i, self.seq, self.seq_reverse)['minus']
            return values
        else:
            val_plus=[0.0,0.0,0.0,0.0]
            val_minus=[0.0,0.0,0.0,0.0]
            explode = (0,0,0,0)
            name = ['A','T','G','C']
            val_plus[0]+=proportion_of(self.genes, self.list_genes_fc, 'A', self.seq, self.seq_reverse)['plus']
            val_plus[1]+=proportion_of(self.genes, self.list_genes_fc, 'T', self.seq, self.seq_reverse)['plus']
            val_plus[2]+=proportion_of(self.genes, self.list_genes_fc, 'G', self.seq, self.seq_reverse)['plus']
            val_plus[3]+=proportion_of(self.genes, self.list_genes_fc, 'C', self.seq, self.seq_reverse)['plus']
            val_minus[0]+=proportion_of(self.genes, self.list_genes_fc, 'A', self.seq, self.seq_reverse)['minus']
            val_minus[1]+=proportion_of(self.genes, self.list_genes_fc, 'T', self.seq, self.seq_reverse)['minus']
            val_minus[2]+=proportion_of(self.genes, self.list_genes_fc, 'G', self.seq, self.seq_reverse)['minus']
            val_minus[3]+=proportion_of(self.genes, self.list_genes_fc, 'C', self.seq, self.seq_reverse)['minus']
            plt.figure(1)
            plt.subplot(211)
            plt.pie(val_plus, explode=explode, labels=name, autopct='%1.1f%%', startangle=90, shadow=True)
            plt.axis('equal')
            plt.subplot(212)
            plt.pie(val_minus, explode=explode, labels=name, autopct='%1.1f%%', startangle=90, shadow=True)
            plt.axis('equal')
            plt.show()



    def load_annotation(self):
        """ Laod a annotations file information where indice
                0 = file, 1 = separator ,2 = Locus column,3 = Strand column,
                4,5 Left Rigth column, 6 start line """
        if os.path.exists(basedir+"data/"+self.name+"/annotation/annotation.info"):
            with open(basedir+"data/"+self.name+"/annotation/annotation.info","r") as f:
                for line in f:
                    line=line.strip()
                    line=line.split('\t')
                    self.genes=annotations_parser_general(basedir+"data/"+self.name+'/annotation/'+line[0],line[1],int(line[2]),int(line[3]),int(line[4]),int(line[5]),int(line[6]))

                f.close()
            return True
        else:
            print(" Please load annotation of GFF file ")
            return False


    def load_annotation_gff(self):
        self.genes=annotations_parser_gff(basedir+"data/"+self.name+"/annotation/sequence.gff3")


    def load_neighbour(self):
        if not self.genes:
            if os.path.exists(basedir+"data/"+self.name+"/annotation/annotation.info"):
                self.load_annotation()
            else:
                self.load_annotation_gff()
        dict_plus={}
        dict_minus={}
        for i in self.genes:
            if self.genes[i].strand == True:
                dict_plus[int(self.genes[i].left)]=i
            else:
                dict_minus[int(self.genes[i].left)]=i
        l_plus=sorted(list(dict_plus.items()), key=operator.itemgetter(0))
        l_minus=sorted(list(dict_minus.items()), key=operator.itemgetter(0))
        self.genes=add_neighbour(self.genes,l_plus)
        self.genes=add_neighbour(self.genes,l_minus)


    def load_expression_level(self):
        """ Add expression level for all genes in dictionary """
        if not self.genes:
            if os.path.exists(basedir+"data/"+self.name+"/annotation/annotation.info"):
                self.load_annotation()
            else:
                self.load_annotation_gff()
        if os.path.exists(basedir+"data/"+self.name+"/expression/expression.info"):
            with open(basedir+"data/"+self.name+"/expression/expression.info","r") as f:
                for line in f:
                    line=line.strip()
                    line=line.split('\t')
                    self.genes=add_expression_to_genes(self.genes,basedir+"data/"+self.name+"/expression/"+line[0], int(line[1]), int(line[2]), line[3])
        else:
            print(" not found expression file information")

    def load_genes_positions(self):
        if not hasattr(self, 'genepos'):
            self.genepos = {}
        l=pd.read_csv(basedir+"data/"+self.name+"/genes_annotations.csv",header=0)
        gp=l[l.Strand=='forward']
        gp=gp[["Left.End.ASAP","Right.End.ASAP"]]
        gpq=np.array(gp)
        self.genepos["+"]=gpq[np.argsort(gpq[:,0])]
        gm=l[l.Strand=='complement']
        gm=gp[["Right.End.ASAP","Left.End.ASAP"]]
        gmq=np.array(gm)
        self.genepos["-"]=gmq[np.argsort(gmq[:,0])]


    def load_complete_TSS_list(self, *args, **kwargs):
        """ Load TSS list from file.
        Two filters can be applied:
        - filt: a minimum number of starts (default 20)
        - buffer: if two TSS are closer than this buffer size, we keep only the strongest one
        """
        filt=kwargs.get("filt")
        if not hasattr(self, 'TSS_complete'):
            self.TSS_complete = {}
        if not filt:
            filt=20
        self.TSS_complete["filter"]=filt
        plus=np.loadtxt(basedir+"data/"+self.name+"/TSS/TSS+.dat",skiprows=1)
        minus=np.loadtxt(basedir+"data/"+self.name+"/TSS/TSS-.dat",skiprows=1)
        print(plus)
        win=kwargs.get("buffer")
        self.TSS_complete["buffer"]=win
        pl,mi=filter_TSS((plus,minus),filt,win)
        self.TSS_complete["+"]=np.array(pl)
        self.TSS_complete["-"]=np.array(mi)

    def add_TSS_data(self,TSS_list,TSS_condition):
        """ Adds TSS from list generated from database as numpy array.
        TSS_condition describes the list, in the case where filters were applied etc."""
        if not hasattr(self, 'expression'):
            self.expression = {}
        self.TSS[TSS_condition]=np.array(TSS_list)

    def load_TSS(self, *args, **kwargs):
        """ Laod a TSS file information where indice 0 = condition, 1 = filename,
        2 = locus_tag, 3 = TSS_column, 4 = start_line, 5 = separator, 6 = strand column, 7 = Sig column
        if much other condition give it in the seconde line of file and change TSS column """
        if not (self.genes):
            if os.path.exists(basedir+"data/"+self.name+"/annotation/annotation.info"):
                self.load_annotation()
            else:
                self.load_annotation_gff()
        if os.path.exists(basedir+"data/"+self.name+"/TSS/TSS.info"):
            with open(basedir+"data/"+self.name+"/TSS/TSS.info","r") as f:
                for line in f:
                    line = line.strip('\n')
                    line = line.split('\t')
                    try:
                        test=int(line[2])# If no locus tag column in file information put None, test if locus tag column is number
                        try:
                            test=int(line[7])# Same test if no sig column
                            self.genes=load_single_TSS(self.genes, self.TSS_complete, basedir+"data/"+self.name+"/TSS/"+line[1], int(line[3]), int(line[4]), line[5], line[0], int(line[6]), self.TSS_plus, self.TSS_minus, tag_column = int(line[2]), sig=int(line[7]))
                        except:
                            self.genes=load_single_TSS(self.genes, self.TSS_complete, basedir+"data/"+self.name+"/TSS/"+line[1], int(line[3]), int(line[4]), line[5], line[0], int(line[6]), self.TSS_plus, self.TSS_minus,tag_column = int(line[2]))
                    except:
                        try:
                            test=int(line[7])
                            self.genes=load_single_TSS(self.genes, self.TSS_complete, basedir+"data/"+self.name+"/TSS/"+line[1], int(line[3]), int(line[4]), line[5], line[0], int(line[6]), self.TSS_plus, self.TSS_minus, sig=int(line[7]))
                        except:
                            self.genes=load_single_TSS(self.genes, self.TSS_complete, basedir+"data/"+self.name+"/TSS/"+line[1], int(line[3]), int(line[4]), line[5], line[0], int(line[6]), self.TSS_plus, self.TSS_minus)
        else:
            print(" no TSS.info maybe try use add_TSS_data()")


    def load_rpkm(self):
        """ Laod a RPKM file information where indice 0 = Condition
        1 = filename type, 2 = RPKM  column, 3 = Start line,
        4 = type of separator, 5=locus_column """
        if not (self.genes):
            if os.path.exists(basedir+"data/"+self.name+"/annotation/annotation.info"):
                self.load_annotation_gff()
            else:
                self.load_annotation()
        if os.path.exists(basedir+"data/"+self.name+"/rpkm/rpkm.info"):
            with open(basedir+"data/"+self.name+"/rpkm/rpkm.info","r") as f:
                for line in f:
                    line = line.strip('\n')
                    line = line.split('\t')
                    self.genes=add_single_rpkm_to_genes(self.genes, basedir+"data/"+self.name+"/rpkm/"+line[1],line[0],int(line[2]),int(line[3]),line[4],int(line[5]))
        else:
            print(" no rpkm file in this folder ")



    def load_depths(self):
        if not hasattr(self, 'cov_minus'):
            self.cov_minus = {}
        if not hasattr(self, 'cov_plus'):
            self.cov_plus = {}
        l=('')
        if os.path.exists(basedir+"data/"+self.name+"/rnaseq_depth/depth_numpy.info"):
            with open(basedir+"data/"+self.name+"/rnaseq_depth/depth_numpy.info","r") as f:
                for line in f:
                    line = line.strip('\n')
                    line = line.split('\t')
                    self.cov_minus[line[0]]=np.load(basedir+"data/"+self.name+"/rnaseq_depth/"+line[1])
                    self.cov_plus[line[0]]=np.load(basedir+"data/"+self.name+"/rnaseq_depth/"+line[2])
            with open(basedir+"data/"+self.name+"/rnaseq_depth/depth.info","r") as f:
                for line in f:
                    line = line.strip('\n')
                    line = line.split('\t')
                    l+=basedir+"data/"+self.name+"/rnaseq_depth/"+line[1]
                    l+=' '
                    l+=basedir+"data/"+self.name+"/rnaseq_depth/"+line[3]
                    l+=' '
                os.system("zip -r "+basedir+"data/"+self.name+"/rnaseq_depth/file.zip "+l)
                for i in l.split():
                    os.system("rm "+i)
        else:
            with open(basedir+"data/"+self.name+"/rnaseq_depth/depth.info","r") as f:
                fw=open(basedir+"data/"+self.name+"/rnaseq_depth/depth_numpy.info","w")
                for line in f:
                    line = line.strip('\n')
                    line = line.split('\t')
                    print("Loading depths corresponding to condition:", line)
                    a=np.loadtxt(basedir+"data/"+self.name+"/rnaseq_depth/"+line[1],usecols=[int(line[2])])
                    b=np.loadtxt(basedir+"data/"+self.name+"/rnaseq_depth/"+line[3],usecols=[int(line[4])])
                    np.save(basedir+"data/"+self.name+"/rnaseq_depth/"+line[1].split(".")[0]+".npy",a)
                    np.save(basedir+"data/"+self.name+"/rnaseq_depth/"+line[3].split(".")[0]+".npy",b)
                    fw.write(line[0]+'\t'+line[1].split(".")[0]+".npy"+'\t'+line[3].split(".")[0]+".npy"+'\n')
                    self.cov_minus[line[0]]=a
                    self.cov_plus[line[0]]=b
                    l+=basedir+"data/"+self.name+"/rnaseq_depth/"+line[1]
                    l+=' '
                    l+=basedir+"data/"+self.name+"/rnaseq_depth/"+line[3]
                    l+=' '
                os.system("zip -r "+basedir+"data/"+self.name+"/rnaseq_depth/file.zip "+l)
                for i in l.split():
                    os.system("rm "+i)
                fw.close()


    def load_genes_in_TU(self, TU):
        """ adds genes to TU accoding to annotation, ordered along orientation of the TU.
        Condition= gene entirely in TU
        """
        if not hasattr(self, 'genes'):
            print("loading annotation")
            load_annotation(self)
        glist=[]
        for g in list(self.genes.values()):
            if g.orientation==TU.orientation and g.left>=TU.left and g.right<=TU.right:
                glist.append(g.name)
        # sort list
        if len(glist)==0:
            TU.add_genes([])
        else:
            TU.add_genes(glist)
            lefts=[self.genes[x].left for x in glist]
            leftsort=sorted(lefts)
            if TU.orientation:
                TU.add_genes([glist[lefts.index(x)] for x in leftsort])
            else:
                TU.add_genes([glist[lefts.index(x)] for x in leftsort[::-1]])

    def add_single_TU(self, TU, index):
        """ adds TU to genome
        """
        if not hasattr(self, 'TU'):
            self.TU={}
        self.TU[index]=TU


    def load_genes_in_TUs(self):
        """ adds genes to all existing TUs.
        """
        if not hasattr(self, "TU"):
            print("no TU in genome")
        else:
            for TU in list(self.TU.values()):
                load_genes_in_TU(self, TU)

    def load_fc(self,*args, **kwargs):
        """ Fc info file, 0=condition 1=file_name, 2=tag_column, 3=fc_column
                4=type of separator, 5 = start line, 6 = p_value( if no write nothing),
                if other source give the line of the source in fc information file """
        if not self.genes:
            if os.path.exists(basedir+"data/"+self.name+"/annotation/annotation.info"):
                self.load_annotation()
            else:
                self.load_annotation_gff()
        n=0
        if os.path.exists(basedir+"data/"+self.name+"/fold_changes/fc.info"):
            with open(basedir+"data/"+self.name+"/fold_changes/fc.info","r") as f:
                for header in f:
                    header=header.strip()
                    header=header.split('\t')
                    try:
                        self.list_genes_fc=add_single_fc_to_genes(self.genes,basedir+"data/"+self.name+"/fold_changes/"+header[1],header[0],int(header[2]),int(header[3]),header[4],int(header[5]),n,p_value=int(header[6]))
                    except:
                        self.list_genes_fc=add_single_fc_to_genes(self.genes,basedir+"data/"+self.name+"/fold_changes/"+header[1],header[0], int(header[2]),int(header[3]),header[4],int(header[5]),n)
                    n+=1
            f.close()
        else:
            print(" No fold change file ")



    def compute_rpkm_from_coverage(self, before=100):
        """Adds rpkm values from coverage: along whole genes Before= number of bps to add before """
        if not self.genes:
            if os.path.exists(basedir+"data/"+self.name+"/annotation/annotation.info"):
                self.load_annotation()
            else:
                self.load_annotation_gff()
        try:
            for g in list(self.genes.keys()):
                if hasattr(self.genes[g],'orientation'):
                    if self.genes[g].orientation==1:
            # gene in + strand
                        for cond in list(self.cov_plus.keys()):
                            self.genes[g].add_single_rpkm(cond, np.mean(self.cov_plus[cond][(self.genes[g].left-100):self.genes[g].right]))
                    else:
            # gene in - strand
                        for cond in list(self.cov_minus.keys()):
                            self.genes[g].add_single_rpkm(cond, np.mean(self.cov_minus[cond][self.genes[g].left:(self.genes[g].right+100)]))
        except:
            print("You need to load coverage pls")


    def load_operon(self):
        if not self.genes:
            if os.path.exists(basedir+"data/"+self.name+"/annotation/annotation.info"):
                self.load_annotation()
            else:
                self.load_annotation_gff()
        self.operon_complete=add_operon(self.genes,basedir+"data/"+self.name+"/operon")


    def load_terminator(self):
        if not self.genes:
            if os.path.exists(basedir+"data/"+self.name+"/annotation/annotation.info"):
                self.load_annotation()
            else:
                self.load_annotation_gff()
        self.terminator_complete=add_terminator(basedir+"data/"+self.name+"/terminator")


    def get_depth_from_accession_files(self):
        if os.path.exists(basedir+"data/"+self.name+"/rnaseq_depth/description.info"):
            with open(basedir+"data/"+self.name+"/rnaseq_depth/description.info","r") as f:
                for line in f:
                    line = line.strip('\n')
                    line=line.split('\t')
                    if line[1] == '2':
                        list_depth=download_pair(basedir+"data/"+self.name+"/rnaseq_depth/"+line[0],self.name)
                    else:
                        list_depth=download_single(basedir+"data/"+self.name+"/rnaseq_depth/"+line[0],self.name)
                    create_depth_info(list_depth,self.name)
            f.close()
        else:
            print("Warning no description.info")


    def get_profile_from_matrix(self,factor_name):
        if not hasattr(self, 'profile'):
            self.profile={}
            self.load_seq()
        a = IUPAC.unambiguous_dna
        self.profile[factor_name]={}
        matrix=create_matrix_from_file(basedir+"data/pwm.txt",factor_name)
        #matrix=create_matrix_from_file_2(basedir+"data/pwm.txt",factor_name)
        seq=Seq(self.seq,a)
        for o in matrix.search_pwm(seq):
            self.profile[factor_name][o[0]]=o[1]

    def load_SIST(self, start, end,*args, **kwargs):
        if not hasattr(self, 'SIST_profile'):
            self.SIST_profile={}
            self.load_seq()
        option = kwargs.get('option')
        if option:
            if option == 'A':
                self.SIST_profile=load_profile(basedir+"data/"+self.name+"/sequence.fasta", start, end, self.seq, option=option)
            elif option == 'Z':
                self.SIST_profile=load_profile(basedir+"data/"+self.name+"/sequence.fasta", start, end, self.seq, option=option)
            elif option == 'C':
                self.SIST_profile=load_profile(basedir+"data/"+self.name+"/sequence.fasta", start, end, self.seq, option=option)
            else:
                print("This option doesn't exist")
        else:
            self.SIST_profile=load_profile(basedir+"data/"+self.name+"/sequence.fasta", start, end, self.seq)

    def load_dom(self):
        i=1
        if not hasattr(self, 'dom'):
            self.dom={}
            if not self.load_annotation():
                self.load_annotation_gff()
            self.load_expression_level()
        with open(basedir+"data/"+self.name+"/domains.txt","r") as f:
            header=next(f)
            for line in f:
                line=line.strip()
                line=line.split('\t')
                self.dom[i]=Domain(start=int(line[1]),end=int(line[2]),index=i)
                self.dom[i].add_genes(self.genes)
                self.dom[i].add_domain_expression()
                self.dom[i].add_list_expression()
                i+=1
