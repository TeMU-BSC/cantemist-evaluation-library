#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 8 15:22:29 2020

@author: tonifuc3m
"""

import pandas as pd
import ann_parsing
import warnings

def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    return '%s:%s: %s: %s\n' % (filename, lineno, category.__name__, message)
warnings.formatwarning = warning_on_one_line


def main(gs_path, pred_path, subtask=['ner','norm']):
    '''
    Load GS and Predictions; format them; compute precision, recall and 
    F1-score and show them.

    Parameters
    ----------
    gs_path : str
        Path to directory with GS .ANN files (Brat format).
    pred_path : str
        Path to directory with Predicted .ANN files (Brat format).

    Returns
    -------
    None.

    '''
    if subtask=='norm':
        gs = ann_parsing.main(gs_path, ['MORFOLOGIA_NEOPLASIA'], with_notes=True)
        pred = ann_parsing.main(pred_path, ['MORFOLOGIA_NEOPLASIA'], with_notes=True)
        gs.columns = ['clinical_case', 'mark', 'label', 'offset', 'span', 'code_gs',
                      'start_pos_gs', 'end_pos_gs']
        pred.columns = ['clinical_case', 'mark', 'label', 'offset', 'span', 'code_pred',
                      'start_pos_pred', 'end_pos_pred']
    elif subtask=='ner':
        gs = ann_parsing.main(gs_path, ['MORFOLOGIA_NEOPLASIA'], with_notes=False)
        pred = ann_parsing.main(pred_path, ['MORFOLOGIA_NEOPLASIA'], with_notes=False)
        gs.columns = ['clinical_case', 'mark', 'label', 'offset', 'span', 
                      'start_pos_gs', 'end_pos_gs']
        pred.columns = ['clinical_case', 'mark', 'label', 'offset', 'span',
                      'start_pos_pred', 'end_pos_pred']
    else:
        raise Exception('Error! Subtask name not properly set up')

    
    P_per_cc, P, R_per_cc, R, F1_per_cc, F1 = calculate_metrics(gs, pred, 
                                                                subtask=subtask)
        
    ###### Show results ######  
    print('\n-----------------------------------------------------')
    print('Clinical case name\t\t\tPrecision')
    print('-----------------------------------------------------')
    for index, val in P_per_cc.items():
        print(str(index) + '\t\t' + str(round(val, 3)))
        print('-----------------------------------------------------')
    if any(P_per_cc.isna()):
        warnings.warn('Some documents do not have predicted codes, ' + 
                      'document-wise Precision not computed for them.')
        
    print('\nMicro-average precision = {}\n'.format(round(P, 3)))
    
    print('\n-----------------------------------------------------')
    print('Clinical case name\t\t\tRecall')
    print('-----------------------------------------------------')
    for index, val in R_per_cc.items():
        print(str(index) + '\t\t' + str(round(val, 3)))
        print('-----------------------------------------------------')
    if any(R_per_cc.isna()):
        warnings.warn('Some documents do not have Gold Standard codes, ' + 
                      'document-wise Recall not computed for them.')
    print('\nMicro-average recall = {}\n'.format(round(R, 3)))
    
    print('\n-----------------------------------------------------')
    print('Clinical case name\t\t\tF-score')
    print('-----------------------------------------------------')
    for index, val in F1_per_cc.items():
        print(str(index) + '\t\t' + str(round(val, 3)))
        print('-----------------------------------------------------')
    if any(P_per_cc.isna()):
        warnings.warn('Some documents do not have predicted codes, ' + 
                      'document-wise F-score not computed for them.')
    if any(R_per_cc.isna()):
        warnings.warn('Some documents do not have Gold Standard codes, ' + 
                      'document-wise F-score not computed for them.')
    print('\nMicro-average F-score = {}\n'.format(round(F1, 3)))


def calculate_metrics(gs, pred, subtask=['ner','norm']):
    '''       
    Calculate task Coding metrics:
    
    Two type of metrics are calculated: per document and micro-average.
    In case a code has several references, just acknowledging one is enough.
    In case of discontinuous references, the reference is considered to 
    start and the start position of the first part of the reference and to 
    end at the final position of the last part of the reference.
    
    INPUT: 
        gs: pandas dataframe
            with the Gold Standard. Columns are those output by the function read_gs.
        pred: pandas dataframe
            with the predictions. Columns are those output by the function read_run.
    
    OUTPUT: 
        P_per_cc: pandas series
            Precision per clinical case (index contains clinical case names)
        P: float
            Micro-average precision
        R_per_cc: pandas series
            Recall per clinical case (index contains clinical case names)
        R: float
            Micro-average recall
        F1_per_cc: pandas series
            F-score per clinical case (index contains clinical case names)
        F1: float
            Micro-average F-score
    '''
    
    # Predicted Positives:
    Pred_Pos_per_cc = \
        pred.drop_duplicates(subset=['clinical_case', "offset"]).\
        groupby("clinical_case")["offset"].count()
    Pred_Pos = pred.drop_duplicates(subset=['clinical_case', "offset"]).shape[0]
    '''
    Pred_Pos_per_cc = \
        pred.drop_duplicates(subset=pred.columns.difference(['mark'])).\
        groupby("clinical_case")["offset"].count() ---> ¿?¿?¿?
    Pred_Pos = pred.drop_duplicates(subset=pred.columns.difference(['mark'])).shape[0]
    '''
    
    # Gold Standard Positives:
    GS_Pos_per_cc = \
        gs.drop_duplicates(subset=['clinical_case', "offset"]).\
        groupby("clinical_case")["offset"].count()
    GS_Pos = gs.drop_duplicates(subset=['clinical_case', "offset"]).shape[0]
    
    # Eliminate predictions not in GS (prediction needs to be in same clinical
    # case and to have the exact same offset to be considered valid!!!!)
    df_sel = pd.merge(pred, gs, 
                      how="right",
                      on=["clinical_case", "offset"])
    
    if subtask=='norm':
        # Check if codes are equal
        df_sel["is_valid"] = \
            df_sel.apply(lambda x: (x["code_gs"] == x["code_pred"]), axis=1)
    elif subtask=='ner':
        is_valid = df_sel.apply(lambda x: x.isnull().any()==False, axis=1)
        df_sel = df_sel.assign(is_valid=is_valid.values)
    else:
        raise Exception('Error! Subtask name not properly set up')
    
    # True Positives:
    TP_per_cc = (df_sel[df_sel["is_valid"] == True]
                 .groupby("clinical_case")["is_valid"].count())
    TP = df_sel[df_sel["is_valid"] == True].shape[0]
    
    # Add entries for clinical cases that are not in predictions but are present
    # in the GS
    cc_not_predicted = (pred.drop_duplicates(subset=["clinical_case"])
                        .merge(gs.drop_duplicates(subset=["clinical_case"]), 
                              on='clinical_case',
                              how='right', indicator=True)
                        .query('_merge == "right_only"')
                        .drop('_merge', 1))['clinical_case'].to_list()
    for cc in cc_not_predicted:
        TP_per_cc[cc] = 0
    
    # Remove entries for clinical cases that are not in GS but are present
    # in the predictions
    cc_not_GS = (gs.drop_duplicates(subset=["clinical_case"])
                .merge(pred.drop_duplicates(subset=["clinical_case"]), 
                      on='clinical_case',
                      how='right', indicator=True)
                .query('_merge == "right_only"')
                .drop('_merge', 1))['clinical_case'].to_list()
    Pred_Pos_per_cc = Pred_Pos_per_cc.drop(cc_not_GS)

    # Calculate Final Metrics:
    P_per_cc =  TP_per_cc / Pred_Pos_per_cc
    P = TP / Pred_Pos
    R_per_cc = TP_per_cc / GS_Pos_per_cc
    R = TP / GS_Pos
    F1_per_cc = (2 * P_per_cc * R_per_cc) / (P_per_cc + R_per_cc)
    if (P+R) == 0:
        F1 = 0
        warnings.warn('Global F1 score automatically set to zero to avoid division by zero')
        return P_per_cc, P, R_per_cc, R, F1_per_cc, F1
    F1 = (2 * P * R) / (P + R)
                                            
    return P_per_cc, P, R_per_cc, R, F1_per_cc, F1