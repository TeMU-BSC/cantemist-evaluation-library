#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 8 15:22:29 2020

@author: tonifuc3m
"""

import argparse
import warnings

import cantemist_coding
import cantemist_ner_norm

def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    return '%s:%s: %s: %s\n' % (filename, lineno, category.__name__, message)
warnings.formatwarning = warning_on_one_line

def parse_arguments():
    '''
    DESCRIPTION: Parse command line arguments
    '''
  
    parser = argparse.ArgumentParser(description='process user given parameters')
    parser.add_argument("-g", "--gs_path", required = True, dest = "gs_path", 
                        help = "path to GS file")
    parser.add_argument("-p", "--pred_path", required = True, dest = "pred_path", 
                        help = "path to predictions file")
    parser.add_argument("-c", "--valid_codes_path", required = False, 
                        default = '../valid-codes.tsv',
                        dest = "codes_path", help = "path to valid codes TSV")
    parser.add_argument('-s', '--subtask', required = True, dest = 'subtask',
                        choices=['ner', 'norm', 'coding'],
                        help = 'Subtask name')
    
    args = parser.parse_args()
    gs_path = args.gs_path
    pred_path = args.pred_path
    codes_path = args.codes_path
    subtask = args.subtask
    
    return gs_path, pred_path, codes_path, subtask


if __name__ == '__main__':
    
    gs_path, pred_path, codes_path, subtask = parse_arguments()
    
    if subtask == 'coding':
        cantemist_coding.main(gs_path, pred_path, codes_path)
    elif subtask == 'ner':
        cantemist_ner_norm.main(gs_path, pred_path, subtask='ner')
    elif subtask == 'norm':
        cantemist_ner_norm.main(gs_path, pred_path, subtask='norm')
        