import argparse
from datetime import datetime
import logging
import os
import subprocess
from pathlib import Path

import python_minifier
import python_obfuscator
from dotenv import load_dotenv
from python_obfuscator.techniques import add_random_variables, one_liner
import requests
from tqdm import tqdm
from utils import (
    get_files_from_folder,
    log_error,
    validate_directories,
)


# Constants -------------------------------------------------------------------
API_URL = "https://picheta.me/obfuscator/obfuscate"
FILE_NAME = Path(__file__).stem
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
        logger.info(
            f"Starting obfuscation of {len(self.files)} file(s) using method '{self.method}'"
        )
        if self.method == "tigress":
            for file in tqdm(self.files, desc="Obfuscating files"):
                if file.suffix in [".py", ".c"]:
                    logger.info(f"Obfuscating file {file} using Tigress")
                    self.__tigress_output(file)
                else:
                    logger.warning(
                        f"Skipping file {file} as it is not a Python or C file"
                    )
        else:
            for file in tqdm(self.files, desc="Obfuscating files"):
                if file.suffix in [".py", ".c"]:
                    logger.info(f"Obfuscating file {file} using method '{self.method}'")
                    self.__obfuscate_file(file)
                else:
                    logger.warning(
                        f"Skipping file {file} as it is not a Python or C file"
                    )

    def __get_obfuscated_code_and_suffix(
        self, original_code: str, file: Path
    ) -> tuple[str, str]:
        """
        Based on the specified method, produce and return the obfuscated code and the appropriate file suffix.

        :param original_code: The original file contents.
        :param file: Path to the file being obfuscated.
        :return: A tuple containing (obfuscated_code, file_suffix).
        """
        logger.info(f"Obfuscating {file} using method '{self.method}'")
        if self.method == "python_obfuscator":
            obfuscated_code = self.__python_obfuscator_output(original_code)
            output_suffix = "_obfuscated"
        elif self.method == "python_minifier":
            obfuscated_code = self.__python_minifier_output(original_code)
            output_suffix = "_minified"
        elif self.method == "pyminifier":
            obfuscated_code = self.__pyminifier_output(file)
            output_suffix = "_pyminified"
        elif self.method == "picheta":
            obfuscated_code = self.__picheta_output(original_code)
            output_suffix = "_picheta"
        else:
            logger.error(f"Unknown method specified: {self.method}")
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
            logger.error(f"Error reading file {file}")
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
            logger.error(f"Error writing obfuscated file {obfuscated_file_path}")
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
                logger.error(f"Error writing original file {original_file_path}")
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
            ["pyminifier", "-O", str(file)], capture_output=True, text=True
        )
        return result.stdout

    def __picheta_output(self, code: str) -> str:
        """
        :param c_code: The C code to be obfuscated.
        :type c_code: str
        :param code_name: The original name of the C code to name the obfuscated file.
        :type code_name: str
        :return: The obfuscated C code, or an empty string if an error occurs.
        :rtype: str
        """
        code = code.replace("\n", "\\n")
        headers = {"Content-Type": "application/json"}
        payload = {"code": code, "language": "c", "rename": True}

        try:
            response = requests.post(API_URL, headers=headers, json=payload)
        except Exception as error:
            logger.error(f"Error during API request: {error}")
            return ""

        if response.status_code != 200:
            logger.error(f"API request failed with status code: {response.status_code}")
            return ""

        try:
            result = response.json()
        except ValueError as error:
            logger.error(f"Error decoding JSON response: {error}")
            return ""

        if not result.get("success", False):
            logger.error(f"Obfuscation failed: {result.get('log')}")
            return ""

        return result.get("code", "")

    def __tigress_output(self, file: Path) -> None:
        """Use Tigress via subprocess to obfuscate the code."""
        # Build output file name
        if self.include_suffix:
            new_file_name = f"{file.stem}_tigress{file.suffix}"
        else:
            new_file_name = f"{file.stem}{file.suffix}"

        obfuscated_file_path = self.obfuscated_folder / new_file_name

        tigress_command = self.__build_tigress_command(file, obfuscated_file_path)

        try:
            subprocess.run(tigress_command, check=True, capture_output=True, text=True)
            if (
                not obfuscated_file_path.exists()
                or obfuscated_file_path.stat().st_size == 0
            ):
                logger.error(
                    f"Tigress output file is empty for {file}. Removing empty file."
                )
                os.remove(obfuscated_file_path)
            else:
                logger.info(
                    f"Tigress obfuscation completed for {file}, output saved to {obfuscated_file_path}"
                )
        except subprocess.CalledProcessError as e:
            logger.error(f"Error obfuscating file {file} with Tigress: {e}")

        # Optionally save the original file
        if self.include_original:
            original_file_path = self.obfuscated_folder / file.name
            try:
                # Read the original file content to save it
                with open(file, "r") as original:
                    original_code = original.read()
                with open(original_file_path, "w") as f:
                    f.write(original_code)
                logger.info(f"Original file saved to {original_file_path}")
            except OSError as e:
                logger.error(f"Error writing original file {original_file_path}: {e}")
                log_error(
                    FILE_NAME, f"Error writing original file {original_file_path}"
                )

    @staticmethod
    def __build_tigress_command(temp_input_file: Path, output_file: Path) -> list[str]:
        """
        :param temp_input_file: The path to the temporary C file.
        :type temp_input_file: str
        :param output_file: The path where the obfuscated C file will be saved.
        :type output_file: str
        :return: The Tigress command as a list of arguments.
        :rtype: list[str]
        """
        return [
            "tigress",
            "--Seed=42",
            "--Statistics=0",
            "--Verbosity=0",
            "--Transform=InitEntropy",
            "--Functions=*",
            "--InitEntropyKinds=vars",
            "--Transform=InitBranchFuns",
            "--InitBranchFunsCount=1",
            "--Transform=AntiBranchAnalysis",
            "--Functions=*",
            "--AntiBranchAnalysisKinds=branchFuns",
            "--AntiBranchAnalysisObfuscateBranchFunCall=false",
            "--AntiBranchAnalysisBranchFunFlatten=true",
            "--Transform=EncodeArithmetic",
            "--Functions=*",
            str(temp_input_file),
            f"--out={output_file}",
        ]


def main(config: argparse.Namespace) -> None:
    """
    Main function to create an Obfuscator instance and run the obfuscation process.

    :param original_folder: The path to the folder containing original files.
    :param obfuscated_folder: The path to the folder where obfuscated files will be saved.
    :param method: The obfuscation method to use.
    :param include_original: Whether to also include original files in the output folder.
    :param include_suffix: Whether to add a suffix to the obfuscated file names.
    """
    logger.info(
        f"Starting obfuscation process with configuration: original_folder={config.original_folder}, "
        f"obfuscated_folder={config.obfuscated_folder}, method={config.method}, "
        f"include_original={config.include_original}, include_suffix={config.include_suffix}"
    )
    obfuscator = Obfuscator(
        config.original_folder,
        config.obfuscated_folder,
        config.method,
        config.include_original,
        config.include_suffix,
    )
    obfuscator.obfuscate_files()

    # log how many files successfully obfuscated
    obfuscated_files = get_files_from_folder(config.obfuscated_folder)
    original_files = get_files_from_folder(config.original_folder)
    msg = f"Obfuscation process completed. ({len(obfuscated_files)}/{len(original_files)})"
    logger.info(msg)
    print(msg)


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
        choices=[
            "python_minifier",
            "python_obfuscator",
            "pyminifier",
            "tigress",
            "picheta",
        ],
        help="Obfuscator to use. Available options: 'python_minifier', 'python_obfuscator', 'pyminifier', 'tigress', 'picheta'",
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
