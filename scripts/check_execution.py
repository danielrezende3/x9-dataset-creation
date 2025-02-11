import argparse
import logging
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from dotenv import load_dotenv
from tqdm import tqdm
from utils import (
    get_files_from_folder,
    get_first_folder,
    log_error,
    validate_directories,
)

# Constants -------------------------------------------------------------------
NUM_WORKERS = 1
TIMEOUT_SECONDS = 30
CHUNK_SIZE = 3
FILE_NAME = Path(__file__).stem
PYTHON_EXECUTABLE = os.getenv("PYTHON38_PATH")
if not PYTHON_EXECUTABLE:
    log_error(FILE_NAME, "PYTHON38_PATH environment variable is not set.")
C_COMPILER = os.getenv("GCC_PATH", "gcc")

# Logging setup ---------------------------------------------------------------
LOG_DIR = "logs"
load_dotenv()
os.makedirs(LOG_DIR, exist_ok=True)
log_filename = os.path.join(
    LOG_DIR, datetime.now().strftime(f"{FILE_NAME}_%Y-%m-%d_%H_%M_%S.log")
)
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format=f"{FILE_NAME} %(levelname)s: %(message)s",
)
logger = logging.getLogger()

# Helper Functions for Execution ----------------------------------------------


def run_python_script(file_path: Path, input_data: str = "100") -> str:
    """Execute a Python script and return its stdout.

    :param file_path: Path to the Python script to execute
    :param input_data: Input to pass to the script via stdin
    :returns: Captured stdout from the script execution
    :raises RuntimeError: If execution times out or encounters an error
    """
    try:
        result = subprocess.run(
            [str(PYTHON_EXECUTABLE), str(file_path)],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Script {file_path} exited with return code {result.returncode}: {result.stderr}"
            )
        return result.stdout
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(f"Timeout expired for {file_path}") from e
    except Exception as e:
        raise RuntimeError(f"Error executing {file_path}") from e


def compile_c_file(c_file: Path) -> Path:
    """
    Compile a C source file using GCC and return the path to the compiled executable.
    The executable will be created in the same directory with the same base name.
    """
    exe_path = c_file.with_suffix("")  # remove .c extension
    try:
        compile_result = subprocess.run(
            [C_COMPILER, str(c_file), "-o", str(exe_path), "-lm"],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            check=True,
        )
        return exe_path
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Compilation failed for {c_file}: {e.stderr}")
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(f"Compilation timed out for {c_file}") from e


def run_c_executable(exe_file: Path, input_data: str = "100") -> str:
    """Execute a compiled C executable and return its stdout."""
    try:
        result = subprocess.run(
            [str(exe_file)],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Executable {exe_file} exited with code {result.returncode}: {result.stderr}"
            )
        return result.stdout
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(f"Execution timed out for {exe_file}") from e
    except Exception as e:
        raise RuntimeError(f"Error executing {exe_file}: {e}") from e


def run_code(file_path: Path, input_data: str = "100") -> str:
    """
    Execute code based on file extension.

    - For Python (.py) files, run using the Python interpreter.
    - For C (.c) files, compile with GCC and run the resulting binary.
    """
    if file_path.suffix == ".py":
        return run_python_script(file_path, input_data)
    elif file_path.suffix == ".c":
        # Check if the executable already exists
        exe_file = file_path.with_suffix("")
        if not exe_file.exists():
            logger.info(f"Compiling {file_path}")
            exe_file = compile_c_file(file_path)
        return run_c_executable(exe_file, input_data)
    else:
        raise RuntimeError(f"Unsupported file type: {file_path.suffix}")


# Comparison and Task Management ---------------------------------------------


def compare_files(
    file1: Path,
    file2: Path,
    input_data: Optional[tuple[str, str]] = None,
    expected_output: Optional[tuple[str, str]] = None,
) -> bool:
    """
    Compare outputs of two scripts (either Python or C) with optional input and expected output validation.

    :param file1: Path to the first script.
    :param file2: Path to the second script.
    :param input_data: Optional input tuple (input string, problem identifier).
    :param expected_output: Optional expected output tuple (expected string, problem identifier).
    :returns: True if both scripts produce matching output, else False.
    """
    input_val = input_data[0] if input_data else "100"
    problem_id = input_data[1] if input_data else ""
    try:
        stdout1 = run_code(file1, input_val).strip()
        stdout2 = run_code(file2, input_val).strip()

        if stdout1 == stdout2:
            part = f"for {input_data[1].split('.')[1]}" if input_data else ""
            logger.info(
                f"SUCCESS: [{get_first_folder(file1)}/{file1.stem}] == [{get_first_folder(file2)}/{file2.stem}] {part}."
            )
            return True
        else:
            logger.error(
                f"STDOUT_MISMATCH: [{get_first_folder(file1)}/{file1.stem}] and "
                f"[{get_first_folder(file2)}/{file2.stem}]: for [{problem_id}]: {repr(stdout1)} != {repr(stdout2)}"
            )
            return False
    except RuntimeError as e:
        logger.error(
            f"RUN_TIME_ERROR: [{get_first_folder(file1)}/{file1.stem}] and "
            f"[{get_first_folder(file2)}/{file2.stem}]: for [{problem_id}]: {e}"
        )
        return False
    except Exception as e:
        logger.error(
            f"UNHANDLED_EXC: [{get_first_folder(file1)}/{file1.stem}] and "
            f"[{get_first_folder(file2)}/{file2.stem}]: for [{problem_id}]: {e}"
        )
        return False


def process_tasks(
    tasks: Iterable[
        Tuple[Path, Path, Optional[tuple[str, str]], Optional[tuple[str, str]]]
    ],
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
    input_contents: List[tuple[str, str]],
    output_contents: List[tuple[str, str]],
) -> List[Tuple[Path, Path, tuple[str, str], tuple[str, str]]]:
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
    original_stems = {file.stem for file in source_files if file.suffix}
    obfuscated_stems = {file.stem for file in reference_files if file.suffix}

    filtered_original_files = [
        file for file in source_files if file.suffix and file.stem in obfuscated_stems
    ]
    filtered_obfuscated_files = [
        file for file in reference_files if file.suffix and file.stem in original_stems
    ]
    removed_original = set(source_files) - set(filtered_original_files)
    removed_obfuscated = set(reference_files) - set(filtered_obfuscated_files)

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
    """Main comparison workflow controller."""
    original_files = get_files_from_folder(config.original_folder)
    obfuscated_files = get_files_from_folder(config.obfuscated_folder)

    # Validate that both folders contain files
    if not original_files:
        log_error(FILE_NAME, f"No files found in {config.original_folder}")
    if not obfuscated_files:
        log_error(FILE_NAME, f"No files found in {config.obfuscated_folder}")

    # Filter files to keep only those with matching stems
    filtered_original_files, filtered_obfuscated_files = filter_matching_files(
        original_files, obfuscated_files
    )
    if not filtered_original_files or not filtered_obfuscated_files:
        log_error(FILE_NAME, "No matching files found after filtering.")

    if config.input_folder:
        input_files = get_files_from_folder(config.input_folder)
        output_files = get_files_from_folder(config.output_folder)
        if not input_files:
            log_error(FILE_NAME, f"No files found in {config.input_folder}")
        if not output_files:
            log_error(FILE_NAME, f"No files found in {config.output_folder}")

        # Additional filtering and validation
        filtered_input_files, filtered_original_files = filter_matching_files(
            input_files, filtered_original_files
        )
        filtered_input_files, filtered_output_files = filter_matching_files(
            filtered_input_files, output_files
        )
        filtered_original_files, filtered_obfuscated_files = filter_matching_files(
            filtered_original_files, filtered_obfuscated_files
        )

        # Ensure consistent lengths
        if len(filtered_original_files) != len(filtered_obfuscated_files):
            log_error(
                FILE_NAME,
                "Mismatch in the number of original and obfuscated files after filtering.",
            )

        input_contents = [(f.read_text(), f.name) for f in filtered_input_files]
        output_contents = [(f.read_text(), f.name) for f in filtered_output_files]

        tasks = setup_tasks_with_io(
            filtered_original_files,
            filtered_obfuscated_files,
            input_contents,
            output_contents,
        )
    else:
        tasks = setup_tasks_simple(filtered_original_files, filtered_obfuscated_files)

    if not tasks:
        log_error(FILE_NAME, "No valid tasks to process after filtering.")

    correct_count = process_tasks(tasks)
    total = len(tasks) if config.input_folder else len(original_files)
    print(f"Correct count: {correct_count}/{total}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compare outputs of original and obfuscated Python/C scripts"
    )
    parser.add_argument(
        "--original_folder",
        type=Path,
        required=True,
        help="Directory containing original scripts (.py or .c)",
    )
    parser.add_argument(
        "--obfuscated_folder",
        type=Path,
        required=True,
        help="Directory containing obfuscated scripts (.py or .c)",
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
