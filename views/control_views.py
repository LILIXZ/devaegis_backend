import psycopg2
from flask import Blueprint, current_app, jsonify, make_response, request

blueprint = Blueprint("control_views", __name__)


@blueprint.route("/", methods=["POST"])
def filter_for_templates():
    """
    Find all the templates related with specific control points
    """
    auth_header = request.headers.get("Authorization")
    if auth_header != current_app.config["AUTH_TOKEN"]:
        return make_response(jsonify({"details": "Permission denied."}), 401)

    control_point = request.form.get("control_point")

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

    # Retrieve the FAISS index
    cursor.execute(
        "SELECT job_name, job_path, job_description, job_script FROM job_templates T0 "
        "INNER JOIN control_to_job_templates T1 ON T0.id = T1.job_template_id "
        "INNER JOIN devaegis_compliance_control T2 ON T1.control_id = T2.id "
        "WHERE T2.title = %s;",
        (control_point,),
    )
    rows = cursor.fetchall()

    # Close connection
    cursor.close()
    conn.close()

    result = [
        {
            "job_name": row[0],
            "job_path": row[1],
            "job_description": row[2],
            "job_script": row[3],
        }
        for row in rows
    ]

    return make_response(jsonify(result), 200)
