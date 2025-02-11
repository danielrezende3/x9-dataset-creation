# Explanation of the scripts

`dataset/`: contains the dataset used in the experiments

- `dataset/codeforces`: contains the codeforces dataset
- `dataset/codeforces_input`: contains the input of the codeforces dataset
- `dataset/codeforces_output`: contains the output of the codeforces dataset
- `dataset/codeforces_pyminifier`: contains the codeforces dataset obfuscated with pyminifier
- `dataset/codeforces_python_minifier`: contains the codeforces dataset obfuscated with python-minifier
- `dataset/codeforces_python_obfuscator`: contains the codeforces dataset obfuscated with python-obfuscator

`scripts/`: contains the scripts used to run the experiments

- `check_execution.py`: checks if the output of the experiments is correct
- `compute_score.py`: computes the precision, recall and f1-score of the experiments
  - ATTENTION: This script needs the flags `--include_original` `--include_suffix` in `obfuscate_files.py` to work properly
- `obfuscate_files.py`: obfuscates the files in the dataset
- `process_codeforces_database.py`: process the database and creates the dataset
- `utils.py`: contains the utility functions used in the experiments

## Language ID's

| Language | ID | Submission count|
|----------|----|-|
| GNU C      | 2  |93,492|
| Python   | 8  |52,433|
|GNU C 11 | 12|18,574|

## stunnix

Production mode with md5 mangler for all symbols. Comments are removed, whitespace is jammed, strings and integers are mangled too.

## Picheta

NOT WORKING!

## Tigress options

**1\. Basic Control Flow Flattening**

This transformation restructures the control flow of a function to make it less predictable:

```bash
tigress --Transform=Flatten --Functions=* --out=Flatten.c input.c
```

**2\. Encoding Literals**

To obscure constant values in the code, you can encode literals:

```bash
tigress --Transform=EncodeLiterals --Functions=* --out=EncodeLiterals.c input.c
```

**3\. Function Merging**

Combine multiple functions into one to complicate analysis:

```bash
tigress --Transform=Merge --Functions=func1,func2 --out=Merge.c input.c
```

**4\. Virtualization**

Transform a function into a virtual machine to significantly increase complexity:

```bash
tigress --Transform=Virtualize --Functions=target_function --out=Virtualize.c input.c
```

**5\. Composite Transformation**

Apply a sequence of transformations for enhanced obfuscation:

```bash
tigress --Transform=EncodeLiterals --Functions=target_function \
        --Transform=Flatten --Functions=target_function \
        --Transform=Virtualize --Functions=target_function \
        --out=output.c input.c
```
