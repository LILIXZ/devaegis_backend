import click
from flask import current_app
from flask.cli import with_appcontext
from sqlalchemy import create_engine, text


@click.command(name="database_healthcheck")
@with_appcontext
def database_healthcheck():
    db_cons = current_app.config["SQLALCHEMY_BINDS"]
    for con_name, con_uri in db_cons.items():
        try:
            e = create_engine(con_uri).connect()
            _ = e.execute(text("select 1"))
            print(f"CONNECTION [{con_name}]: CONNECTED")
        except Exception as inst:
            print(f"CONNECTION [{con_name}]: NOT CONNECTED - {inst}")
