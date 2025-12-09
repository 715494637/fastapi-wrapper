# FastAPI Gemini Wrapper

一个基于 FastAPI 的 Gemini API 包装器，提供简洁的 RESTful API 接口来访问 Google 的 Gemini AI 模型。

## 功能特性

- 🚀 基于 FastAPI 的高性能异步 API
- 🤖 集成 Google Gemini AI 模型
- 📚 自动生成的 API 文档（Swagger/ReDoc）
- 🔧 灵活的配置管理
- 📝 结构化日志记录
- 🛡️ 内置错误处理
- 🏥 健康检查端点
- 🔒 环境变量配置

## 快速开始

### 安装

```bash
# 克隆仓库
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

### 配置

1. 复制环境变量模板：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，添加你的 Gemini API 密钥：
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 运行

```bash
# 启动开发服务器
python start.py

# 或使用 uvicorn
uvicorn src.main:app --reload
```

服务器将在 http://localhost:8000 启动

## API 文档

启动服务器后，访问以下地址查看 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 项目结构

```
fastapi-wrapper/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py      # 配置管理
│   ├── models/
│   │   ├── __init__.py
│   │   └── gemini_models.py # Pydantic 模型
│   ├── converters/
│   │   ├── __init__.py
│   │   └── request_converter.py  # 请求转换器
│   └── utils/
│       ├── __init__.py
│       ├── logger.py        # 日志配置
│       └── exceptions.py    # 自定义异常
├── requirements.txt         # 项目依赖
├── start.py                # 启动脚本
├── .env.example            # 环境变量模板
├── .gitignore              # Git 忽略文件
├── README.md               # 项目说明
└── SERVER_DEPLOYMENT.md    # 部署指南
```

## 环境变量

主要环境变量配置：

```env
# API 配置
API_TITLE=FastAPI Gemini Wrapper
API_VERSION=1.0.0

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=info

# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```

## 开发

### 添加新的 API 端点

1. 在 `src/models/` 中定义 Pydantic 模型
2. 在 `src/main.py` 中添加路由
3. 在 `src/converters/` 中添加请求转换逻辑
4. 更新 API 文档

### 运行测试

```bash
# 安装测试依赖
pip install pytest pytest-asyncio

# 运行测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=src
```

## 部署

详细的部署指南请参考 [SERVER_DEPLOYMENT.md](./SERVER_DEPLOYMENT.md)

支持以下部署方式：

- Docker 容器化部署
- Nginx 反向代理
- Systemd 服务（Linux）
- 云平台部署（Heroku、Vercel、AWS Lambda）

## API 使用示例

### 基本请求

```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "你好，请介绍一下自己",
       "temperature": 0.7,
       "max_tokens": 1000
     }'
```

### 响应示例

```json
{
  "success": true,
  "data": {
    "response": "你好！我是 Gemini，一个由 Google 开发的大语言模型...",
    "usage": {
      "prompt_tokens": 10,
      "completion_tokens": 50,
      "total_tokens": 60
    }
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 监控

### 健康检查

```bash
curl http://localhost:8000/health
```

响应：
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}
```

## 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 支持

如果遇到问题或有任何疑问，请：

1. 查看 [SERVER_DEPLOYMENT.md](./SERVER_DEPLOYMENT.md) 部署指南
2. 搜索已有的 [Issues](https://github.com/715494637/fastapi-wrapper/issues)
3. 创建新的 Issue

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 基础 Gemini API 集成
- FastAPI 框架搭建
- 自动 API 文档生成
- Docker 部署支持

---

⭐ 如果这个项目对你有帮助，请给它一个星标！