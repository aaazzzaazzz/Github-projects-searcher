# 数据库Schema查看指南

本指南将帮助您了解如何使用提供的工具来获取和查看数据库schema。

## 工具概述

我们提供了两个主要工具来帮助您查看数据库schema：

1. **schema_viewer.py** - 核心Schema查看工具
2. **schema_usage_examples.py** - 使用示例脚本

## 支持的数据库

- SQLite
- PostgreSQL

## 基本使用方法

### 1. 命令行使用

```bash
# 查看所有表的schema
python schema_viewer.py

# 查看特定表的schema
python schema_viewer.py --table projects

# 不显示示例数据
python schema_viewer.py --no-data

# 限制示例数据条数
python schema_viewer.py --data-limit 5

# 导出schema到JSON文件
python schema_viewer.py --export schema.json

# 指定数据库URL
python schema_viewer.py --db-url "postgresql://user:pass@localhost:5432/db"
```

### 2. 代码中使用

```python
from schema_viewer import SchemaViewer

# 创建查看器实例
viewer = SchemaViewer()

# 获取所有表名
tables = viewer.get_all_tables()
print(f"表: {tables}")

# 获取特定表的schema
schema = viewer.get_table_schema('projects')
print(f"字段: {[col['name'] for col in schema['columns']]}")

# 获取表数据
data = viewer.get_table_data('projects', limit=3)
print(f"数据: {data}")

# 打印完整schema
viewer.print_schema(table_name='projects')
```

## 功能详解

### 1. 获取表信息

- **表名列表**: `get_all_tables()`
- **表结构**: `get_table_schema(table_name)`
- **记录数**: `get_table_count(table_name)`
- **示例数据**: `get_table_data(table_name, limit)`

### 2. Schema信息包含

每个表的schema信息包含：

- **字段信息**: 名称、类型、是否可空、默认值
- **主键**: 主键字段列表
- **索引**: 索引名称、字段、是否唯一
- **外键**: 外键关系和引用表
- **记录数**: 表中的总记录数

### 3. 输出格式

- **控制台输出**: 格式化的文本显示
- **JSON导出**: 完整的schema结构导出

## 常见使用场景

### 场景1: 检查数据库连接和基本结构

```python
from schema_viewer import SchemaViewer

try:
    viewer = SchemaViewer()
    tables = viewer.get_all_tables()
    print(f"成功连接数据库，找到 {len(tables)} 个表")
except Exception as e:
    print(f"数据库连接失败: {e}")
```

### 场景2: 检查特定表的结构

```python
viewer = SchemaViewer()
if 'projects' in viewer.get_all_tables():
    schema = viewer.get_table_schema('projects')
    print(f"projects表有 {len(schema['columns'])} 个字段")
    print(f"主键: {schema['primary_keys']}")
```

### 场景3: 调试数据问题

```python
viewer = SchemaViewer()
count = viewer.get_table_count('projects')
print(f"projects表有 {count} 条记录")

if count > 0:
    data = viewer.get_table_data('projects', limit=1)
    print("第一条记录:", data[0])
```

### 场景4: 导出完整schema文档

```bash
python schema_viewer.py --export database_schema.json
```

## 配置说明

### 1. 使用默认配置

工具会自动使用 `config.py` 中的 `settings.database_url` 配置。

### 2. 环境变量配置

在 `.env` 文件中设置：

```env
# SQLite
DATABASE_URL=sqlite:///github_search.db

# PostgreSQL
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

### 3. 手动指定

```python
# SQLite
viewer = SchemaViewer("sqlite:///github_search.db")

# PostgreSQL
viewer = SchemaViewer("postgresql://user:pass@localhost:5432/db")
```

## 故障排除

### 1. 连接问题

**问题**: 无法连接到数据库
**解决**: 
- 检查数据库服务是否运行
- 验证连接URL格式
- 确认用户名密码正确

### 2. 权限问题

**问题**: 无法读取表结构
**解决**:
- 确认数据库用户有读取权限
- 检查表是否存在

### 3. SQLAlchemy版本兼容性

**问题**: 出现SQLAlchemy相关错误
**解决**:
- 检查SQLAlchemy版本
- 更新依赖: `pip install -r requirements.txt`

## 高级用法

### 1. 自定义Schema分析

```python
viewer = SchemaViewer()

# 分析所有表的字段类型分布
type_stats = {}
for table in viewer.get_all_tables():
    schema = viewer.get_table_schema(table)
    for col in schema['columns']:
        col_type = str(col['type'])
        type_stats[col_type] = type_stats.get(col_type, 0) + 1

print("字段类型统计:")
for col_type, count in type_stats.items():
    print(f"  {col_type}: {count}")
```

### 2. 数据完整性检查

```python
viewer = SchemaViewer()

# 检查外键关系
for table in viewer.get_all_tables():
    schema = viewer.get_table_schema(table)
    if schema['foreign_keys']:
        print(f"表 {table} 的外键关系:")
        for fk in schema['foreign_keys']:
            print(f"  {fk['constrained_columns']} -> {fk['referred_table']}")
```

## 最佳实践

1. **定期备份Schema**: 使用 `--export` 功能定期导出schema
2. **版本控制**: 将导出的schema文件纳入版本控制
3. **文档更新**: 当数据库结构变更时，及时更新schema文档
4. **自动化检查**: 在CI/CD中集成schema检查，确保结构一致性

## 相关文件

- `schema_viewer.py` - 核心工具
- `schema_usage_examples.py` - 使用示例
- `project/models.py` - SQLAlchemy模型定义
- `config.py` - 数据库配置
- `.env` - 环境变量配置

## 总结

使用这些工具，您可以轻松地：

- 查看数据库的完整结构
- 理解表之间的关系
- 检查数据完整性
- 生成schema文档
- 调试数据相关问题

如果您在使用过程中遇到任何问题，请参考故障排除部分或查看工具的源代码获取更多信息。