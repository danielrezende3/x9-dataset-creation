import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse
from tqdm import tqdm
from utils import get_files_from_folder, log_error

TIMEOUT_SECONDS = 15
FILE_NAME = Path(__file__).stem


def run_and_save_stdout(file_path: Path) -> str:
    try:
        result = subprocess.run(
            ["python", file_path],
            input="100",
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        raise


def compare_stdout_of_two_files(file1: Path, file2: Path) -> bool:
    try:
        stdout1 = run_and_save_stdout(file1)
        stdout2 = run_and_save_stdout(file2)
        return stdout1 == stdout2
    except subprocess.TimeoutExpired as e:
        print(f"Timeout expired for file: {e.cmd}")
        return False


def main(data_set_orifinal_folder: Path, data_set_obfuscated_folder: Path) -> None:
    original_files = sorted(get_files_from_folder(data_set_orifinal_folder))
    obfuscated_files = sorted(get_files_from_folder(data_set_obfuscated_folder))
    correct_count = 0

    if len(original_files) != len(obfuscated_files):
        log_error(
            FILE_NAME,
            "The number of files in the original and obfuscated folders do not match.",
        )

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for original_file, obfuscated_file in zip(original_files, obfuscated_files):
            futures.append(
                executor.submit(
                    compare_stdout_of_two_files, original_file, obfuscated_file
                )
            )

        for future in tqdm(futures):
            is_correct = future.result()
            correct_count += int(is_correct)

    print(f"Correct count: {correct_count}/{len(original_files)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check if the obfuscation and original match the same output"
    )
    parser.add_argument(
        "--original_folder",
        type=str,
        default="./dataset/original",
        help="The path to the folder containing the original files",
    )
    parser.add_argument(
        "--obfuscated_folder",
        type=str,
        help="The path to the folder containing the obfuscated files",
    )

    args = parser.parse_args()

    original_arg = args.original_folder
    obfuscated_arg = args.obfuscated_folder

    # Check that they are non-empty strings
    if not original_arg or not isinstance(original_arg, str):
        log_error(FILE_NAME, "--original_folder must be a valid non-empty string.")

    if not obfuscated_arg or not isinstance(obfuscated_arg, str):
        log_error(FILE_NAME, "--obfuscated_folder must be a valid non-empty string.")

    # Create the Path objects
    original_folder = Path(original_arg)
    obfuscated_folder = Path(obfuscated_arg)

    # Now check if they exist and are directories
    if not original_folder.is_dir():
        log_error(
            FILE_NAME,
            f"The path '{original_folder}' does not exist or is not a directory.",
        )

    if not obfuscated_folder.is_dir():
        log_error(
            FILE_NAME,
            f"The path '{obfuscated_folder}' does not exist or is not a directory",
        )

    main(original_folder, obfuscated_folder)
