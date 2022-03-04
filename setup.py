import os
import re
from setuptools import find_packages, setup

with open(
    os.path.join(os.path.dirname(__file__), "sqlalchemy_neo4j", "__init__.py")
) as v:
    VERSION = re.compile(r".*__version__ = \"(.*?)\"", re.S).match(v.read()).group(1)

readme = os.path.join(os.path.dirname(__file__), "README.md")

DESCRIPTION = "SQLAlchemy Dialect for Neo4j"
with open(readme, "r") as fh:
    long_description = fh.read()

setup(
    name="sqlalchemy_neo4j",
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Beni Ben Zikry",
    license="Apache",
    url="https://github.com/bbenzikry/sqlalchemy-neo4j",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Database :: Front-Ends",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(include=["sqlalchemy_neo4j"]),
    install_requires=["sqlalchemy>=1.0,<1.4"],
    include_package_data=True,
    extras_require=dict(
        neo4j=["neo4j>=4.0.0"],
        jdbc=["JPype1==1.3.0", "JayDeBeApi==1.2.3"],
    ),
    zip_safe=False,
    keywords="SQLAlchemy Neo4j Dialect",
    entry_points={
        "sqlalchemy.dialects": [
            "neo4j.jdbc = sqlalchemy_neo4j.neo4j_jdbc:Neo4jDialect_jdbc",
            # TODO: cypher support
            # "neo4j.cypher = sqlalchemy_neo4j.neo4j_cypher:Neo4jDialect_cypher",
        ]
    },
)
