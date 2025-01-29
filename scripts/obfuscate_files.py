import argparse
import subprocess
from pathlib import Path

import python_minifier
import python_obfuscator
from python_obfuscator.techniques import add_random_variables, one_liner
from tqdm import tqdm
from utils import get_files_from_folder, log_error, validate_directories

FILE_NAME = Path(__file__).stem


class Obfuscator:
    """
    A class that handles file obfuscation using different methods.

    :param original_folder: The path to the folder with original files.
    :param obfuscated_folder: The path to the folder for obfuscated files.
    :param method: The obfuscation method to use.
    :param include_original: Whether to include the original file in the output folder.
    :param include_suffix: Whether to add an obfuscation suffix (e.g. '_obfuscated') to the output file name.
    """

    def __init__(
        self,
        original_folder: Path,
        obfuscated_folder: Path,
        method: str,
        include_original: bool,
        include_suffix: bool = False,
    ) -> None:
        self.original_folder = original_folder
        self.obfuscated_folder = obfuscated_folder
        self.files = get_files_from_folder(original_folder)
        self.method = method
        self.include_original = include_original
        self.include_suffix = include_suffix

    def obfuscate_files(self) -> None:
        """
        Obfuscate all files in the original folder and save them to the obfuscated folder.
        """
        for file in tqdm(self.files, desc="Obfuscating files"):
            self.__obfuscate_file(file)

    def __get_obfuscated_code_and_suffix(
        self, original_code: str, file: Path
    ) -> tuple[str, str]:
        """
        Based on the specified method, produce and return the obfuscated code and the appropriate file suffix.

        :param original_code: The original file contents.
        :param file: Path to the file being obfuscated.
        :return: A tuple containing (obfuscated_code, file_suffix).
        """
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
        return obfuscated_code, output_suffix

    def __obfuscate_file(self, file: Path) -> None:
        """
        Obfuscate a single file using the specified method.

        :param file: The file to be obfuscated.
        """
        try:
            with open(file, "r") as f:
                original_code = f.read()
        except OSError:
            log_error(FILE_NAME, f"Error reading file {file}")

            obfuscated_code, output_suffix = self.__get_obfuscated_code_and_suffix(
                original_code, file
            )

            # Build output file name
            if self.include_suffix:
                new_file_name = f"{file.stem}{output_suffix}{file.suffix}"
            else:
                new_file_name = f"{file.stem}{file.suffix}"

            obfuscated_file_path = self.obfuscated_folder / new_file_name
            try:
                with open(obfuscated_file_path, "w") as f:
                    f.write(obfuscated_code)
            except OSError:
                log_error(
                    FILE_NAME,
                    f"Error writing obfuscated file {obfuscated_file_path}",
                )

            # Optionally save the original file
            if self.include_original:
                original_file_path = self.obfuscated_folder / file.name
                try:
                    with open(original_file_path, "w") as f:
                        f.write(original_code)
                except OSError:
                    log_error(
                        FILE_NAME,
                        f"Error writing original file {original_file_path}",
                    )

    def __python_obfuscator_output(self, code: str) -> str:
        """(UNSTABLE) Use python_obfuscator library to obfuscate the code."""
        obfuscator = python_obfuscator.obfuscator()
        return obfuscator.obfuscate(
            code, remove_techniques=[add_random_variables, one_liner]
        )

    def __python_minifier_output(self, code: str) -> str:
        """Use python_minifier library to obfuscate the code."""
        return python_minifier.minify(code, remove_literal_statements=True)

    def __pyminifier_output(self, file: Path) -> str:
        """Use pyminifier via subprocess to obfuscate the code."""
        result = subprocess.run(
            ["pyminifier", "-O", file], capture_output=True, text=True
        )
        return result.stdout


def main(config: argparse.Namespace) -> None:
    """
    Main function to create an Obfuscator instance and run the obfuscation process.

    :param original_folder: The path to the folder containing original files.
    :param obfuscated_folder: The path to the folder where obfuscated files will be saved.
    :param method: The obfuscation method to use.
    :param include_original: Whether to also include original files in the output folder.
    :param include_suffix: Whether to add a suffix to the obfuscated file names.
    """
    obfuscator = Obfuscator(
        config.original_folder,
        config.obfuscated_folder,
        config.method,
        config.include_original,
        config.include_suffix,
    )
    obfuscator.obfuscate_files()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Obfuscate the files and save them in the obfuscated folder"
    )
    parser.add_argument(
        "--original_folder",
        type=Path,
        required=True,
        help="The path to the folder containing the original files",
    )
    parser.add_argument(
        "--obfuscated_folder",
        type=Path,
        required=True,
        help="The path to the folder where the obfuscated files will be saved",
    )
    parser.add_argument(
        "--method",
        type=str,
        required=True,
        choices=["python_minifier", "python_obfuscator", "pyminifier"],
        help="Obfuscator to use. Available options: 'python_minifier', '(UNSTABLE) python_obfuscator', 'pyminifier'",
    )
    parser.add_argument(
        "--include_original",
        action="store_true",
        help="Include the original files in the output folder",
    )
    parser.add_argument(
        "--include_suffix",
        action="store_true",
        help="Add an obfuscation suffix based on the method name (e.g., '_pyminifier') to the output file names",
    )

    args = parser.parse_args()

    original_arg = args.original_folder
    obfuscated_arg = args.obfuscated_folder
    required_dirs = [original_arg, obfuscated_arg]

    # Validate directories
    validate_directories(FILE_NAME, *required_dirs)

    main(args)
