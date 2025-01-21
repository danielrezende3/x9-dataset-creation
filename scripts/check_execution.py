import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from tqdm import tqdm
from utils import get_files_from_folder

DATA_SET_ORIGINAL_FOLDER = Path("./dataset/original")
DATA_SET_OBFUSCATED_FOLDER = Path("./dataset/minifier")
TIMEOUT_SECONDS = 15


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


def main():
    files = get_files_from_folder(DATA_SET_ORIGINAL_FOLDER)
    correct_count = 0

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for file in files:
            original_path = DATA_SET_ORIGINAL_FOLDER / file
            obfuscated_path = DATA_SET_OBFUSCATED_FOLDER / file
            futures.append(
                executor.submit(
                    compare_stdout_of_two_files, original_path, obfuscated_path
                )
            )

        for future in tqdm(futures):
            is_correct = future.result()
            correct_count += int(is_correct)

    print(f"Correct count: {correct_count}/{len(files)}")


if __name__ == "__main__":
    main()
