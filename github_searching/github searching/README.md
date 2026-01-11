# GitHub项目智能搜索引擎
队长：马健原（DataEase数据大屏的实现，前端与后端的结合，优化前端） 队员：李思莹（前后端功能基本实现，数据库的搭建）
基于DeepSeek AI技术的GitHub项目智能搜索引擎，为开发者提供精准的项目推荐和搜索服务。

项目结构：
我们的系统采用了分层架构设计，从上到下分为前端展示层、FastAPI应用层、服务模块层和数据层。
       前端层：采用HTML5、CSS3和JavaScript构建，集成了DataEase数据可视化工具，支持词云图和各种统计图表的展示。用户可以通过响应式界面进行搜索，系统会实时返回结果和AI分析解释。
       应用层：使用FastAPI作为Web框架，这是一个高性能的异步框架，能够自动生成API文档。我们设计了RESTful风格的API接口，包括搜索、项目详情、趋势分析等多个端点，为前端提供稳定的数据服务。
       服务层：分为搜索服务、AI服务和数据服务三个核心模块。搜索服务负责处理复杂查询逻辑和过滤条件；AI服务通过DeepSeek大模型提供自然语言理解和智能推荐；数据服务则为可视化组件提供数据支持。
       数据层：使用SQLAlchemy作为ORM工具，系统目前使用SQLite数据库作为主要数据存储。在数据库中我们设计了四个核心数据表：项目基本信息表、事件日志表、贡献者统计表和项目活跃度统计表，通过这些表来存储和管理所有的GitHub数据。当前所有有效的项目数据、事件日志和贡献者信息都存储在SQLite数据库中，确保数据的完整性和可靠性。


## 📋 系统要求
- **Python 3.8+**
- **8GB+ RAM**
- **2GB+ 磁盘空间**

#  注意！由于本项目没有能力使用嵌入版dataease,若想启动本搜索引擎中查看数据大屏的功能，一定要确保已下载过dataease社区版，在本地导入本项目中包含的det2文件，然后用本地获得的数据大屏链接修改现有index_simplified.html中的对应链接，才能达到可视化的效果

## 🛠️ 安装部署

### 前置准备：安装必需的库

在启动服务之前，需要先安装以下Python依赖库：

#### 1. 创建虚拟环境（推荐）

```bash
# 创建Python虚拟环境
python3 -m venv .venv

# 激活虚拟环境
# Linux/Mac:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate.bat
```

#### 2. 安装依赖库

```bash
# 第一步：升级 pip（必须执行，否则可能遇到依赖解析错误）
python -m pip install --upgrade pip

# 第二步：如需完整功能，可尝试安装完整依赖
pip install -r requirements.txt

#如果安装 `requirements.txt` 时遇到依赖冲突（AssertionError等错误），逐个安装可选依赖（根据需要选择）：
```bash
# Web框架
fastapi==0.104.1
uvicorn[standard]==0.24.0

# 数据库
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9  # PostgreSQL

# 数据处理
pandas==2.1.3
openpyxl==3.1.2
numpy==1.25.2

# API集成
httpx==0.25.2
requests==2.31.0

# 搜索和文本处理
elasticsearch==8.11.0
sentence-transformers==2.2.2
torch==2.1.1

# 认证和安全
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# 配置和环境
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0

# 日志和监控
loguru==0.7.2

# 前端相关
jinja2==3.1.2
aiofiles==23.2.1

# 开发工具
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.11.0
flake8==6.1.0

# DeepSeek API客户端
openai==1.3.7  # 兼容OpenAI API格式

```

#### 3. 配置环境变量

```bash
# 复制配置文件
cp .env.example .env

# 编辑配置文件，设置DeepSeek API密钥
# DEEPSEEK_API_KEY=your_api_key_here
```

#### 4. 初始化数据库（可选）

```bash
# 导入Excel数据到数据库（如果需要）
python data_importer.py
```

### 启动服务

#### 方法一：使用启动脚本（推荐）

```bash
# 使用run.py启动
python run.py
```

#### 方法二：直接使用uvicorn启动

```bash
# 开发模式（支持热重载）
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### 方法三：后台运行（Linux/Mac）

```bash
# 使用nohup在后台运行
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > github_search.log 2>&1 &

# 查看进程ID
echo $! > github_search.pid

# 停止服务
kill $(cat github_search.pid)
```

#### 方法四：使用systemd服务（Linux生产环境）

创建服务文件 `/etc/systemd/system/github-search.service`：

```ini
[Unit]
Description=GitHub Search Service
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/daolun_1
Environment="PATH=/path/to/daolun_1/.venv/bin"
ExecStart=/path/to/daolun_1/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 启用并启动服务
sudo systemctl enable github-search
sudo systemctl start github-search

# 查看服务状态
sudo systemctl status github-search

# 查看日志
sudo journalctl -u github-search -f
```

### 访问应用

启动成功后，在浏览器中打开：

- **主页**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/health

## 📁 项目结构

```
github-search-engine/
├── main.py                 # FastAPI主应用
├── run.py                  # 启动脚本
├── config.py               # 配置管理
├── requirements.txt        # 依赖包列表
├── .env.example           # 环境变量示例
├── data_importer.py       # 数据导入脚本
├── analyze_data.py        # 数据分析脚本
├── project/              # 数据模型
│   ├── __init__.py
│   ├── models.py         # SQLAlchemy模型
│   └── database.py       # 数据库配置
├── services/             # 业务逻辑
│   ├── __init__.py
│   ├── search_service.py  # 搜索服务
│   └── deepseek_service.py # DeepSeek AI服务
├── templates/            # HTML模板
│   └── index.html
├── static/              # 静态文件
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
└── data/               # 数据文件
    ├── top_300_metrics_full.xlsx
    └── top300_20_23_robust_all_fixed.xlsx
```

## 🔧 配置说明

### 环境变量配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DATABASE_URL` | 数据库连接URL | `sqlite:///github_search.db` |
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | 必填 |
| `DEEPSEEK_API_BASE` | DeepSeek API地址 | `https://api.deepseek.com/v1` |
| `DEEPSEEK_MODEL` | 使用的模型 | `deepseek-chat` |
| `SEARCH_RESULTS_LIMIT` | 搜索结果限制 | `20` |
| `DEBUG` | 调试模式 | `False` |

### 数据库配置

支持SQLite和PostgreSQL：

**SQLite（默认）:**
```
DATABASE_URL=sqlite:///github_search.db
```

**PostgreSQL:**
```
DATABASE_URL=postgresql://username:password@localhost:5432/github_search
```

## 📊 API文档

### 搜索API
```
GET /api/search?q=关键词&page=1&page_size=20&sort_by=relevance
```

**参数说明:**
- `q`: 搜索关键词
- `page`: 页码
- `page_size`: 每页大小
- `sort_by`: 排序方式 (relevance, stars, forks, activity, recent)

### 项目详情API
```
GET /api/projects/{project_key}
```

### 趋势项目API
```
GET /api/trending?time_period=monthly&limit=10
```

### 语言统计API
```
GET /api/languages
```

### 趋势分析API
```
GET /api/trends?time_period=yearly
```

## 🎨 使用指南

### 基础搜索
1. 在搜索框输入关键词，如"机器学习"、"Web开发"
2. 点击搜索或按回车键
3. 查看搜索结果和AI分析解释

### 高级搜索
1. 点击"高级搜索"展开选项
2. 选择编程语言、活跃度、贡献者类型等过滤条件
3. 选择排序方式
4. 执行搜索

### 查看项目详情
1. 在搜索结果中点击项目名称
2. 查看项目统计、活动历史、贡献者信息
3. 查看AI生成的项目摘要和相关推荐

### 趋势分析
1. 在首页查看趋势项目
2. 切换时间周期（月度/季度/年度）
3. 查看语言统计分布

## 🔍 数据来源

本系统基于以下GitHub数据：

- **时间范围**: 2020年1月 - 2023年3月
- **项目数量**: 300个顶级项目
- **数据类型**: 
  - 项目基本信息（星标、分叉、语言等）
  - 详细事件日志（Issues、PR、Push等）
  - 贡献者活动和统计

## 🚀 性能优化

### 数据库优化
- 为常用查询字段添加索引
- 使用连接池管理数据库连接
- 实现查询结果缓存

### 搜索优化
- 分页加载减少内存占用
- 异步API调用提升响应速度
- 前端虚拟滚动处理大量结果

### AI服务优化
- 请求频率限制
- 响应缓存机制
- 错误重试策略

## 🛡️ 安全考虑

- API密钥安全存储
- SQL注入防护
- XSS攻击防护
- CORS配置
- 请求频率限制

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📝 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 基础搜索功能
- DeepSeek AI集成
- 项目详情页面
- 趋势分析功能

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [DeepSeek](https://www.deepseek.com/) - 提供AI技术支持
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Web框架
- [Bootstrap](https://getbootstrap.com/) - 前端UI框架
- [Font Awesome](https://fontawesome.com/) - 图标库

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件
- 项目讨论区

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！
