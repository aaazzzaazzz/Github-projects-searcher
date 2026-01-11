# 部署指南

本文档详细说明了如何在不同环境中部署GitHub项目智能搜索引擎。

## 🚀 快速部署（开发环境）

### 前置要求
- Python 3.8+
- Git
- 8GB+ RAM

### 步骤
```bash
# 1. 克隆项目
git clone <repository-url>
cd github-search-engine

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置 DEEPSEEK_API_KEY

# 5. 导入数据
python data_importer.py

# 6. 启动服务
python run.py
```

访问 http://localhost:8000

## 🐳 Docker部署

### 1. 创建Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. 创建docker-compose.yml
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/github_search
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
    depends_on:
      - db
    volumes:
      - ./data:/app/data

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=github_search
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### 3. 部署命令
```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f app

# 导入数据（首次运行）
docker-compose exec app python data_importer.py
```

## ☁️ 云平台部署

### Heroku部署
```bash
# 1. 安装Heroku CLI
# 2. 登录Heroku
heroku login

# 3. 创建应用
heroku create your-app-name

# 4. 设置环境变量
heroku config:set DEEPSEEK_API_KEY=your_api_key
heroku config:set DATABASE_URL=your_database_url

# 5. 部署
git push heroku main

# 6. 导入数据
heroku run python data_importer.py
```

### AWS部署（使用Elastic Beanstalk）

1. **准备应用**
```bash
# 创建应用目录
eb init github-search-engine

# 选择平台：Python
# 选择版本：Python 3.9
```

2. **创建requirements.txt**
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pandas==2.1.3
openpyxl==3.1.2
openai==1.3.7
python-dotenv==1.0.0
psycopg2-binary==2.9.9
```

3. **创建application.py**
```python
from main import app

if __name__ == "__main__":
    app.run()
```

4. **部署**
```bash
eb create production
eb deploy
```

## 🔧 生产环境配置

### 1. 环境变量配置
```bash
# 生产环境配置
DEBUG=False
DATABASE_URL=postgresql://user:pass@host:5432/db
DEEPSEEK_API_KEY=your_production_key
ALLOWED_ORIGINS=["https://yourdomain.com"]
```

### 2. Nginx配置
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/your/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 3. Systemd服务配置
```ini
[Unit]
Description=GitHub Search Engine
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/app
Environment=PATH=/path/to/your/venv/bin
ExecStart=/path/to/your/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4. 启用服务
```bash
sudo systemctl enable github-search
sudo systemctl start github-search
sudo systemctl status github-search
```

## 📊 监控和日志

### 1. 应用监控
```python
# 在main.py中添加监控中间件
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('requests_total', 'Total requests')
REQUEST_LATENCY = Histogram('request_duration_seconds', 'Request latency')

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.time()
    REQUEST_COUNT.inc()
    response = await call_next(request)
    REQUEST_LATENCY.observe(time.time() - start_time)
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### 2. 日志配置
```python
# 在config.py中添加日志配置
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "formatter": "default",
            "class": "logging.FileHandler",
            "filename": "app.log",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["default", "file"],
    },
}
```

## 🔒 安全配置

### 1. HTTPS配置
```bash
# 使用Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### 2. 防火墙配置
```bash
# UFW配置
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 3. 数据库安全
```sql
-- 创建专用数据库用户
CREATE USER github_search WITH PASSWORD 'secure_password';
CREATE DATABASE github_search_db OWNER github_search;
GRANT ALL PRIVILEGES ON DATABASE github_search_db TO github_search;
```

## 🚀 性能优化

### 1. 数据库优化
```sql
-- 创建索引
CREATE INDEX idx_projects_language ON projects(repo_language);
CREATE INDEX idx_events_created ON github_events(created_at);
CREATE INDEX idx_events_project ON github_events(project_key);
```

### 2. 缓存配置
```python
# Redis缓存
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@lru_cache(maxsize=1000)
def get_cached_results(query):
    cache_key = f"search:{query}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # 执行搜索
    results = perform_search(query)
    redis_client.setex(cache_key, 3600, json.dumps(results))
    return results
```

### 3. CDN配置
```html
<!-- 使用CDN加速静态资源 -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
```

## 📈 扩展部署

### 1. 负载均衡
```nginx
upstream app_servers {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    location / {
        proxy_pass http://app_servers;
    }
}
```

### 2. 数据库集群
```bash
# PostgreSQL主从复制
# 主库配置
wal_level = replica
max_wal_senders = 3
wal_keep_segments = 64

# 从库配置
standby_mode = 'on'
primary_conninfo = 'host=master_ip port=5432 user=replicator'
```

## 🔍 故障排除

### 常见问题

1. **数据库连接失败**
   ```bash
   # 检查数据库状态
   sudo systemctl status postgresql
   
   # 检查连接
   psql -h localhost -U postgres -d github_search
   ```

2. **API密钥错误**
   ```bash
   # 检查环境变量
   echo $DEEPSEEK_API_KEY
   
   # 测试API连接
   curl -H "Authorization: Bearer $DEEPSEEK_API_KEY" https://api.deepseek.com/v1/models
   ```

3. **内存不足**
   ```bash
   # 检查内存使用
   free -h
   
   # 调整应用配置
   export PYTHONUNBUFFERED=1
   export GUNICORN_WORKERS=2
   ```

4. **端口占用**
   ```bash
   # 查找占用端口的进程
   sudo lsof -i :8000
   
   # 杀死进程
   sudo kill -9 <PID>
   ```

### 日志分析
```bash
# 查看应用日志
tail -f app.log

# 查看Nginx日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# 查看系统日志
journalctl -u github-search -f
```

## 📞 支持和帮助

如果在部署过程中遇到问题，请：

1. 查看日志文件
2. 检查配置文件
3. 运行系统测试：`python test_system.py`
4. 提交Issue到项目仓库

---

🎉 部署完成后，您就可以使用这个强大的GitHub项目智能搜索引擎了！