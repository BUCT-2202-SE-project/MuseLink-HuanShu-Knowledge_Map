在neo4j中执行代码

​		因为数据量太过庞大，直接执行耗时较久且服务器性能不足，因此先对id建立唯一约束

- ```cypher
  CREATE CONSTRAINT artifact_id_unique FOR (a:Artifact) REQUIRE a.id IS UNIQUE;
  ```

  导入文物的基本信息

- ```cypher
  :auto
  CALL {
    LOAD CSV WITH HEADERS FROM 'file:///collection.csv' AS row
    MERGE (o:Artifact {id: row.`Object ID`})
    ON CREATE SET 
      o.title = row.Title,
      o.descripe = row.descripe,
      o.url = row.`Object URL`
    ON MATCH SET 
      o.title = row.Title,
      o.descripe = row.descripe,
      o.url = row.`Object URL`
  } IN TRANSACTIONS OF 5000 ROWS;
  ```

  对博物馆建立唯一约束并导入博物馆和文物的关系 

- ```cypher
  // 先建唯一约束（只需执行一次）
  CREATE CONSTRAINT museum_name_unique 
  FOR (m:Museum) 
  REQUIRE m.name IS UNIQUE;
  
  // 然后执行批量导入关系
  :auto
  CALL {
    LOAD CSV WITH HEADERS FROM 'file:///relation1.csv' AS row
    MATCH (a:Artifact {id: row.`Object ID`})
    MERGE (m:Museum {name: row.Museum})
    MERGE (m)-[r:包含]->(a)
    SET r.artifact_title = a.title  // 把 title 存到关系上
  } IN TRANSACTIONS OF 1000 ROWS;
  
  ```

- ```cypher
  :auto
  CALL {
    LOAD CSV WITH HEADERS FROM 'file:///relation2.csv' AS row
    MATCH (a:Artifact {id: row.`Object ID`})  // 根据 Object ID 匹配 Artifact 节点
    MERGE (p:Period {period: row.Period})     // 创建 Period 节点，如果不存在
    MERGE (a)-[r:年代]->(p)                  // 创建 Artifact 和 Period 之间的年代关系
  } IN TRANSACTIONS OF 1000 ROWS;
  
  ```

- ```cypher
  :auto
  CALL {
    LOAD CSV WITH HEADERS FROM 'file:///relation3.csv' AS row
    MATCH (a:Artifact {id: row.`Object ID`})  // 根据 Object ID 匹配 Artifact 节点
    MERGE (artist:Artist {name: row.Artist})   // 创建 Artist 节点，如果不存在
    MERGE (a)-[r:作者]->(artist)               // 创建 Artifact 和 作家 之间的关系
  } IN TRANSACTIONS OF 1000 ROWS;
  ```

- 以上代码执行之后，就建立了文物与博物馆 作者 年代 之间的关系

```cypher
MATCH (m:Museum)-[r1:包含]->(a:Artifact)
MATCH (a)-[r2:年代]->(p:Period)
MATCH (a)-[r3:作者]->(artist:Artist)
RETURN m, r1, a, r2, p, r3, artist SKIP 1000 LIMIT 1000
```











