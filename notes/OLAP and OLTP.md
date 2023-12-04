# OLAP & OLTP



OLTP: State of the Current World       Query & Update   事务型

OLAP: History   Aggregation Query                                分析型



# 数据的分类

- 状态数据：账户，课程表，购物车
- 历史数据：购物历史，打卡记录，车辆轨迹



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



# 日志

REDO 一个变量在内存中只有一个



任何故障，SSD只要收到写的信息就一定会写完，因为硬件设计，故障后会有部分电容



CRC 



redo日志：写硬盘次数会降低，因为放在最后写，对于一个变量的重复修改会有好处

​					==内存中需要保留改动的值，对内存消耗大==

checkpoint 在某时刻，将之前的日志清空，减小系统空间消耗。一般两分钟一次。



# 数据正确性

并发执行：加锁

解锁：统一在最后



数据一致性

- 添加新属性synchronize TODO DONE
- 数据库中添加文档集合，每个文档集合代表一个任务 ==消息队列==



两阶段加锁：

- 使用前加锁，使用后放锁
- 两端程序之间不能有交叉



# 事务处理

==ACID==

Atomicity  

Consistency 

Isolation: Read commited;   Repeatable Read 多事务并行时互不干扰

Durability: 一旦提交则不可撤销



日志保证AD  并发控制保证I



Abort操作需要记录日志。

两条并行的操作，一个操作回滚会导致另一个操作的结果回滚。

Abort后**才能**释放某个数据的锁

如果不记录Abort，则会被当做事务没完成，回到最初的状态。

Abort相当于end提示符



==事务原则==

短小：否则对数据加锁时间过长，造成系统拥堵

减少事务间的冲突，减少死锁的概率



# 日志和锁的结合

- 崩溃时的原子性（日志）

  一段操作或全部执行，或全部不执行

- 并发时的原子性（锁）



==要考虑性能==



# 线性一致

可串行化调度



如果操作A在操作B开始前结束，A一定排在B之前。



