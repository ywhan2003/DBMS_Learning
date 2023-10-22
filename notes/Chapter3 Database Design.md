# 数据库设计

终端：前端用户界面  (基本定下功能)

服务器：后端



数据库设计解决：

- 存什么
- 怎么存：组织结构等



步骤：

- 需求分析
- 概念设计：存什么
- 结构设计：怎么存



**优化目标**：访问效率



问题：

- 几个文档集合
- 每个文档集合的文档存什么属性，结构是怎么样的



用户集合：编号，信息，粉丝：用户的编号，关注：用户的编号，文章：文章的编号

文章集合：作者：id和名称，题目，时间，内容，评论：用户+内容

用户首页集合：把所有显示的内容存进去



好坏判断依据：

- 是否丢失信息
- 访问效率（重点）：频率高的重点优化



是否嵌入：根据功能，是否需要脱离另一文档来进行访问；访问效率

冗余属性

冗余文档

索引



## 设计原则



### 概念设计



对象，对象之间的关系

> n:1 文章：用户
>
> n:m 用户：用户

以上内容为**概念模型**



### 结构设计



一个对象存到一个文档

多个对象存到一个文档 （嵌入式）

> 文章的信息嵌入到用户文档中，但这种方式不合适
>
> 因为这两个信息往往会分别访问



内容的存储与关系的存储

> 文章的文档中有uid元素来访问用户
>
> 因为访问文章时往往需要得到作者用户的信息
>
> 同时用户的文档中可以有文章的id，理由类似



**冗余数据**

- 提高读取数据的效率
- 降低更新数据的效率
- 增大软件开发复杂度
- 增大软件维护的负担

经常更新的数据不适合构建冗余数据



**索引**

> 电影与对应的评论的存储
>
> - 电影中存评论
> - 电影中存评论的id
> - 评论数据集中添加被评论电影的id，并在id上增加索引



时间段存储：一个个线段



文档过大

- 使用一个单独的文档，添加索引