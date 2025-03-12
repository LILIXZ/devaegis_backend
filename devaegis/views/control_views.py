import logging

import psycopg2
from flask import Blueprint, current_app, jsonify, make_response, request

from devaegis.utils.search_utils import \
    retrieve_relevant_template_with_project_info

blueprint = Blueprint("control_views", __name__)
logger = logging.getLogger(__name__)


@blueprint.route("/", methods=["POST"])
def filter_for_templates():
    """
    Find all the templates related with specific control points
    """
    auth_header = request.headers.get("Authorization")
    if auth_header != current_app.config["AUTH_TOKEN"]:
        return make_response(jsonify({"details": "Permission denied."}), 401)

    control_points = request.json.get("control_points", [])
    project_info = request.json.get("project_info")

    DB_PARAMS = {
        "host": current_app.config["POSTGRES_HOSTNAME"],
        "user": current_app.config["POSTGRES_USER"],
        "port": current_app.config["POSTGRES_PORT"],
        "dbname": current_app.config["POSTGRES_DB"],
        "password": current_app.config["POSTGRES_PASSWORD"],
    }

    # Connect to PostgreSQL
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()

    matched_jobs = []

    for control_point in control_points:
        # Retrieve the job templates
        query = f"""
        SELECT job_name, job_path, job_description, job_script FROM job_templates T0 
        INNER JOIN control_to_job_templates T1 ON T0.id = T1.job_template_id 
        INNER JOIN devaegis_compliance_control T2 ON T1.control_id = T2.id 
        WHERE T2.title = '{control_point}';
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        if len(rows) > 0:
            template_list = [
                {
                    "job_name": row[0],
                    "job_path": row[1],
                    "job_description": row[2],
                }
                for row in rows
            ]

            matched_job = retrieve_relevant_template_with_project_info(
                template_list, project_info
            )
            matched_jobs.append(matched_job)

    result = []

    for job in matched_jobs:
        query = f"""
                SELECT job_script FROM job_templates
                WHERE job_name = '{job['job_name']}' and job_path = '{job['job_path']}';
        """
        cursor.execute(query)
        row = cursor.fetchone()
        result.append(row[0])

    # Close connection
    cursor.close()
    conn.close()

    return make_response(jsonify(result), 200)
