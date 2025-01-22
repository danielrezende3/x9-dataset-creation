import argparse
import subprocess
from pathlib import Path

import python_minifier
import python_obfuscator
from python_obfuscator.techniques import add_random_variables, one_liner
from tqdm import tqdm
from utils import get_files_from_folder, log_error

FILE_NAME = Path(__file__).stem


class Obfuscator:
    def __init__(
        self,
        original_folder: Path,
        obfuscated_folder: Path,
        method: str,
        include_original: bool,
    ):
        self.original_folder = original_folder
        self.obfuscated_folder = obfuscated_folder
        self.files = get_files_from_folder(original_folder)
        self.method = method
        self.include_original = include_original

    def obfuscate_files(self):
        for file in tqdm(self.files):
            self.__obfuscate_file(file)

    def __obfuscate_file(self, file: Path):
        with open(file, "r") as f:
            original_code = f.read()

        # Depending on the selected method, call the appropriate function
        if self.method == "python_obfuscator":
            obfuscated_code = self.__python_obfuscator_output(original_code)
            output_suffix = "_obfuscated"
        elif self.method == "python_minifier":
            obfuscated_code = self.__python_minifier_output(original_code)
            output_suffix = "_minified"
        elif self.method == "pyminifier":
            obfuscated_code = self.__pyminifier_output(file)
            output_suffix = "_pyminified"
        else:
            log_error(FILE_NAME, f"Unknown method: {self.method}")

        # Save the obfuscated file
        new_file_path = f"{file.stem}{output_suffix}{file.suffix}"
        obfuscated_file_path = self.obfuscated_folder / new_file_path
        with open(obfuscated_file_path, "w") as f:
            f.write(obfuscated_code)

        # (optional) Save the original file
        if self.include_original:
            original_file_path = self.obfuscated_folder / file.name
            with open(original_file_path, "w") as f:
                f.write(original_code)

    def __python_obfuscator_output(self, code: str):
        # ! This is giving me multiple errors
        obfuscator = python_obfuscator.obfuscator()
        return obfuscator.obfuscate(
            code, remove_techniques=[add_random_variables, one_liner]
        )

    def __python_minifier_output(self, code: str):
        return python_minifier.minify(code, remove_literal_statements=True)

    def __pyminifier_output(self, file: Path):
        return subprocess.run(
            ["pyminifier", "-O", file], capture_output=True, text=True
        ).stdout


def main(
    original_folder: Path,
    obfuscated_folder: Path,
    method: str,
    include_original: bool,
):
    obfuscator = Obfuscator(
        original_folder, obfuscated_folder, method, include_original
    )
    obfuscator.obfuscate_files()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Obfuscate the files and save them in the obfuscated folder"
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
        help="The path to the folder where the obfuscated files will be saved",
    )
    parser.add_argument(
        "--method",
        type=str,
        help="Obfuscator used, available: 'python_minifier', 'python_obfuscator', 'pyminifier'",
    )
    parser.add_argument(
        "--include_original",
        action="store_true",
        help="Include the original files in the output folder",
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
            f"The path '{obfuscated_folder}' does not exist or is not a directory.",
        )

    if args.method not in ["python_minifier", "python_obfuscator", "pyminifier"]:
        log_error(
            FILE_NAME,
            "--method unavailable, try one of these: 'python_minifier', 'python_obfuscator', 'pyminifier'",
        )

    method = args.method
    include_original = args.include_original
    main(original_folder, obfuscated_folder, method, include_original)
