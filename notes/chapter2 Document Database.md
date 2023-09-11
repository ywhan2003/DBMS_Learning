# 数据库系统基本概念

- 存放
- 组织
- 正确性
- 处理平台



# 数据模型

==键值对==

"Zhang San" &rarr; born on Jan 1, 2000

**键值对方法无法逆向查询**



## 数据模型选择

- 易用性

- 功能性



## 数据库功能

==CRUD==

- create
- read
- update
- delete



数据模型需要能够实现以上功能

但是不能保证所有功能都能达到最佳效率



**数据模型决定增删改查的方式**



# 文档数据库

- database: 数据库
- collection: 文档集
- document: 文档

```mysql
{
	"name": "Zhang San",
	"birthday": "Jan 1, 2000",
	"gender": "male"
}
```

此外，存在嵌套文档结构

```mysql
{
	"name": "Zhang San",
	"birthday": {
		"day": 1,
		"month": "Jan",
		"year": 2000
	},
	"gender": "male"
}
```

可以使用树状结构存储



## 基本功能和语法

```mysql
db.myCollection.insertOne({})
```

- `db`：数据库
- `myCollection`：文档集

参数：文档

用于插入一个新的内容



```mysql
db.myCollection.find(
	{
    	"gender": "male",
    	"birthday.year": "2001"
    }
)
```

此处使用一个文档去匹配文档，即**文档匹配**



```mysql
db.myCollection.updateOne(
	{
    	"name": "Zhang San"
    }, --目标
    {
    	$set: {"birthday.year": "2002"}
    }	--改动指令
)
```

改动内容



```mysql
db.myCollection.deleteOne(
	{
    	"name": "Zhang San"
    }
)
```



以上存在的问题：不能**唯一**识别一个对象

为了解决这一问题，系统会为每一个对象自动生成一个`_id`



