# 1. Introduction

Scripts to compute Cantemist evaluation metrics.

Written in Python 3.8

Output is printed in terminal.

# 2. Requirements

+ Python3
+ pandas
+ trectools

To install them: 
```
pip install -r requirements.txt
```


# 3. Execution
+ CANTEMIST-NER

```
cd src  
python main.py -g ../gs-data/ -p ../toy-data/ -s ner
```

+ CANTEMIST-NORM

```
cd src
python main.py -g ../gs-data/ -p ../toy-data/ -s norm
```

+ CANTEMIST-CODING

```
cd src
python main.py -g ../gs-data/gs-coding.tsv -p ../toy-data/pred-coding.tsv -c ../valid-codes.tsv -s coding
```

# 4. Other interesting stuff:
### Metrics
For CANTEMIST-NER and CANTEMIST-NORM, the relevant metrics are precision, recall and f1-score. The latter will be used to decide the award winners.
For CANTEMIT-CODING, the relevant metric is Mean Average Precision.
For more information about metrics, see the shared task webpage: https://temu.bsc.es/cantemist

### Script Arguments
+ ```-g/--gs_path```: path to directory with Gold Standard .ann files (if we are in subtask NER or NORM) or path to Gold Standard TSV file (if we are in subtask CODING)
+ ```-p/--pred_path```: path to directory with Prediction .ann files (if we are in subtask NER or NORM) or path to Prediction TSV file (if we are in subtask CODING)
+ ```-c/--valid_codes_path```: path to TSV file with valid codes (provided here). Codes not included in this TSV will not be used for MAP computation.
+ ```-s/--subtask```: subtask name (```ner```, ```norm```, or ```coding```).

### Examples: 
+ CANTEMIST-NER

```
$ cd src
$ python main.py -g ../gs-data/ -p ../toy-data/ -s ner

-----------------------------------------------------
Clinical case name			Precision
-----------------------------------------------------
cc_onco1.ann		0.5
-----------------------------------------------------
cc_onco3.ann		1.0
-----------------------------------------------------

Micro-average precision = 0.846


-----------------------------------------------------
Clinical case name			Recall
-----------------------------------------------------
cc_onco1.ann		0.667
-----------------------------------------------------
cc_onco3.ann		1.0
-----------------------------------------------------

Micro-average recall = 0.917


-----------------------------------------------------
Clinical case name			F-score
-----------------------------------------------------
cc_onco1.ann		0.571
-----------------------------------------------------
cc_onco3.ann		1.0
-----------------------------------------------------

Micro-average F-score = 0.88

```

+ CANTEMIST-NORM

```
$ cd src
$ python main.py -g ../gs-data/ -p ../toy-data/ -s norm

-----------------------------------------------------
Clinical case name			Precision
-----------------------------------------------------
cc_onco1.ann		0.25
-----------------------------------------------------
cc_onco3.ann		1.0
-----------------------------------------------------

Micro-average precision = 0.769


-----------------------------------------------------
Clinical case name			Recall
-----------------------------------------------------
cc_onco1.ann		0.333
-----------------------------------------------------
cc_onco3.ann		1.0
-----------------------------------------------------

Micro-average recall = 0.833


-----------------------------------------------------
Clinical case name			F-score
-----------------------------------------------------
cc_onco1.ann		0.286
-----------------------------------------------------
cc_onco3.ann		1.0
-----------------------------------------------------

Micro-average F-score = 0.8

```

+ CANTEMIST-CODING

```
$ cd src
$ python main.py -g ../gs-data/gs-coding.tsv -p ../toy-data/pred-coding.tsv -c ../valid-codes.tsv -s coding

MAP estimate: 0.75

```

