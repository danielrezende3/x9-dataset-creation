# Hub of experiments

1. Download dolos
2. Download jplag
3. Setup the TheAlgorithms/projectEuler
4. Check execution of files
5. Obfuscate with a method
6. Compute the score

## How to setup the experiments

How to download dolos

```
npm install -g @dodona/dolos
```

Versions of 
- dolos: v2.9.0
- jplag: v5.1.0



```bash
dolos --output-format csv --language python dataset/python_minifier/*.py
```

```bash
java -jar scripts/jplag-5.1.0.jar -l python3 dataset/python_minifier --csv-export 
```

## Using python-minifier

Default settings dolos and jplag

(precision, recall, f1-score)

|#Experiment | dolos | jplag
|-|-|-|
|python-minifier default settings|(1.00, 0.10, 0.18)|(1.00, 0.82, 0.90)|


how can I create an automation that check the f1 score?