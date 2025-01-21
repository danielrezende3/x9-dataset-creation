from pathlib import Path
import python_minifier
from utils import get_files_from_folder

DATA_SET_ORIGINAL_FOLDER = Path("./dataset/original")
DATA_SET_OBFUSCATED_FOLDER = Path("./dataset/python_minifier")


def minifie_file(file):
    with open(f"{DATA_SET_ORIGINAL_FOLDER}/{file}", "r") as f:
        code = f.read()
    minified_code = python_minifier.minify(code, remove_literal_statements=True)
    stem, suffix = file.split(".")
    with open(f"{DATA_SET_OBFUSCATED_FOLDER}/{stem}_minified.{suffix}", "w") as f:
        f.write(minified_code)


def minifie_files(files):
    for file in files:
        minifie_file(file)


def main():
    files = get_files_from_folder(DATA_SET_ORIGINAL_FOLDER)
    minifie_files(files)


if __name__ == "__main__":
    main()
