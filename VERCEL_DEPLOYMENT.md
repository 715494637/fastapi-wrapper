# Vercel 部署指南

## 概述

本指南将帮助您将 FastAPI Gemini Wrapper 项目部署到 Vercel 平台。Vercel 提供了无服务器函数（Serverless Functions）支持，非常适合部署 FastAPI 应用。

## 前置要求

1. **Vercel 账户**
   - 访问 [vercel.com](https://vercel.com) 注册账户
   - 支持 GitHub、GitLab、Bitbucket 或邮箱注册

2. **项目准备**
   - 确保项目已推送到 GitHub 仓库
   - 项目结构符合 Vercel 要求

## 部署步骤

### 方法一：通过 Vercel CLI 部署（推荐）

1. **安装 Vercel CLI**
   ```bash
   # 使用 npm
   npm install -g vercel

   # 或使用 yarn
   yarn global add vercel

   # 或使用 pnpm
   pnpm add -g vercel
   ```

2. **登录 Vercel**
   ```bash
   vercel login
   ```
   按提示选择登录方式并完成认证。

3. **部署项目**
   ```bash
   # 在项目根目录执行
   vercel
   ```

4. **配置部署选项**
   ```
   ? Set up and deploy "~/fastapi-wrapper"? [Y/n] y
   ? Which scope do you want to deploy to? Your Name
   ? Link to existing project? [y/N] n
   ? What's your project's name? fastapi-wrapper
   ? In which directory is your code located? ./
   ? Want to override the settings? [y/N] n
   ```

5. **设置环境变量**
   ```bash
   # 添加 Gemini API 所需的环境变量
   vercel env add SECURE_1PSID
   vercel env add SECURE_1PSIDTS
   vercel env add GEMINI_PROXY  # 可选
   ```

6. **重新部署以应用环境变量**
   ```bash
   vercel --prod
   ```

### 方法二：通过 Vercel 网页界面部署

1. **登录 Vercel Dashboard**
   - 访问 [vercel.com/dashboard](https://vercel.com/dashboard)

2. **创建新项目**
   - 点击 "Add New..." → "Project"
   - 导入 GitHub 仓库

3. **配置项目设置**
   - **Framework Preset**: Other
   - **Root Directory**: ./
   - **Build Command**: 留空
   - **Output Directory**: 留空
   - **Install Command**: `pip install -r requirements.txt`

4. **添加环境变量**
   在 Environment Variables 部分添加：
   ```
   SECURE_1PSID=your_secure_1psid_value
   SECURE_1PSIDTS=your_secure_1psidts_value
   GEMINI_PROXY=your_proxy_url  # 可选
   ```

5. **部署**
   - 点击 "Deploy" 按钮
   - 等待部署完成

## 项目结构说明

为了在 Vercel 上正确部署，项目需要以下结构：

```
fastapi-wrapper/
├── api/
│   └── index.py          # Vercel 函数入口点
├── src/
│   ├── main.py           # FastAPI 主应用
│   ├── config/
│   ├── models/
│   ├── converters/
│   └── utils/
├── requirements.txt      # Python 依赖
├── vercel.json          # Vercel 配置文件
├── .env.example         # 环境变量示例
├── start.py            # 本地启动脚本
└── README.md
```

### 关键文件说明

#### 1. `vercel.json`
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ],
  "env": {
    "PYTHON_VERSION": "3.11"
  },
  "functions": {
    "api/index.py": {
      "runtime": "python3.11"
    }
  }
}
```

#### 2. `api/index.py`
```python
"""
Vercel serverless function entry point for FastAPI application.
"""

import os
import sys
from pathlib import Path

# Add parent directory to Python path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / "src"))

# Set environment variables for Vercel
os.environ.setdefault("HOST", "0.0.0.0")
os.environ.setdefault("PORT", "8000")
os.environ.setdefault("DEBUG", "false")

# Import and run FastAPI app
from main import app

# Vercel expects a handler function
handler = app
```

## 环境变量配置

### 必需的环境变量

| 变量名 | 说明 | 获取方式 |
|--------|------|----------|
| `SECURE_1PSID` | Gemini 认证 Cookie | 浏览器开发者工具 |
| `SECURE_1PSIDTS` | Gemini 认证时间戳 | 浏览器开发者工具 |

### 可选的环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `GEMINI_PROXY` | 代理设置 | 无 |
| `GEMINI_TIMEOUT` | 请求超时时间 | 300 |
| `GEMINI_AUTO_REFRESH` | 自动刷新认证 | true |
| `LOG_LEVEL` | 日志级别 | INFO |
| `DEBUG` | 调试模式 | false |

## 获取 Gemini 认证信息

1. **打开 Gemini Web**
   - 访问 [gemini.google.com](https://gemini.google.com)
   - 登录您的 Google 账户

2. **获取认证 Cookie**
   - 按 F12 打开开发者工具
   - 切换到 Application/应用程序 标签
   - 在左侧找到 Cookies → https://gemini.google.com
   - 复制以下两个值：
     - `__Secure-1psid`
     - `__Secure-1psidts`

3. **配置环境变量**
   - 在 Vercel 项目设置中添加这两个值
   - 或使用 Vercel CLI：
     ```bash
     vercel env add SECURE_1PSID
     # 粘贴 __Secure-1psid 的值

     vercel env add SECURE_1PSIDTS
     # 粘贴 __Secure-1psidts 的值
     ```

## 常见问题与解决方案

### 1. 部署失败：模块未找到

**问题**：`ModuleNotFoundError: No module named 'src'`

**解决方案**：
- 确保 `api/index.py` 正确设置了 Python 路径
- 检查 `vercel.json` 中的路径配置

### 2. 认证错误

**问题**：返回 401 Authentication Error

**解决方案**：
- 检查 `SECURE_1PSID` 和 `SECURE_1PSIDTS` 是否正确
- 重新获取 Gemini Cookie
- 确保环境变量已正确设置

### 3. 冷启动延迟

**问题**：首次请求响应缓慢

**解决方案**：
- 这是 Vercel 无服务器函数的正常行为
- 考虑使用 Vercel Pro 计划获得更好的性能
- 可以添加预热端点

### 4. 超时错误

**问题**：请求超时

**解决方案**：
- 增加 `GEMINI_TIMEOUT` 环境变量
- 检查 `GEMINI_PROXY` 设置
- 考虑简化请求内容

## 性能优化建议

### 1. 减少冷启动时间

```python
# 在 api/index.py 中预加载模块
import os
import sys
from pathlib import Path

# 预加载所有必需模块
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / "src"))

# 预设环境变量
os.environ.setdefault("HOST", "0.0.0.0")
os.environ.setdefault("PORT", "8000")
os.environ.setdefault("DEBUG", "false")

# 预导入
import main
app = main.app
handler = app
```

### 2. 使用缓存

在 Vercel KV 中存储常用响应：
```python
# 使用 Vercel KV 作为缓存
from vercel_kv import get, set

async def cached_response(key, func, ttl=3600):
    cached = await get(key)
    if cached:
        return cached
    result = await func()
    await set(key, result, ttl=ttl)
    return result
```

### 3. 优化依赖

移除不必要的依赖，保持 `requirements.txt` 精简：
```txt
# 仅保留必需的依赖
fastapi==0.115.13
uvicorn[standard]==0.34.0
python-multipart==0.0.19
pydantic==2.12.5
pydantic-settings==2.10.0
httpx==0.28.1
loguru==0.7.3
```

## 监控与日志

### 1. 查看 Vercel 日志

```bash
# 查看实时日志
vercel logs

# 查看特定函数日志
vercel logs --filter=api/index.py

# 查看最近的日志
vercel logs --since=1h
```

### 2. 在 Vercel Dashboard 查看日志

1. 访问项目 Dashboard
2. 点击 "Functions" 标签
3. 点击函数名称查看日志
4. 使用过滤器筛选错误或警告

### 3. 集成外部监控

```python
# 添加 Sentry 监控
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
)
```

## 更新部署

### 1. 自动部署（推荐）

通过 GitHub 集成，每次推送代码自动触发部署：
1. 在 Vercel 项目设置中启用 GitHub 集成
2. 配置自动部署规则
3. 推送代码到 GitHub 即自动部署

### 2. 手动部署

```bash
# 部署到预览环境
vercel

# 部署到生产环境
vercel --prod
```

### 3. 回滚部署

```bash
# 回滚到上一个版本
vercel rollback

# 查看部署历史
vercel list
```

## 域名配置

### 1. 使用 Vercel 子域名

部署成功后，您将获得一个 `.vercel.app` 子域名。

### 2. 使用自定义域名

1. **添加域名**
   ```bash
   vercel domains add yourdomain.com
   ```

2. **配置 DNS**
   - 添加 CNAME 记录：`cname.vercel-dns.com`
   - 或使用 A 记录（Vercel 提供）

3. **启用 HTTPS**
   - Vercel 自动提供免费 SSL 证书

## 成本考虑

### 1. Vercel 免费额度

- **带宽**：100GB/月
- **函数执行**：100,000 次/月
- **函数执行时间**：100,000 分钟/月

### 2. 优化成本

- 使用缓存减少函数调用
- 优化响应大小减少带宽使用
- 监控使用量避免超额

## 安全最佳实践

### 1. 环境变量安全

- 永远不要在代码中硬编码敏感信息
- 使用 Vercel 的环境变量功能
- 定期轮换 API 密钥

### 2. API 安全

```python
# 添加速率限制
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

@app.post("/v1/chat/completions")
@limiter.limit("60/minute")
async def create_chat_completion(request: ChatCompletionRequest):
    # ... 处理逻辑
```

### 3. CORS 配置

```python
# 限制 CORS 来源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # 具体域名而非 *
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)
```

## 总结

通过以上步骤，您已成功将 FastAPI Gemini Wrapper 部署到 Vercel。主要优势包括：

- ✅ **零配置部署**：Vercel 自动处理 Python 环境
- ✅ **自动 HTTPS**：免费 SSL 证书
- ✅ **全球 CDN**：自动内容分发
- ✅ **无服务器**：按需付费，自动扩缩容
- ✅ **Git 集成**：自动部署和回滚

如有其他问题，请参考：
- [Vercel Python 文档](https://vercel.com/docs/concepts/functions/serverless-functions)
- [FastAPI 部署指南](https://fastapi.tiangolo.com/deployment/)
- 项目 GitHub Issues