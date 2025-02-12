import argparse
import subprocess
from glob import glob
from pathlib import Path

import pandas as pd
from sklearn.metrics import f1_score, precision_score, recall_score

from scripts.utils import log_error, validate_directories

FILE_NAME = Path(__file__).stem


def compute_score_metrics(data: pd.DataFrame) -> tuple[float, float, float]:
    precision = precision_score(
        data["ground_truth"], data["prediction"], zero_division=0
    )
    recall = recall_score(data["ground_truth"], data["prediction"], zero_division=0)
    f1 = f1_score(data["ground_truth"], data["prediction"], zero_division=0)
    return float(precision), float(recall), float(f1)


def retrieve_model_variables(model_type: str) -> tuple[str, str, str]:
    if model_type == "jplag":
        return "submissionName1", "submissionName2", "averageSimilarity"
    elif model_type == "dolos":
        return "leftFilePath", "rightFilePath", "similarity"
    else:
        log_error(FILE_NAME, f"Unknown model type: {model_type}")


def evaluate_similarity(data: pd.DataFrame, model_type: str) -> pd.DataFrame:
    submission1, submission2, similarity = retrieve_model_variables(model_type)
    try:
        data["problem1"] = data[submission1].str.extract(r"problem_(\d+)", expand=False)
        data["problem2"] = data[submission2].str.extract(r"problem_(\d+)", expand=False)

        data["ground_truth"] = data["problem1"] == data["problem2"]
        threshold = 0.8
        data["prediction"] = data[similarity] >= threshold
        return data
    except KeyError:
        log_error(
            FILE_NAME,
            f"Could not find columns for model type {model_type} in the CSV file",
        )


def read_csv_calc_print_score(csv_path: Path, model: str) -> None:
    print(f"--- {model} ---")
    data = pd.read_csv(csv_path)
    data = evaluate_similarity(data, model)
    precision, recall, f1 = compute_score_metrics(data)

    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")
    print(f"f1-score: {f1:.2f}")
    print(f"({precision:.2f}, {recall:.2f}, {f1:.2f})")


def main(config: argparse.Namespace) -> None:
    folder_path = Path(config.folder_path)

    files_py = glob(f"./{folder_path}/*.py")
    files_c = glob(f"./{folder_path}/*.c")
    # Ensure that the folder contains only one file type.
    if files_py and files_c:
        log_error(
            FILE_NAME,
            "Folder must contain only one type of files: either Python or C files, not both.",
        )
    elif files_py:
        dolos_language = "python"
        files = files_py
        jplag_language = "python3"
    elif files_c:
        dolos_language = "C"
        files = files_c
        jplag_language = "c"
    else:
        log_error(FILE_NAME, "No valid Python or C files found in the folder.")

    # Execute dolos on the selected files.
    dolos_result = subprocess.run(
        [
            "dolos",
            "--output-format",
            "csv",
            "--language",
            dolos_language,
            *files,
        ],
        capture_output=True,
        text=True,
    )

    # Extract the output directory from dolos's stdout.
    try:
        first_line = dolos_result.stdout.splitlines()[0]
        output_dir = first_line.split(":")[1].strip()
    except (IndexError, ValueError):
        log_error(FILE_NAME, "Unexpected output format from dolos.")

    read_csv_calc_print_score(Path(f"./{output_dir}/pairs.csv"), "dolos")

    # Run jplag
    subprocess.run(
        [
            "java",
            "-jar",
            "scripts/jplag-5.1.0.jar",
            "-l",
            jplag_language,
            str(folder_path),
            "--csv-export",
            "--cluster-skip",
        ],
        timeout=10,
        capture_output=True,
        text=True,
    )

    read_csv_calc_print_score(Path("./results/results.csv"), "jplag")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run and compute the score of the dataset"
    )
    parser.add_argument(
        "folder_path",
        type=str,
        help="The path to the solutions folder, needs to be all files, original and obfuscated",
    )
    args = parser.parse_args()

    validate_directories(FILE_NAME, Path(args.folder_path))
    main(args)
