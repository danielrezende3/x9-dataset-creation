# Hub of experiments

This repo contains the experiments done for the [code4bench](https://github.com/code4bench/Code4Bench) database

## What each file does?

- `dataset/`: contains the dataset used in the experiments
  - `dataset/codeforces`: contains the codeforces dataset
  - `dataset/codeforces_input`: contains the input of the codeforces dataset
  - `dataset/codeforces_output`: contains the output of the codeforces dataset
  - `dataset/codeforces_pyminifier`: contains the codeforces dataset obfuscated with pyminifier
  - `dataset/codeforces_python_minifier`: contains the codeforces dataset obfuscated with python-minifier
  - `dataset/codeforces_python_obfuscator`: contains the codeforces dataset obfuscated with python-obfuscator
- `scripts/`: contains the scripts used to run the experiments
  - `check_execution.py`: checks if the output of the experiments is correct
  - `compute_score.py`: computes the precision, recall and f1-score of the experiments
  - `obfuscate_files.py`: obfuscates the files in the dataset
  - `process_codeforces_database.py`: process the database and creates the dataset
  - `utils.py`: contains the utility functions used in the experiments

## How to setup the experiments

### Downloading and processing the dataset

TODO!

### How to download dolos, at least version 2.9

Need to have npm installed on your environment

```bash
npm install -g @dodona/dolos
```

### How to download jplag, at least version 5.1

Need to have java installed on your environment

```bash
wget -P ./scripts https://github.com/jplag/JPlag/releases/download/v5.1.0/jplag-5.1.0-jar-with-dependencies.jar
```

### Preparing venv

```bash
python -m venv .venv 
source venv/bin/activate
pip install -r requirements.txt
```

## How to test the dataset

### For dolos

```bash
dolos --output-format csv --language python file_path/*.py
```

### For jplag

```bash
java -jar scripts/jplag-5.1.0.jar -l python3 file_path/ --csv-export 
```

## Usage Instructions

### Run the Entire Workflow

```bash
make
```

or, alternatively

```bash
make all
```

### Alternatively, run only the score computation

```bash
make score
```

### Indepedent commands

#### Set Up Only

```bash
make setup
```



#### Run Obfuscation Steps Only

```bash
make obfuscate
```

#### Run Execution Checks Only

```bash
make check
```

#### Run Score Computation Only

```bash
make score
```

#### Clean Up Generated Directories

```bash
make clean
```
