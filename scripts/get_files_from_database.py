import argparse
import logging
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Configure logging
LOG_DIR = "./logs"
FILE_NAME = Path(__file__).stem
os.makedirs(LOG_DIR, exist_ok=True)
log_filename = os.path.join(
    LOG_DIR, datetime.now().strftime(f"{FILE_NAME}_%Y-%m-%d_%H_%M_%S.log")
)
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format=f"{FILE_NAME} %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

Lang_to_ID = {
    "C": 1,
    "PYTHON": 8,
    "GNU_C": 12,
}


class DatabaseConnector:
    """Database connector for MySQL using SQLAlchemy."""

    def __init__(self):
        logger.info("Initializing DatabaseConnector")
        load_dotenv()  # Load environment variables from a .env file
        self.db_user = os.getenv("DB_USER")
        self.db_password = os.getenv("DB_PASSWORD")
        self.db_host = os.getenv("DB_HOST")
        self._validate_credentials()
        self.engine = self._create_engine()
        logger.info("Database engine created successfully.")

    def _validate_credentials(self):
        if not self.db_user or not self.db_password:
            logger.error("Environment variables DB_USER or DB_PASSWORD are not set!")
            raise ValueError(
                "Environment variables DB_USER or DB_PASSWORD are not set!"
            )

    def _create_engine(self):
        return create_engine(
            f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}/code4bench"
        )

    def execute_query(self, query, params=None):
        logger.info(f"Executing query: {query}")
        with self.engine.connect() as connection:
            result = connection.execute(query, params or {})
            rows = result.fetchall()
            logger.info(f"Query executed successfully. Fetched {len(rows)} rows.")
            return rows


class DataProcessor:
    """Processes database rows into structured dictionaries for problems and test cases."""

    @staticmethod
    def define_problem(row):
        """
        Convert a database row into a problem dictionary.
        """
        return {
            "id": row[0],
            "submission": row[1],
            "sourceCode": row[2],
            "author": row[3],
            "memory": row[4],
            "time": row[5],
            "sent": row[6],
            "countline": row[7],
            "problems_id": row[8],
            "verdicts_id": row[9],
            "languages_id": row[10],
            "isDuplicate": row[11],
        }

    @staticmethod
    def define_test_case(row):
        """
        Convert a database row into a test case dictionary.
        """
        return {
            "problems_id": row[0],
            "isValid": row[1],
            "expectedresult": row[2],
            "inputdata": row[3],
        }

    @staticmethod
    def clean_str(s: str) -> str:
        """
        Clean and normalize a string.
        """
        return s.strip().replace("\r\r\n", "\n")


class FileHandler:
    """Handles saving source code and test case files to disk."""

    def __init__(self, base_path: str, language: str):
        """
        Initialize the file handler.
        """
        self.base_path = base_path
        self.input_path = f"{base_path}_input"
        self.output_path = f"{base_path}_output"
        self.language = language.upper()
        logger.info(f"FileHandler initialized for language: {self.language}")

    def save_code_to_file(self, problem_id, source_code):
        """
        Save the source code of a problem to a file.
        """
        os.makedirs(self.base_path, exist_ok=True)
        cleaned_code = DataProcessor.clean_str(source_code)

        if self.language == "C":
            file_extension = "c"
        elif self.language == "PYTHON":
            file_extension = "py"
        else:
            logger.error("Invalid language. Choose between 'C' and 'PYTHON'.")
            raise ValueError("Invalid language. Choose between 'C' and 'PYTHON'.")

        file_path = os.path.join(
            self.base_path, f"problem_{problem_id}.{file_extension}"
        )
        with open(file_path, "w") as f:
            f.write(cleaned_code)
        logger.info(f"Saved source code for problem {problem_id} to {file_path}")

    def save_test_case_to_file(self, problem_id, input_data, expected_result, test_id):
        """
        Save a test case's input and expected output to separate files.
        """
        os.makedirs(self.input_path, exist_ok=True)
        os.makedirs(self.output_path, exist_ok=True)

        input_file_path = os.path.join(
            self.input_path, f"problem_{problem_id}.in_{test_id}"
        )
        output_file_path = os.path.join(
            self.output_path, f"problem_{problem_id}.out_{test_id}"
        )

        with open(input_file_path, "w") as f:
            f.write(DataProcessor.clean_str(input_data))
        with open(output_file_path, "w") as f:
            f.write(DataProcessor.clean_str(expected_result))
        logger.info(f"Saved test case {test_id} for problem {problem_id}.")


def process_problems(folder_path: str, language: str, save: bool) -> list[int]:
    """
    Fetch problems from the database and optionally save their source code files.
    """
    logger.info("Processing problems...")
    db_connector = DatabaseConnector()
    data_processor = DataProcessor()

    problem_query = text("""
    SELECT *
    FROM source s1
    WHERE id IN (
        SELECT MIN(id)
        FROM source s2
        WHERE languages_id = :language_ID AND verdicts_id = 1
        GROUP BY problems_id
    )
    LIMIT 100;
    """)

    problem_rows = db_connector.execute_query(
        problem_query, {"language_ID": Lang_to_ID[language.upper()]}
    )
    problems = [data_processor.define_problem(row) for row in problem_rows]
    problem_ids = [problem["problems_id"] for problem in problems]
    logger.info(f"Fetched {len(problem_ids)} problem IDs.")

    if save:
        file_handler = FileHandler(folder_path, language)
        for problem in problems:
            file_handler.save_code_to_file(
                problem["problems_id"], problem["sourceCode"]
            )

    return problem_ids


def process_test_cases(
    folder_path: str, language: str, problem_ids: list[int], save: bool
) -> None:
    """
    Fetch test cases for the given problem IDs and optionally save them to files.
    """
    if not problem_ids:
        logger.info("No problem IDs provided. Skipping test case processing.")
        return

    logger.info("Processing test cases...")
    db_connector = DatabaseConnector()
    data_processor = DataProcessor()

    testcase_query = text("""
    WITH RankedTestcases AS (
        SELECT 
            problems_id,
            isValid,
            expectedresult,  
            inputdata,       
            ROW_NUMBER() OVER (PARTITION BY problems_id ORDER BY id) AS row_num
        FROM testcases
        WHERE problems_id IN :problem_ids
    )
    SELECT problems_id, isValid, expectedresult, inputdata
    FROM RankedTestcases
    WHERE row_num <= 3;
    """)

    testcase_rows = db_connector.execute_query(
        testcase_query, {"problem_ids": tuple(problem_ids)}
    )
    testcases = [data_processor.define_test_case(row) for row in testcase_rows]
    logger.info(
        f"Fetched test cases for {len(set([tc['problems_id'] for tc in testcases]))} problems."
    )

    if save:
        file_handler = FileHandler(folder_path, language)
        # Group test cases by problem to correctly assign test IDs (e.g., 1, 2, 3)
        grouped_testcases = defaultdict(list)
        for testcase in testcases:
            grouped_testcases[testcase["problems_id"]].append(testcase)

        for problem_id, tcs in grouped_testcases.items():
            for index, testcase in enumerate(tcs, start=1):
                file_handler.save_test_case_to_file(
                    problem_id, testcase["inputdata"], testcase["expectedresult"], index
                )


def main(
    folder_path: str, language: str, is_save_problems: bool, is_save_testcases: bool
):
    """
    Main function to process and optionally save problem source code files and test case files.
    """
    logger.info("Starting main process...")
    # Process problems regardless, as test case retrieval requires problem IDs.
    problem_ids = process_problems(folder_path, language, save=is_save_problems)

    if is_save_testcases:
        process_test_cases(folder_path, language, problem_ids, save=True)
    logger.info("Process completed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process problems and test cases from the database and optionally save them as files."
    )
    parser.add_argument(
        "--folder",
        type=str,
        required=True,
        help="Base folder path for saving files.",
    )
    parser.add_argument(
        "--language",
        type=str,
        required=True,
        help="Programming language (e.g., C, PYTHON).",
    )
    parser.add_argument(
        "--problems", action="store_true", help="Save problem source code files."
    )
    parser.add_argument(
        "--testcases", action="store_true", help="Save test case files."
    )

    args = parser.parse_args()

    folder_path = args.folder
    language = args.language

    # If neither flag is provided, notify the user and exit.
    if not (args.problems or args.testcases):
        logger.error(
            "No saving option selected. Use --problems and/or --testcases to save files."
        )
        print(
            "No saving option selected. Use --problems and/or --testcases to save files."
        )
        exit(1)

    is_save_problems = args.problems
    is_save_testcases = args.testcases

    try:
        main(folder_path, language, is_save_problems, is_save_testcases)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        exit(1)
