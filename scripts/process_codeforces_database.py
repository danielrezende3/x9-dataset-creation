import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


class DatabaseConnector:
    def __init__(self):
        load_dotenv()  # Load environment variables from a .env file
        self.db_user = os.getenv("DB_USER")
        self.db_password = os.getenv("DB_PASSWORD")
        self.db_host = os.getenv("DB_HOST")
        self._validate_credentials()
        self.engine = self._create_engine()

    def _validate_credentials(self):
        if not self.db_user or not self.db_password:
            raise ValueError(
                "Environment variables DB_USER or DB_PASSWORD are not set!"
            )

    def _create_engine(self):
        return create_engine(
            f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}/code4bench"
        )

    def execute_query(self, query, params=None):
        with self.engine.connect() as connection:
            result = connection.execute(query, params or {})
            return result.fetchall()


class DataProcessor:
    @staticmethod
    def define_problem(row):
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
        return {
            "problems_id": row[0],
            "isValid": row[1],
            "expectedresult": row[2],
            "inputdata": row[3],
        }

    @staticmethod
    def clean_str(s: str) -> str:
        return s.strip().replace("\r\r\n", "\n")


class FileHandler:
    @staticmethod
    def save_code_to_file(problem_id, source_code, base_path="./dataset/codeforces"):
        os.makedirs(base_path, exist_ok=True)
        with open(f"{base_path}/problem_{problem_id}.py", "w") as f:
            f.write(DataProcessor.clean_str(source_code))

    @staticmethod
    def save_test_case_to_file(
        problem_id,
        input_data,
        expected_result,
        id,
    ):
        input_path = "./dataset/codeforces_input"
        output_path = "./dataset/codeforces_output"
        os.makedirs(input_path, exist_ok=True)
        os.makedirs(output_path, exist_ok=True)

        with open(f"{input_path}/problem_{problem_id}.in_{id}", "w") as f:
            f.write(DataProcessor.clean_str(input_data))
        with open(
            f"{output_path}/problem_{problem_id}.out_{id}",
            "w",
        ) as f:
            f.write(DataProcessor.clean_str(expected_result))


def main():
    db_connector = DatabaseConnector()
    data_processor = DataProcessor()
    file_handler = FileHandler()

    # Define the SQL query to fetch problems
    problem_query = text("""
    SELECT *
    FROM source s1
    WHERE id IN (
        SELECT MIN(id)
        FROM source s2
        WHERE languages_id = 8 AND verdicts_id = 1
        GROUP BY problems_id
    )
    LIMIT 100;
    """)

    # Execute the query and fetch results
    problem_rows = db_connector.execute_query(problem_query)
    list_problems = [data_processor.define_problem(row) for row in problem_rows]
    list_problems_id = [problem["problems_id"] for problem in list_problems]

    # Define the SQL query to fetch test cases
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

    # Execute the query and fetch results
    testcase_rows = db_connector.execute_query(
        testcase_query, {"problem_ids": tuple(list_problems_id)}
    )
    testcase_rows_formatted = [
        data_processor.define_test_case(row) for row in testcase_rows
    ]

    # Save source code to files
    for problem in list_problems:
        file_handler.save_code_to_file(problem["problems_id"], problem["sourceCode"])

    # Save test cases to files
    for id, testcase in enumerate(testcase_rows_formatted):
        test_id = id % 3 + 1
        file_handler.save_test_case_to_file(
            testcase["problems_id"],
            testcase["inputdata"],
            testcase["expectedresult"],
            test_id,
        )


if __name__ == "__main__":
    main()
