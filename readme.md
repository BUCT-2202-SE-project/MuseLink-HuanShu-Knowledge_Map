# 🕸️ 知识图谱构建子系统

## 项目介绍

### 技术方案

- 数据爬取：python
  - py2neo
  - pandas
  - requests
  - bs4
  - csv
  - chardet
  - googletrans
- 数据库：MySQL+neo4j

### 核心功能

- [x] 数据爬取以及整合
- [x] 知识图谱制作以及展示

### 实现过程

1. 博物馆数据爬取完毕后，数据文件以utf-8格式导出csv，之后由数据清洗的同学进行筛选以及情洗

2. 编写代码，调用百度翻译等api接口，进行数据的翻译，之后对翻译不合适的地方进行手动翻译

3. 设计三元组并建模 因为文物有重名，因此三元组内一致采用文物id作为主键

4. 三元组建模，将三元组文件放入服务器上的neo4j的import文件夹中

   1. 连接neo4j:http://123.56.94.39:7474/
   2. 账户：neo4j
   3. 密码：

6. ```cypher
   MATCH (m:Museum)-[r1:包含]->(a:Artifact)
   MATCH (a)-[r2:年代]->(p:Period)
   MATCH (a)-[r3:作者]->(artist:Artist)
   RETURN m, r1, a, r2, p, r3, artist SKIP 1000 LIMIT 1000
   ```

   执行这条语句即可在知识图谱中展现出所有关系

   因为服务器以及neo4j性能的限制，一次只能展现出一千条左右
