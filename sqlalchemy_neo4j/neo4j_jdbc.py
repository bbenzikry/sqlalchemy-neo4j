import os
from typing import List
from sqlalchemy import util
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL
from sqlalchemy.engine.base import Connection
from sqlalchemy.sql import sqltypes
from .jdbc import JDBCDialect


def parse_jdbc_url(url: URL):
    host = url.host
    port = url.port
    db = url.database
    jdbc_url = f"jdbc:neo4j://{host}:{port}"
    # We let the driver handle the default operation
    # of connecting to the "current" database
    # in case no database is defined
    if db:
        jdbc_url = f"{jdbc_url}/{db}"
    return jdbc_url


def get_database_product_version(jconn):
    """
    Return Neo4j version.
    Args:
        jconn: The underlying java connection.

    Returns:
        The Neo4j version.
    """
    metadata = jconn.getMetaData()
    return metadata.getDatabaseProductVersion()


# Note: these are kept for reference
# and are currently set directly in the connection string.
DEFAULT_JDBC_ARGS = {
    "AssumeUTC": False,
    "Auth_Type": "Basic",
    "ConnectionTimeoutMS": 5000,
    "DefaultBinaryColumnLength": 32767,
    "DefaultStringColumnLength": 255,
    "EnableJavaDriverLogging": False,
    "ExcludeLabels": None,
    "ExcludeRels": None,
    "FetchSize": 1000,
    "IncludeLabels": None,
    "LabelSeparator": "__",
    "LogLevel": 0,
    "LogPath": os.getcwd(),
    # The interval at which the connector samples nodes when scanning through the data
    # store. For example, if you set this property to 2000, then the connector samples one
    # node for every 2000 nodes in the data store.
    "LabelsSampleSize": 100,
    "MaxIdentifierLen": 4096,
    "PWD": "",
    "RelNodeSeparator": "_",
    "RelsSampleSize": 100,
    "ServerPolicy": None,
    "SSL": False,
    "sslCustomCertPath": "",
    # Or: TRUST_ALL_CERTIFICATES,TRUST_CUSTOM_CA_SIGNED_CERTIFICATES
    "sslTrustStrategy": "TRUST_SYSTEM_CA_SIGNED_CERTIFICATES",
    "sslVerifyHostname": True,
    "StrictlyUseBoltScheme": False,
    "ViewDefinitionFile": "",
}

# pylint: disable=abstract-method
class Neo4jDialect_jdbc(JDBCDialect):
    """
    Neo4j JDBC Dialect for SQL Alchemy
    """

    jdbc_db_name = "neo4j"
    jdbc_driver_name = "com.simba.neo4j.jdbc.Driver"

    def initialize(self, connection: Connection):
        jconn = self.get_underlying_java_conn(connection)
        self.version = get_database_product_version(jconn)
        super(Neo4jDialect_jdbc, self).initialize(connection)

    def create_connect_args(self, url: URL):
        if url is None:
            return
        if "PWD" not in url.query:
            raise Exception(
                """
                Password not supplied to neo4j dialect.
                Make sure all parameters are properly escape.
                """
            )
        jdbc_url = parse_jdbc_url(url)
        self.db = url.database

        return (
            (),
            {
                "jclassname": self.jdbc_driver_name,
                "dsn": jdbc_url,
                # Note: we're passing driver args explicitly instead of the URL to avoid any issues with quoting
                "driver_args": {item[0]: item[1] for item in url.query.items()},
            },
        )

    def get_schema_names(self, engine: Engine, info_cache=None):
        with engine.connect() as connection:
            jconn = self.get_underlying_java_conn(connection)
            metadata = jconn.getMetaData()
            schema_cur = metadata.getSchemas()
            schema_names = []
            while schema_cur.next():
                schema_names.append(schema_cur.getString("TABLE_SCHEM"))
            return schema_names

    def get_table_names(self, engine: Engine, schema, info_cache=None) -> List[str]:
        with engine.connect() as connection:
            jconn = self.get_underlying_java_conn(connection)

            metadata = jconn.getMetaData()
            tbl_cur = metadata.getTables(self.db, schema, "%", None)
            table_names = []
            while tbl_cur.next():
                table_names.append(tbl_cur.getString("TABLE_NAME"))
            return table_names

    def get_columns(self, engine, table_name, schema, info_cache=None) -> List[str]:
        with engine.connect() as connection:
            jconn = self.get_underlying_java_conn(connection)
            metadata = jconn.getMetaData()
            column_cur = metadata.getColumns(self.db, schema, table_name, "%")
            columns = []
            while column_cur.next():
                name: str = column_cur.getString("COLUMN_NAME")
                # if name.startswith('_'):
                # continue
                colspec = column_cur.getString("TYPE_NAME")
                coltype = self.ischema_names.get(colspec)
                if not colspec:
                    util.warn(
                        "Did not recognize type '%s' of column '%s'" % (colspec, name)
                    )
                    coltype = sqltypes.NULLTYPE
                columns.append({"name": name, "type": coltype})
            return columns

    # TODO: use cypher views
    def get_pk_constraint(self, conn, table_name, schema=None, **kw):
        return {"constrained_columns": [], "name": None}

    # TODO: use cypher views
    def get_primary_keys(self):
        return []

    # TODO: use cypher views
    def get_foreign_keys(self, connection, table_name, schema=None, **kw):
        return []

    # TODO: use cypher views
    def get_indexes(self, connection, table_name, schema=None, **kw):
        return []

    def has_table(self, connection: Connection, table_name, schema=None):
        jconn = self.get_underlying_java_conn(connection)
        metadata = jconn.getMetaData()
        tbl_cur = metadata.getTables(self.db, schema, table_name, None)
        exists = False
        while tbl_cur.next():
            exists = True
            break
        return exists

    def _get_server_version_info(self, connection):
        return tuple(int(x) for x in self.version.split("."))

    def _get_default_schema_name(self, engine):
        return self.get_schema_names(engine)[0]

    def get_isolation_level(self, dbapi_conn):
        return "SERIALIZABLE"


# pylint: disable=invalid-name
dialect = Neo4jDialect_jdbc
