# FastAPI Wrapper 服务器部署指南

## 项目概述

这是一个基于 FastAPI 的 Gemini API 包装器服务，提供 RESTful API 接口来访问 Gemini 模型功能。

## 系统要求

- Python 3.8+
- 操作系统：Windows/Linux/macOS
- 内存：至少 512MB
- 磁盘空间：至少 100MB

## 快速开始

### 1. 环境准备

```bash
# 克隆项目（从GitHub）
git clone https://github.com/715494637/fastapi-wrapper.git
cd fastapi-wrapper

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑 .env 文件，填入你的配置
```

`.env` 文件示例：

```env
# API配置
API_TITLE=FastAPI Gemini Wrapper
API_VERSION=1.0.0
API_DESCRIPTION=RESTful wrapper for Gemini API

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=info

# Gemini API配置
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash

# 可选：安全配置
SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 可选：CORS配置
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]
```

### 3. 启动服务器

#### 开发模式

```bash
# 使用启动脚本
python start.py

# 或直接使用 uvicorn
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 生产模式

```bash
# 使用 gunicorn（Linux/macOS）
pip install gunicorn
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

# 或使用 uvicorn（无热重载）
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## API 文档

服务器启动后，可以访问以下地址：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **健康检查**: http://localhost:8000/health

## 生产部署方案

### 1. Docker 部署

创建 `Dockerfile`：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  fastapi-wrapper:
    build: .
    ports:
      - "8000:8000"
    environment:
      - HOST=0.0.0.0
      - PORT=8000
      - DEBUG=false
    env_file:
      - .env
    restart: unless-stopped
```

部署命令：

```bash
# 构建并运行
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 2. Nginx 反向代理

Nginx 配置示例 (`/etc/nginx/sites-available/fastapi-wrapper`)：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 可选：WebSocket支持
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

启用站点：

```bash
sudo ln -s /etc/nginx/sites-available/fastapi-wrapper /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. Systemd 服务（Linux）

创建服务文件 `/etc/systemd/system/fastapi-wrapper.service`：

```ini
[Unit]
Description=FastAPI Wrapper Service
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/path/to/fastapi-wrapper
Environment=PATH=/path/to/fastapi-wrapper/venv/bin
ExecStart=/path/to/fastapi-wrapper/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable fastapi-wrapper
sudo systemctl start fastapi-wrapper
sudo systemctl status fastapi-wrapper
```

### 4. 云平台部署

#### Heroku

1. 创建 `Procfile`：
   ```
   web: uvicorn src.main:app --host 0.0.0.0 --port $PORT
   ```

2. 部署：
   ```bash
   heroku create your-app-name
   heroku config:set GEMINI_API_KEY=your_key
   git push heroku main
   ```

#### Vercel

1. 安装 Vercel CLI
2. 创建 `vercel.json`：
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "start.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "start.py"
       }
     ]
   }
   ```

#### AWS Lambda

使用 Mangum 包装器：

```python
# lambda_handler.py
from mangum import Mangum
from src.main import app

handler = Mangum(app)
```

## 监控和日志

### 日志配置

项目使用 `loguru` 进行日志管理，可以在 `.env` 中配置：

```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
LOG_FILE=logs/app.log
```

### 健康检查

- 端点：`GET /health`
- 返回：服务状态和基本信息

### 监控建议

1. **使用 Prometheus + Grafana**
   ```python
   # 添加到 requirements.txt
   prometheus-fastapi-instrumentator
   ```

2. **使用 APM 工具**
   - Sentry：错误追踪
   - DataDog：性能监控
   - New Relic：全栈监控

## 安全最佳实践

1. **使用 HTTPS**
   - 配置 SSL 证书（Let's Encrypt 免费证书）
   - 强制 HTTPS 重定向

2. **API 密钥管理**
   - 使用环境变量存储敏感信息
   - 定期轮换 API 密钥
   - 使用密钥管理服务（AWS Secrets Manager 等）

3. **访问控制**
   - 实现速率限制
   - 添加 API 认证（JWT 或 API Key）
   - 设置 CORS 策略

4. **防火墙配置**
   ```bash
   # 仅允许必要端口
   sudo ufw allow 22/tcp   # SSH
   sudo ufw allow 80/tcp   # HTTP
   sudo ufw allow 443/tcp  # HTTPS
   sudo ufw enable
   ```

## 性能优化

1. **启用缓存**
   ```python
   # 安装 redis
   pip install redis
   # 配置缓存中间件
   ```

2. **使用连接池**
   - 数据库连接池
   - HTTP 客户端连接池

3. **负载均衡**
   - 使用多实例部署
   - 配置负载均衡器（Nginx、HAProxy）

## 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 查找占用端口的进程
   netstat -tulpn | grep :8000
   # 或使用 lsof
   lsof -i :8000
   ```

2. **权限问题**
   ```bash
   # 确保正确的文件权限
   chmod +x start.py
   chown -R www-data:www-data /path/to/app
   ```

3. **依赖冲突**
   ```bash
   # 重新创建虚拟环境
   rm -rf venv
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

### 日志分析

```bash
# 查看实时日志
tail -f logs/app.log

# 查找错误
grep "ERROR" logs/app.log

# 分析访问模式
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c
```

## 备份和恢复

### 数据备份

```bash
# 创建备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf backup/fastapi-wrapper_$DATE.tar.gz \
    --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='logs' \
    .
```

### 自动化备份

添加到 crontab：

```bash
# 每天凌晨2点备份
0 2 * * * /path/to/backup-script.sh
```

## 联系支持

如果遇到问题，请：

1. 查看日志文件
2. 检查 GitHub Issues
3. 提交新的 Issue 并包含：
   - 错误信息
   - 系统环境
   - 复现步骤

---

**注意**：请确保在生产环境中使用强密码、启用 HTTPS 并定期更新依赖包。