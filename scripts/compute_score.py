import argparse
import sys
import pandas as pd
from sklearn.metrics import f1_score, precision_score, recall_score


def calculate_and_print_score(data: pd.DataFrame) -> None:
    precision = precision_score(data["ground_truth"], data["prediction"])
    recall = recall_score(data["ground_truth"], data["prediction"])
    f1 = f1_score(data["ground_truth"], data["prediction"])

    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")
    print(f"f1-score: {f1:.2f}")
    print(f"({precision:.2f}, {recall:.2f}, {f1:.2f})")


def get_variables_for_model(model_type: str) -> tuple[str, str, str]:
    if model_type == "jplag":
        return "submissionName1", "submissionName2", "averageSimilarity"
    elif model_type == "dolos":
        return "leftFilePath", "rightFilePath", "similarity"
    else:
        raise ValueError(f"Unknown model type: {model_type}")


def process_data(data: pd.DataFrame, model_type: str) -> pd.DataFrame:
    submission1, submission2, similarity = get_variables_for_model(model_type)
    try:
        data["problem1"] = data[submission1].str.extract(r"problem_(\d+)", expand=False)
        data["problem2"] = data[submission2].str.extract(r"problem_(\d+)", expand=False)

        data["ground_truth"] = data["problem1"] == data["problem2"]
        threshold = 0.8
        data["prediction"] = data[similarity] > threshold
        return data
    except KeyError:
        sys.exit(
            f"compute_score.py: error: Could not find columns for model type {model_type} in the CSV file"
        )


def main(csv_path: str, model_type) -> None:
    data = pd.read_csv(csv_path)

    data = process_data(data, model_type)

    calculate_and_print_score(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute the score of the model")
    parser.add_argument(
        "csv_path",
        type=str,
        help="The path to the CSV file containing the ground truth and predictions",
    )
    parser.add_argument(
        "model_type",
        type=str,
        help="Type of the model, either 'dolos' or 'jplag'",
    )
    args = parser.parse_args()

    if args.model_type not in ["dolos", "jplag"]:
        print("compute_score.py: error: model_type must be either 'dolos' or 'jplag'")

    csv_path = args.csv_path
    model_type = args.model_type

    main(csv_path, model_type)
