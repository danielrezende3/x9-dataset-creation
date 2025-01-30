# Hub of experiments

This repo contains the experiments done for the [code4bench](https://github.com/code4bench/Code4Bench) database

## Preliminary results

Note: The results scores are in the format (dolos, jplag)

|obfuscator|precision |recall|f1-score|correct output|
|---|---|---|---|---|
|codeforces_pyminifier| 1.00, 1.00| 0.53, 0.81| 0.69, 0.89|35/300|
|codeforces_python_minifier| 1.00, 1.00| 0.85, 0.88| 0.92, 0.94|295/300|
|codeforces_python_obfuscator| 1.00, 1.00| 0.98, 0.99| 0.99, 0.99| 213/300|

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

Before hand, you need to have the following installed on your environment:

- python3.8, this is because the code have some imports that are only available in this version
- java runtime
- unrar
- wget
- mysql
- npm

After that you need to setup the environmet variables in `.env` file

```bash
DB_USER=username
DB_PASSWORD=username_password
DB_HOST=database_host
PYTHON38_PATH=python38_path
```

### Preparing venv

```bash
python -m venv .venv 
source .venv/bin/activate
pip install -r requirements.txt
```

### How to download dolos, at least version 2.9

Need to have npm installed on your environment

```bash
npm install -g @dodona/dolos
```

### How to download jplag, at least version 5.1

Need to have java installed on your environment

```bash
wget -O scripts/jplag-5.1.0.jar https://github.com/jplag/JPlag/releases/download/v5.1.0/jplag-5.1.0-jar-with-dependencies.jar
```

### Downloading and processing the dataset

First you need to setup the environment before doing the script

BEFORE: Check if `unrar`, `wget` and `mysql` are installed on your environment

WARNING: The script will take some time to download and process the database (~1 hour)

```bash
chmod +x import_sql.sh
./import_sql.sh
```

## Usage Instructions

### Run the Entire Workflow

```bash
make
```

### Alternatively, run only the score computation

```bash
make score
```
