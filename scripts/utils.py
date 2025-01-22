from os import listdir
from os.path import isfile, join
from pathlib import Path
from typing import NoReturn

EXCLUDE_FROM_LIST = ["problem_145.py", "problem_187.py"]


def log_error(file_name, message: str) -> NoReturn:
    print(f"{file_name}: error: {message}")
    exit(1)


def get_files_from_folder(folder: Path) -> list[Path]:
    return [
        Path(folder) / f
        for f in listdir(folder)
        if isfile(join(folder, f)) and f not in EXCLUDE_FROM_LIST
    ]
