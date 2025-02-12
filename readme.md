# Experiment Hub for Code4Bench

This repository contains experiments evaluating code obfuscators using the [Code4Bench](https://github.com/code4bench/Code4Bench) database.

## Key Results (Preliminary)

Evaluation metrics (Dolos, JPlag) for precision, recall, and F1-score:

| Obfuscator                   | Precision  | Recall     | F1-Score   |  Correct Output |
| ---------------------------- | ---------- | ---------- | ---------- |  -------------- |
| codeforces_pyminifier        | 1.00, 1.00 | 0.53, 0.81 | 0.69, 0.89 |  35/300         |
| codeforces_python_minifier   | 1.00, 1.00 | 0.85, 0.88 | 0.92, 0.94 |  295/300        |
| codeforces_python_obfuscator | 1.00, 1.00 | 0.98, 0.99 | 0.99, 0.99 |  213/300        |
| gnu_c_stunnix                | 0.00, 1.00 | 0.00, 0.93 | 0.00, 0.97 |  292/300        |

## Setup Guide

### Prerequisites

- Python 3.8 (required for specific imports)
- Java Runtime
- `unrar`, `wget`, `mysql`, `npm`

### Configuration

1. Create `.env` file:

   ```bash
   DB_USER=username
   DB_PASSWORD=username_password
   DB_HOST=database_host
   PYTHON38_PATH=python38_path
   ```

2. Initialize Python environment:

   ```bash
   python -m venv .venv 
   source .venv/bin/activate
   pip install -r requirements.txt
   export PYTHONPATH=$PWD
   ```

3. Install tools:

   ```bash
   # Dolos (v2.9+)
   npm install -g @dodona/dolos

   # JPlag (v5.1+)
   wget -O scripts/jplag-5.1.0.jar https://github.com/jplag/JPlag/releases/download/v5.1.0/jplag-5.1.0-jar-with-dependencies.jar
   ```

4. Download and process dataset (~1 hour):

   ```bash
   chmod +x import_sql.sh
   ./import_sql.sh  # Requires unrar, wget, mysql
   ```

## Usage

Run the full workflow:

```bash
make
```

Calculate scores only:

```bash
make score
```
