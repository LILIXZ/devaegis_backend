import logging

import psycopg2
from flask import Blueprint, current_app, jsonify, make_response, request
from sqlalchemy import text

from utils.search_utils import retrieve_relevant_template_with_project_info

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

    print("INPUT CONTROL POINTS", control_points)
    print("INPUT PROJECT INFO", project_info)
    logger.info("INFO INPUT CONTROL POINTS: " + control_points.__str__())
    logger.info("INFO INPUT PROJECT INFO: " + project_info)
    logger.debug("DEBUG INPUT CONTROL POINTS: " + control_points.__str__())
    logger.debug("DEBUG INPUT PROJECT INFO: " + project_info)

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

    result = []

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

        template_list = [
            {
                "job_script": row[3],
            }
            for row in rows
        ]

        matched_template = retrieve_relevant_template_with_project_info(
            template_list, project_info
        )
        result.append(matched_template)

    # Close connection
    cursor.close()
    conn.close()

    return make_response(jsonify(result), 200)
