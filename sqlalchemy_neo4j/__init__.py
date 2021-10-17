"""Neo4j SQL Alchemy dialect based on the Neo4j BI Connector for JDBC."""
from sqlalchemy.dialects import registry

__version__ = "0.1.dev"
registry.register("neo4j", "sqlalchemy_neo4j.neo4j_jdbc", "Neo4jDialect_jdbc")
registry.register("neo4j+jdbc", "sqlalchemy_neo4j.neo4j_jdbc", "Neo4jDialect_jdbc")
# registry.register("neo4j+cypher", "sqlalchemy_neo4j.neo4j_cypher", "Neo4jDialect_cypher")
