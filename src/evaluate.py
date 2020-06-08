###############################################################################
#
#   Copyright 2019 Secretaría de Estado para el Avance Digital (SEAD)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#                      PharmaCoNER Evaluation Script
#
# This script is distributed as apart of the Pharmacological Substances,
# Compounds and proteins and Named Entity Recognition (PharmaCoNER) task.
# It is slightly based on the evaluation script from the i2b2 2014
# Cardiac Risk and Personal Health-care Information (PHI) tasks. It is
# intended to be used via command line:
#
# $> python evaluate.py [ner|indexing] GOLD SYSTEM
#
# It produces Precision, Recall and F1 (P/R/F1) measures for both subtracks.
#
# SYSTEM and GOLD may be individual files or also directories in which case
# all files in SYSTEM will be compared to files the GOLD directory based on
# their file names.
#
# Basic Examples:
#
# $> python evaluate.py ner gold/01.ann system/run1/01.ann
#
# Evaluate the single system output file '01.ann' against the gold standard
# file '01.ann' for the NER subtrack. Input files in BRAT format.
#
# $> python evaluate.py indexing gold/01.tsv system/run1/01.tsv
#
# Evaluate the single system output file '01.tsv' against the gold standard
# file '01.tsv' for the Concept Indexing subtrack. Input files in TSV format.
#
# $> python evaluate.py indexing gold/ system/run1/
#
# Evaluate the set of system outputs in the folder system/run1 against the
# set of gold standard annotations in gold/ using the Concept Indexing
# subtrack. Input files in TSV format.
#
# $> python evaluate.py ner gold/ system/run1/ system/run2/ system/run3/
#
# Evaluate the set of system outputs in the folder system/run1, system/run2
# and in the folder system/run3 against the set of gold standard annotations
# in gold/ using the NER subtrack. Input files in BRAT format.

import os
import argparse
from classes import BratAnnotation, IndexingAnnotation, NER_Evaluation, Indexing_Evaluation
from collections import defaultdict
class evaluation(object):

    def __init__(self):
        self.format = None
        self.subtrack = []
        self.system = ""
        self.gs = ""
        self.subtask1 = ""
        self.subtask2 = ""


    def get_document_dict_by_system_id(self, system_dirs, annotation_format):
        """Takes a list of directories and returns annotations. """

        documents = defaultdict(lambda: defaultdict(int))

        for fn in os.listdir(system_dirs):
            if fn.endswith(".ann") or fn.endswith(".tsv"):
                sa = annotation_format(os.path.join(system_dirs, fn))
                documents[sa.sys_id][sa.id] = sa

        return documents



    def subtracking(self,system):
        for ta in os.listdir(system):
            if ta.endswith("subtask1"):
                self.subtask1 = "subtask1"
                self.subtrack.append(NER_Evaluation)
                self.format = BratAnnotation
            if ta.endswith("subtask2"):
                self.subtask2 = "subtask2"
                self.subtrack.append(Indexing_Evaluation)
                self.format = IndexingAnnotation


    def checking(self,gs):
        for st in self.subtrack:
            subtask = os.path.join(self.system, "subtask1" if st == NER_Evaluation else "subtask2")
            for filename in os.listdir(gs):
                if filename.endswith(".ann") or filename.endswith(".tsv"):
                    result = os.path.isfile(os.path.join(subtask,filename))
                    if result == False:
                        return result

        return True

    def eval(self, input, output):
        """Evaluate the system by calling either NER_evaluation or Indexing_Evaluation.
        'system' can be a list containing either one file,  or one or more
        directories. 'gs' can be a file or a directory. """

        gold_ann = {}
        evaluations = []

        system = os.path.join(input,'res')
        gs = os.path.join(input, 'ref')


        # Handle if two files were passed on the command line
        if os.path.isdir(system) and os.path.isdir(gs):

            self.subtracking(system)

            results  = []
            if not os.path.exists(output):
                os.makedirs(output)
            result_file = os.path.join(output,"scores.txt")
            file_W = open(result_file, 'w+')

            correctFile = self.checking(gs)

            if correctFile:
                if len(self.subtrack) >= 1:
                    for st in self.subtrack:


                        subtask = os.path.join(gs, "subtask1" if st == NER_Evaluation else "subtask2")

                        for filename in os.listdir(subtask):
                            if filename.endswith(".ann") or filename.endswith(".tsv"):
                                format = BratAnnotation if st == NER_Evaluation else IndexingAnnotation
                                annotations = format(os.path.join(subtask, filename))
                                gold_ann[annotations.id] = annotations


                        subtask = os.path.join(system, "subtask1" if st == NER_Evaluation else "subtask2")

                        for system_id, system_ann in sorted(
                                self.get_document_dict_by_system_id(subtask, BratAnnotation if st == NER_Evaluation else IndexingAnnotation).items()):
                            e = st(system_ann, gold_ann)
                            e.print_report(file_W)
                            evaluations.append(e)
                else:
                    print("You did not follow the submission structure\n")
                    file_W.write("You did not follow the submission structure\n")
                    file_W.write("Subtask1_Precision : {}\n".format("ERROR"))
                    file_W.write("Subtask1_Recall : {}\n".format("ERROR"))
                    file_W.write("Subtask1_F1 : {}\n".format("ERROR"))
                    file_W.write("Subtask2_Precision : {}\n".format("ERROR"))
                    file_W.write("Subtask2_Recall : {}\n".format("ERROR"))
                    file_W.write("Subtask2_F1 : {}\n".format("ERROR"))

            else:
                print("You did not annotate all data\n")
                file_W.write("You did not follow the submission structure\n")
                file_W.write("Subtask1_Precision : {}\n".format("ERROR"))
                file_W.write("Subtask1_Recall : {}\n".format("ERROR"))
                file_W.write("Subtask1_F1 : {}\n".format("ERROR"))
                file_W.write("Subtask2_Precision : {}\n".format("ERROR"))
                file_W.write("Subtask2_Recall : {}\n".format("ERROR"))
                file_W.write("Subtask2_F1 : {}\n".format("ERROR"))

            file_W.close()

        else:
            Exception("Must pass file file or [directory/]+ directory/"
                      "on command line!")

        return evaluations[0] if len(evaluations) == 1 else evaluations


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluation script for the PharmaCoNER track.")

    parser.add_argument("input_dir",
                        help="Directory to load GS and Submitions")
    parser.add_argument("output_dir",
                        help="Directory to print results")

    args = parser.parse_args()

    x = evaluation()
    x.eval(args.input_dir, args.output_dir)
