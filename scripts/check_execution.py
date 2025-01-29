import argparse
import logging
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from tqdm import tqdm
from utils import get_files_from_folder, log_error, validate_directories

# Constants -------------------------------------------------------------------
TIMEOUT_SECONDS = 15
CHUNK_SIZE = 3
FILE_NAME = Path(__file__).stem
PYTHON_EXECUTABLE = "/home/danielrezende/.pyenv/versions/3.8.20/bin/python"
NUM_WORKERS = 4
LOG_DIR = "logs"
# Logging setup Constants -----------------------------------------------------
os.makedirs(LOG_DIR, exist_ok=True)
log_filename = os.path.join(LOG_DIR, datetime.now().strftime("app_%Y-%m-%d_%H_%M.log"))


logging.basicConfig(
    filename=log_filename,
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s: %(message)s",
)
logger = logging.getLogger()


def run_script(file_path: Path, input_data: str = "100") -> str:
    """Execute a Python script and return its stdout.

    :param file_path: Path to the Python script to execute
    :param input_data: Input to pass to the script via stdin
    :returns: Captured stdout from the script execution
    :raises RuntimeError: If execution times out or encounters an error
    """
    try:
        result = subprocess.run(
            [PYTHON_EXECUTABLE, str(file_path)],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
        return result.stdout
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(f"Timeout expired for {file_path}") from e
    except Exception as e:
        raise RuntimeError(f"Error executing {file_path}") from e


def log_comparison_details(
    file1: Path,
    file2: Path,
    stdout1: str,
    stdout2: str,
    expected_output: Optional[str] = None,
) -> None:
    """
    Logs detailed comparison results for two script outputs.

    :param file1: Path to the first script.
    :param file2: Path to the second script.
    :param stdout1: Output from the first script.
    :param stdout2: Output from the second script.
    :param expected_output: Optional expected output to validate against.
    """
    if expected_output is not None:
        # Check and log discrepancies for the first script
        if stdout1 != expected_output:
            logger.error(
                f"EXPECTED_MISMATCH: [{file1.parent}/{file1.stem}] Output mismatch: "
                f"Expected '{expected_output}', Got '{stdout1}'"
            )
        # Check and log discrepancies for the second script
        if stdout2 != expected_output:
            logger.error(
                f"EXPECTED_MISMATCH: [{file2.parent}/{file2.stem}] Output mismatch: "
                f"Expected '{expected_output}', Got '{stdout2}'"
            )
    else:
        # If no expected output, compare the two outputs directly
        if stdout1 != stdout2:
            logger.error(
                f"STDOUT_MISMATCH: Output mismatch between [{file1.parent}/{file1.stem}] and "
                f"[{file2.parent}/{file2.stem}]: "
                f"'{stdout1}' != '{stdout2}'"
            )


def compare_files(
    file1: Path,
    file2: Path,
    input_data: Optional[str] = None,
    expected_output: Optional[str] = None,
) -> bool:
    """
    Compare outputs of two scripts with optional input and expected output validation.

    :param file1: Path to the first script.
    :param file2: Path to the second script.
    :param input_data: Optional input to provide to the scripts.
    :param expected_output: Optional expected output to validate against.
    :returns: True if both scripts produce matching (and expected) output, else False.
    """
    try:
        # Run both scripts with the provided input_data or default to "100"
        stdout1 = run_script(file1, input_data or "100").strip()
        stdout2 = run_script(file2, input_data or "100").strip()
        logger.info(
            f"STARTING: comparing for [{file1.parent}/{file1.stem}] and [{file2.parent}/{file2.stem}]."
        )
        # Determine if outputs match (and match expected_output if provided)
        if expected_output is not None:
            result = (stdout1 == stdout2) and (stdout1 == expected_output)
        else:
            result = stdout1 == stdout2

        if result:
            logger.info(
                f"SUCCESS: Outputs match for [{file1.parent}/{file1.stem}] and "
                f"[{file2.parent}/{file2.stem}]."
            )
        else:
            # Log detailed comparison results
            log_comparison_details(file1, file2, stdout1, stdout2, expected_output)
            logger.error(
                f"FAILURE: Outputs do not match for [{file1.parent}/{file1.stem}] and "
                f"[{file2.parent}/{file2.stem}]."
            )

        return result

    except RuntimeError as e:
        logger.error(
            f"RuntimeError while comparing [{file1.parent}/{file1.stem}] and "
            f"[{file2.parent}/{file2.stem}]: {e}"
        )
        return False


def process_tasks(
    tasks: Iterable[Tuple[Path, Path, Optional[str], Optional[str]]],
) -> int:
    """Process comparison tasks concurrently with progress tracking.

    :param tasks: Iterable of comparison tasks
    :returns: Number of successful comparisons
    """
    correct_count = 0

    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        futures = [executor.submit(compare_files, *task) for task in tasks]

        for future in tqdm(futures, desc="Processing files"):
            correct_count += int(future.result())

    return correct_count


def setup_tasks_simple(
    original_files: List[Path], obfuscated_files: List[Path]
) -> List[Tuple[Path, Path, None, None]]:
    """Create comparison tasks for basic execution without input.

    :param original_files: List of original Python script paths
    :param obfuscated_files: List of obfuscated Python script paths
    :returns: List of tasks as tuples
    """
    if len(original_files) != len(obfuscated_files):
        log_error(FILE_NAME, "Mismatch in original/obfuscated file counts")
    return [
        (orig, obf, None, None) for orig, obf in zip(original_files, obfuscated_files)
    ]


def setup_tasks_with_io(
    original_files: List[Path],
    obfuscated_files: List[Path],
    input_contents: List[str],
    output_contents: List[str],
) -> List[Tuple[Path, Path, str, str]]:
    """Create comparison tasks with input/output validation.

    :param original_files: List of original Python script paths
    :param obfuscated_files: List of obfuscated Python script paths
    :param input_contents: List of input data strings
    :param output_contents: List of expected output data strings
    :returns: List of tasks as tuples
    """
    if len(input_contents) != len(original_files) * CHUNK_SIZE:
        log_error(
            FILE_NAME,
            f"Input count mismatch. Expected {len(original_files) * CHUNK_SIZE}, got {len(input_contents)}",
        )

    if len(input_contents) != len(output_contents):
        log_error(
            FILE_NAME,
            f"Mismatch between input ({len(input_contents)}) and output ({len(output_contents)}) counts",
        )

    tasks = []
    input_chunks = [
        input_contents[i : i + CHUNK_SIZE]
        for i in range(0, len(input_contents), CHUNK_SIZE)
    ]
    output_chunks = [
        output_contents[i : i + CHUNK_SIZE]
        for i in range(0, len(output_contents), CHUNK_SIZE)
    ]

    for orig, obf, in_chunk, out_chunk in zip(
        original_files, obfuscated_files, input_chunks, output_chunks
    ):
        for inp, outp in zip(in_chunk, out_chunk):
            tasks.append((orig, obf, inp, outp))

    return tasks


def filter_matching_files(
    source_files: List[Path], reference_files: List[Path]
) -> Tuple[List[Path], List[Path]]:
    """
    Filters `source_files` and `reference_files` to keep only those with matching stems.

    Files without a suffix (extension) are ignored. The function logs the removed files
    and returns the filtered lists.

    :param source_files: List of source file paths
    :param reference_files: List of reference file paths
    :returns: A tuple containing the filtered lists of source and reference files
    """
    logger.info(
        f"Comparing {len(source_files)} from {source_files[0].parent} with {len(reference_files)} from {reference_files[0].parent}."
    )
    original_files_set = set(source_files)
    obfuscated_files_set = set(reference_files)

    original_stems = {file.stem for file in source_files if file.suffix}
    obfuscated_stems = {file.stem for file in reference_files if file.suffix}

    filtered_original_files = [
        file for file in source_files if file.suffix and file.stem in obfuscated_stems
    ]
    filtered_obfuscated_files = [
        file for file in reference_files if file.suffix and file.stem in original_stems
    ]

    removed_original = original_files_set - set(filtered_original_files)
    removed_obfuscated = obfuscated_files_set - set(filtered_obfuscated_files)

    if not removed_original and not removed_obfuscated:
        logger.info(
            f"No files were removed. Both {source_files[0].parent} and {reference_files[0].parent} remain unchanged."
        )
    else:
        if removed_original:
            logger.info(f"Removed from {source_files[0].parent}:")
            for file in removed_original:
                logger.info(str(file))
        if removed_obfuscated:
            logger.info(f"Removed from {reference_files[0].parent}:")
            for file in removed_obfuscated:
                logger.info(str(file))
        logger.info("End of removed files.")
    return filtered_original_files, filtered_obfuscated_files


def main(config: argparse.Namespace) -> None:
    """Main comparison workflow controller.

    :param config: Parsed command-line arguments
    """
    original_files = get_files_from_folder(config.original_folder)
    obfuscated_files = get_files_from_folder(config.obfuscated_folder)

    # Filter files to keep only those with matching stems
    filtered_original_files, filtered_obfuscated_files = filter_matching_files(
        original_files, obfuscated_files
    )

    if config.input_folder:
        input_files = get_files_from_folder(config.input_folder)
        output_files = get_files_from_folder(config.output_folder)

        # Filter files to keep only those with matching stems
        filtered_input_files, filtered_original_files = filter_matching_files(
            input_files, filtered_original_files
        )
        filtered_input_files, filtered_output_files = filter_matching_files(
            filtered_input_files, output_files
        )
        filtered_original_files, filtered_obfuscated_files = filter_matching_files(
            filtered_original_files, filtered_obfuscated_files
        )

        input_contents = [f.read_text() for f in filtered_input_files]
        output_contents = [f.read_text() for f in filtered_output_files]

        tasks = setup_tasks_with_io(
            filtered_original_files,
            filtered_obfuscated_files,
            input_contents,
            output_contents,
        )
    else:
        tasks = setup_tasks_simple(filtered_original_files, filtered_obfuscated_files)

    correct_count = process_tasks(tasks)
    total = len(tasks) if config.input_folder else len(original_files)

    print(f"Correct count: {correct_count}/{total}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compare outputs of original and obfuscated Python scripts"
    )
    parser.add_argument(
        "--original_folder",
        type=Path,
        required=True,
        help="Directory containing original Python scripts",
    )
    parser.add_argument(
        "--obfuscated_folder",
        type=Path,
        required=True,
        help="Directory containing obfuscated Python scripts",
    )
    parser.add_argument(
        "--input_folder", type=Path, help="Directory containing input files"
    )
    parser.add_argument(
        "--output_folder", type=Path, help="Directory containing expected output files"
    )

    args = parser.parse_args()

    # Validate directories
    required_dirs = [args.original_folder, args.obfuscated_folder]
    if args.input_folder:
        required_dirs.extend([args.input_folder, args.output_folder])

    validate_directories(FILE_NAME, *required_dirs)
    main(args)
