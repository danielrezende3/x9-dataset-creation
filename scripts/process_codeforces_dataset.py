import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# Print the results
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


def clean_str(s: str) -> str:
    return s.strip().replace("\r\r\n", "\n")


def define_test_case(row):
    return {
        "problems_id": row[0],
        "isValid": row[1],
        "expectedresult": row[2],
        "inputdata": row[3],
    }


load_dotenv()  # Load environment variables from a .env file

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
if not db_user or not db_password:
    raise ValueError("Environment variables DB_USER or DB_PASSWORD are not set!")

# Create a database connection using SQLAlchemy
engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/code4bench")

# Define the SQL query
query = text("""
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
with engine.connect() as connection:
    result = connection.execute(query)
    rows = result.fetchall()

list_problems_id = []
list_solution = []
for row in rows:
    dict_row = define_problem(row)
    list_solution.append(dict_row)
    list_problems_id.append(dict_row["problems_id"])

testcase_query = text("""
WITH RankedTestcases AS (
    SELECT 
        problems_id,
        isValid,
        expectedresult,  -- New column
        inputdata,       -- New column
        ROW_NUMBER() OVER (PARTITION BY problems_id ORDER BY id) AS row_num
    FROM testcases
    WHERE problems_id IN :problem_ids
)
SELECT problems_id, isValid, expectedresult, inputdata
FROM RankedTestcases
WHERE row_num <= 3;
""")

with engine.connect() as connection:
    result = connection.execute(
        testcase_query, {"problem_ids": tuple(list_problems_id)}
    )
    testcase_rows = result.fetchall()


testcase_rows_formated = []
for test in testcase_rows:
    testcase_rows_formated.append(define_test_case(test))

for solution in list_solution:
    with open(f"./dataset/codeforces/problem_{solution['problems_id']}.py", "w") as f:
        f.write(clean_str(solution["sourceCode"]))

for id, testcase in enumerate(testcase_rows_formated):
    id = id % 3 + 1
    with open(
        f"./dataset/codeforces_input/problem_{testcase['problems_id']}_{id}.in", "w"
    ) as f:
        f.write(clean_str(testcase["inputdata"]))

    with open(
        f"./dataset/codeforces_output/problem_{testcase['problems_id']}_{id}.out", "w"
    ) as f:
        f.write(clean_str(testcase["expectedresult"]))
