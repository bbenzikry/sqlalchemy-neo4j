# SQL Alchemy dialect for Neo4j

This package provides the SQL dialect for Neo4j, using the official JDBC driver (the Neo4j "BI Connector" )

## Installation
```bash
pip install sqlalchemy-neo4j
```

## Prerequisites
- Java 8 / 11
- Download the [Neo4j BI Connector](https://neo4j.com/bi-connector/)
  > The reason the JAR is not included in the package is due to licensing concerns. I may add the jar into the bundle in the future.
- Add the jar to the classpath, either directly via the ``CLASSPATH`` environment variable or while initializing the JVM
  > You can also use the ``NEOJDBC_WARMUP`` environment variable, which will ensure we reuse an existing jpype instance or create a new one ( with default parameters )


## Getting started 
```python

from sqlalchemy import create_engine 

# This happens automatically if you set the NEOJDBC_WARMUP environment variable
jpype.startJVM()

eng = create_engine("neo4j+jdbc://neo4j-neo4j:7687/neo4j?UID=neo4j&PWD=QUOTED_PASSWORD&LogLevel=6&StrictlyUseBoltScheme=false")

execute = engine.execute("select * from Node.YOUR_NODE limit 1")
rows = execute.fetchall()
for row in rows:
    print(row)
```

See more [examples](./examples/)


## Related projects
* [Neo4j Metabase Driver](https://github.com/bbenzikry/metabase-neo4j-driver) - Use Neo4j with Metabase. Use both SQL and Cypher ( the driver uses the same underlying BI connector for SQL queries )

## Future
- Add Cypher support
- Add support for Cypher views in JDBC driver
- Add ORM support and testing


## Donations ##

<div align="center">
Did this project help you out? 
<p>
<a href="https://etherscan.io/address/0x10c97e3e727cb3ee0bafb4f99f63225525150a35">bbenzikry.eth / 0x10c97e3e727cb3ee0bafb4f99f63225525150a35</a>
</p>
<img src="https://user-images.githubusercontent.com/1993348/221440410-bec29828-dbf8-4908-aa18-dc41e70592bb.png" width="200" />
</div>
