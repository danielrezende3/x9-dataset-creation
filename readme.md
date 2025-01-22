# Hub of experiments

- [Hub of experiments](#hub-of-experiments)
  - [What each file does](#what-each-file-does)
  - [How to setup the experiments](#how-to-setup-the-experiments)
    - [Downloading the dataset](#downloading-the-dataset)
      - [Downloading TheAlgorithms/rosetta\_code](#downloading-thealgorithmsrosetta_code)
      - [Downloading codeforces dataset](#downloading-codeforces-dataset)
    - [How to download dolos, version 2.9](#how-to-download-dolos-version-29)
    - [How to download jplag, version 5.1](#how-to-download-jplag-version-51)
    - [Preparing venv](#preparing-venv)
  - [How to run the dataset](#how-to-run-the-dataset)
    - [For dolos](#for-dolos)
    - [For jplag](#for-jplag)
  - [Experiments](#experiments)
    - [Experiment 1: Verify if modified files yield identical I/O](#experiment-1-verify-if-modified-files-yield-identical-io)
    - [Experiment 2: Verify precision recall and f1-score of dolos and jplag](#experiment-2-verify-precision-recall-and-f1-score-of-dolos-and-jplag)

## What each file does

- `dataset/`: contains the dataset used in the experiments
- `scripts/`: contains the scripts used to run the experiments
  - `check_execution.py`: checks if the output of the experiments is correct
  - `compute_score.py`: computes the precision, recall and f1-score of the experiments
  - `obfuscate_files.py`: obfuscates the files in the dataset
  - `utils.py`: contains the utility functions used in the experiments

## How to setup the experiments

### Downloading the dataset

#### Downloading TheAlgorithms/rosetta_code

TODO!

#### Downloading codeforces dataset

TODO!

### How to download dolos, version 2.9

Note: need to have npm installed on your environment

```bash
npm install -g @dodona/dolos
```

### How to download jplag, version 5.1

Note: You also need to have java installed on your environment

```bash
wget -P ./scripts https://github.com/jplag/JPlag/releases/download/v5.1.0/jplag-5.1.0-jar-with-dependencies.jar
```

### Preparing venv

```bash
python -m venv .venv 
source venv/bin/activate
pip install -r requirements.txt
```

## How to run the dataset

### For dolos

```bash
dolos --output-format csv --language python dataset/python_minifier/*.py
```

### For jplag

```bash
java -jar scripts/jplag-5.1.0.jar -l python3 dataset/python_minifier --csv-export 
```

## Experiments

### Experiment 1: Verify if modified files yield identical I/O

|Dataset|obfuscation type|Notes|
|-------|----------------|-----|
|TheAlgorithms/rosetta_code|python-minifier default settings|Identical|
|TheAlgorithms/rosetta_code|pyminifier -O|Different|

### Experiment 2: Verify precision recall and f1-score of dolos and jplag

Default settings dolos and jplag, the result is in (precision, recall, f1-score) format

|Dataset| Experiment                       | dolos              | jplag              |
|--------------------------------| -------------------------------- | ------------------ | ------------------ |
|TheAlgorithms/rosetta_code| python-minifier default settings | (1.00, 0.10, 0.18) | (1.00, 0.82, 0.90) |
|TheAlgorithms/rosetta_code| pyminifier -O | x | x |
