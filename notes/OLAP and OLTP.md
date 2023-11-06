# OLAP & OLTP



OLTP: State of the Current World       Query & Update

OLAP: History   Aggregation Query



## 历史名词

**Data Warehouse**: 历史积累数据

**Business Intelligence**: 用于分析数据，帮助决策



## Data Flow

不能直接在业务系统数据库上进行，使用它们进行业务分析，数据可能不全，需要经过==ETL==的过程

Extraction：将数据推到Data Staging Area，

Transformation：将数据变为便于分析的结构

Load：汇聚数据



## Data Cube

将不同维度的数据整合在一起，帮助决策者从不同的维度进行分析



Slicing and Dicing



Roll Up and Drill Down



Star Schema



Snowflake Schema

