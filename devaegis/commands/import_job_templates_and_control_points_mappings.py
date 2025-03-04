import csv
import os

import psycopg2

DB_PARAMS = {
    "host": "aws-0-ap-southeast-1.pooler.supabase.com",
    "user": "postgres.lqdjinscrjzvkmrjpzcu",
    "port": "5432",
    "dbname": "postgres",
    "password": "2awcRcXEdLVgbR4",
}

DATA_JOBS_FILE_PATH = os.path.join(
    os.getcwd(),
    "devaegis_backend",
    "commands",
    "data",
    "JobsTemplates.csv",
)

DATA_CONTROL_POINTS_TO_JOBS_MAPPINGS = os.path.join(
    os.getcwd(),
    "devaegis_backend",
    "commands",
    "data",
    "ControlPoint2Jobs.csv",
)


def parse_csv(file_path):
    with open(file_path, mode="r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        data = list(reader)

    print(f"CSV parsed - {file_path}")
    return data


def create_and_cleanse_tables():
    # Connect to PostgreSQL
    conn = psycopg2.connect(**DB_PARAMS)
    with conn.cursor() as cur:
        # Create table is not exist
        cur.execute(
            "CREATE TABLE IF NOT EXISTS job_templates (id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), job_name VARCHAR(255),job_path VARCHAR(255),job_description TEXT,job_script TEXT);"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS control_to_job_templates (control_id UUID NOT NULL, job_template_id UUID NOT NULL, PRIMARY KEY (control_id, job_template_id), FOREIGN KEY (control_id) REFERENCES devaegis_compliance_control(id), FOREIGN KEY (job_template_id) REFERENCES job_templates(id));"
        )
        cur.execute("DELETE FROM job_templates;")
        cur.execute("DELETE FROM control_to_job_templates;")
        conn.commit()

    print("Table creation completed.")


def insert_jobs(jobs_list):
    # Connect to PostgreSQL
    conn = psycopg2.connect(**DB_PARAMS)
    with conn.cursor() as cur:
        # Insert records
        for job in jobs_list:
            cur.execute(
                "INSERT INTO job_templates (job_name, job_path, job_description, job_script) VALUES (%s, %s, %s, %s);",
                (job["Job Name"], job["Path"], job["Description"], job["Script"]),
            )
        conn.commit()

    print("Job data creation completed.")


def insert_mappings(mappings_list):
    # Connect to PostgreSQL
    conn = psycopg2.connect(**DB_PARAMS)
    with conn.cursor() as cur:
        # Insert records
        for mapping in mappings_list:
            control_name = mapping["Control Point"]
            job_name = mapping["Job Name"]
            job_path = mapping["Path"]

            cur.execute(
                "SELECT id FROM devaegis_compliance_control WHERE title = %s;",
                (control_name,),
            )
            control_id = cur.fetchone()

            cur.execute(
                "SELECT id FROM job_templates WHERE job_name = %s AND job_path = %s;",
                (job_name, job_path),
            )
            job_id = cur.fetchone()

            cur.execute(
                "INSERT INTO control_to_job_templates (control_id, job_template_id) VALUES (%s, %s);",
                (control_id, job_id),
            )
        conn.commit()

    print("Mapping data creation completed.")


def import_job_templates_and_control_points_mapping():
    jobs_list = parse_csv(DATA_JOBS_FILE_PATH)
    control_points_to_jobs = parse_csv(DATA_CONTROL_POINTS_TO_JOBS_MAPPINGS)
    create_and_cleanse_tables()
    insert_jobs(jobs_list)
    insert_mappings(control_points_to_jobs)
    print("Update completed.")


if __name__ == "__main__":
    import_job_templates_and_control_points_mapping()
