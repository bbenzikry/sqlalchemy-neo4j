"""Base dialect and type handling for JDBC."""
import os
from sqlalchemy import (
    BIGINT,
    BINARY,
    DATE,
    FLOAT,
    TIME,
    TIMESTAMP,
    VARCHAR,
    String,
    TypeDecorator,
)
from sqlalchemy.engine.default import DefaultDialect
from sqlalchemy.engine import Connection
from sqlalchemy.sql import sqltypes
from sqlalchemy.sql.sqltypes import BOOLEAN
import jpype.dbapi2 as dbapi2
import jpype

from sqlalchemy_neo4j.interop import start_jvm

ischema_names = {
    "BOOLEAN": BOOLEAN,
    "BIGINT": BIGINT,
    "LONGVARBINARY": BINARY,
    "VARCHAR": VARCHAR,
    "TIME": TIME,
    "TYPE_DATE": DATE,
    "TIMESTAMP": TIMESTAMP,
    "DOUBLE": FLOAT,
}


class MixedBinary(TypeDecorator):
    impl = String

    def process_result_value(self, value, dialect):
        if isinstance(value, str):
            value = bytes(value, "utf-8")
        elif value is not None:
            value = bytes(value)
        return value


class JDBCDialect(DefaultDialect):
    def __init__(self, *args, **kwargs):
        super(JDBCDialect, self).__init__(*args, **kwargs)
        # The user is responsible for starting the JVM with the class path, but we can
        # if NEOJDBC_WARMUP is available, we'll start the jvm automatically for the user.
        if not jpype.isJVMStarted():
            warmup = bool(os.environ.get("NEOJDBC_WARMUP"))
            if warmup:
                start_jvm()
            else:
                raise Exception(
                    "The JVM must be started before connecting to a JDBC driver."
                )
        try:
            jpype.JClass(self.jdbc_driver_name)
        except TypeError:
            err = (
                "The `%s` JDBC driver class was not located in the java class path"
                % (str(self.jdbc_driver_name),),
            )
            raise Exception(err)

    jdbc_db_name = None
    jdbc_driver_name = None
    supports_native_decimal = True
    supports_sane_rowcount = False
    supports_sane_multi_rowcount = False
    supports_unicode_binds = True
    description_encoding = None
    ischema_names = ischema_names
    colspecs = {
        sqltypes.LargeBinary: MixedBinary,
    }

    @classmethod
    # pylint: disable=method-hidden
    def dbapi(cls):
        return dbapi2

    def get_dbapi_conn(self, connection: Connection) -> dbapi2.Connection:

        """
         Return underlying dbapi connection.
        Args:
            connection: db api connection

        Returns:
            Instance of java.sql.Connection (https://docs.oracle.com/javase/8/docs/api/java/sql/Connection.html)
        """
        dbapi_conn = connection.connection
        while dbapi_conn is not None and not isinstance(dbapi_conn, dbapi2.Connection):
            dbapi_conn = dbapi_conn.connection
        return dbapi_conn

    def get_underlying_java_conn(self, connection: Connection):
        """
        Recursively searches for an underlying java connection.
        """
        dbapi = self.get_dbapi_conn(connection)
        return dbapi.connection

    def is_disconnect(self, e, connection, cursor):
        if not isinstance(e, self.dbapi.ProgrammingError):
            return False
        e = str(e)
        return "connection is closed" in e or "cursor is closed" in e

    def do_rollback(self, dbapi_connection):
        pass
