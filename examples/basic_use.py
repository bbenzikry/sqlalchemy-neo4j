import os
import jpype

import sqlalchemy as sqla
from sqlalchemy import create_engine
from sqlalchemy.engine.reflection import Inspector
from urllib.parse import quote


def get_engine(user, password, db="neo4j", host="127.0.0.1:7687"):
    # Note that we're quoting whatever can be problematic for parsing
    # Output url example:
    # neo4j+jdbc://neo4j-neo4j:7687/neo4j?UID=neo4j&PWD=PASSWORD%23&LogLevel=6&StrictlyUseBoltScheme=false
    # pylint: disable=line-too-long
    url = f"neo4j+jdbc://{host}/{quote(db)}?PWD={quote(password)}&UID={quote(user)}&LogLevel=2&StrictlyUseBoltScheme=false"
    eng = create_engine(url)
    return eng


if __name__ == "__main__":
    usr = os.environ["NEOJDBC_USER"]
    pwd = os.environ["NEOJDBC_PASSWORD"]
    host = os.environ["NEOJDBC_HOST"]
    port = os.environ["NEOJDBC_PORT"]

    # This happens automatically if you set the NEOJDBC_WARMUP environment var
    jpype.startJVM()

    # create engine
    engine = get_engine(usr, pwd, "neo4j", f"{host}:{port}")
    inspector: Inspector
    inspector = sqla.inspect(engine)
    schema_names = inspector.get_schema_names()
    for schema in schema_names:
        print(f"SCHEMA::{schema}")
        table_names = inspector.get_table_names(schema)
        for table in table_names:
            print(f"{schema}::{table}")
            column_names = inspector.get_columns(table, schema)
            for column in column_names:
                print(f"{schema}::{table}::{column}")

    # simple execution
    # execute = engine.execute("select * from Node.YOUR_NODE limit 1")
    # rows = execute.fetchall()
    # for row in rows:
    # print(row)

    # close pool
    engine.dispose()
