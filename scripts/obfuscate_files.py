import subprocess
import argparse
from pathlib import Path
import python_obfuscator
from python_obfuscator.techniques import add_random_variables, one_liner
import python_minifier
from utils import get_files_from_folder
from pyminifier.obfuscate import apply_obfuscation, obfuscation_machine


class Obfuscator:
    def __init__(self, original_folder: Path, obfuscated_folder: Path, method: str):
        self.original_folder = original_folder
        self.obfuscated_folder = obfuscated_folder
        self.files = get_files_from_folder(original_folder)
        self.method = method  # Store the method

    def obfuscate_files(self):
        for file in self.files:
            self.__obfuscate_file(file)

    def __python_obfuscator_output(self, code: str):
        obfuscator = python_obfuscator.obfuscator()
        return obfuscator.obfuscate(
            code, remove_techniques=[add_random_variables, one_liner]
        )

    def __python_minifier_output(self, code: str):
        return python_minifier.minify(code, remove_literal_statements=True)

    def __pyminifier_output(self, file: Path):
        return subprocess.run(
            ["pyminifier", file], capture_output=True, text=True
        ).stdout

    def __obfuscate_file(self, file: Path):
        # Read the original file
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
            raise ValueError(f"Unknown method: {self.method}")
        # Save the obfuscated file
        obfuscated_file_path = (
            self.obfuscated_folder / f"{file.stem}{output_suffix}{file.suffix}"
        )
        with open(obfuscated_file_path, "w") as f:
            f.write(obfuscated_code)

        # Save the original file in the obfuscated folder (optional)
        original_file_path = self.obfuscated_folder / file.name
        with open(original_file_path, "w") as f:
            f.write(original_code)


def main(original_folder: Path, obfuscated_folder: Path, method: str):
    obfuscator = Obfuscator(original_folder, obfuscated_folder, method)
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

    args = parser.parse_args()

    original_arg = args.original_folder
    obfuscated_arg = args.obfuscated_folder

    # Check that they are non-empty strings
    if not original_arg or not isinstance(original_arg, str):
        print(
            "compute_score.py: error: --original_folder must be a valid non-empty string."
        )
        exit(1)

    if not obfuscated_arg or not isinstance(obfuscated_arg, str):
        print(
            "compute_score.py: error: --obfuscated_folder must be a valid non-empty string."
        )
        exit(1)

    # Create the Path objects
    original_folder = Path(original_arg)
    obfuscated_folder = Path(obfuscated_arg)

    # Now check if they exist and are directories
    if not original_folder.is_dir():
        print(
            f"compute_score.py: error: The path '{original_folder}' does not exist or is not a directory."
        )
        exit(1)

    if not obfuscated_folder.is_dir():
        print(
            f"compute_score.py: error: The path '{obfuscated_folder}' does not exist or is not a directory."
        )
        exit(1)

    if args.method not in ["python_minifier", "python_obfuscator", "pyminifier"]:
        print(
            "compute_score.py: error: --method unavailable, try one of these: 'python_minifier', 'python_obfuscator', 'pyminifier'"
        )
        exit(1)

    method = args.method
    main(original_folder, obfuscated_folder, method)
