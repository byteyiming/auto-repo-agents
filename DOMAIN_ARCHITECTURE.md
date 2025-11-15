# Domain Architecture Explanation

## 🤔 为什么使用 `api.omnidoc.info`？

### 当前架构（子域名分离）

```
omnidoc.info          → 前端 (Vercel)
api.omnidoc.info      → 后端 API (Oracle Cloud)
```

### ✅ 使用子域名的优势

1. **独立部署和扩展**
   - 前端在 Vercel（CDN + Edge Network）
   - 后端在 Oracle Cloud（服务器）
   - 可以独立扩展，互不影响

2. **CORS 配置更清晰**
   - 前端域名：`omnidoc.info`
   - API 域名：`api.omnidoc.info`
   - CORS 配置简单明了

3. **符合 RESTful API 最佳实践**
   - 很多大型应用都使用 `api.*` 子域名
   - 例如：GitHub (`api.github.com`), Twitter (`api.twitter.com`)

4. **SSL 证书管理**
   - 每个子域名可以独立配置 SSL
   - 更灵活的安全配置

5. **缓存策略**
   - 前端可以设置不同的缓存策略
   - API 可以设置不同的缓存策略

### ❌ 使用子域名的缺点

1. **需要配置两个 DNS 记录**
   - `omnidoc.info` → Vercel
   - `api.omnidoc.info` → Oracle Cloud

2. **需要两个 SSL 证书**
   - 但 Let's Encrypt 免费，自动续期

## 🔄 替代方案：使用路径（Path-based）

如果你不想用子域名，也可以这样：

```
omnidoc.info          → 前端 (Vercel)
omnidoc.info/api      → 后端 API (通过 Vercel Proxy)
```

### 如何改为路径方式？

#### 方案 1：Vercel Rewrites（推荐）

在 `frontend/vercel.json` 中配置：

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://api.omnidoc.info/api/:path*"
    }
  ]
}
```

然后前端使用：
```bash
NEXT_PUBLIC_API_BASE=https://omnidoc.info/api
```

#### 方案 2：Nginx 反向代理（如果都在同一服务器）

如果前后端都在 Oracle Cloud，可以用 Nginx：

```nginx
server {
    listen 80;
    server_name omnidoc.info www.omnidoc.info;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

## 📊 对比

| 特性 | 子域名 (`api.omnidoc.info`) | 路径 (`omnidoc.info/api`) |
|------|---------------------------|-------------------------|
| **部署灵活性** | ⭐⭐⭐⭐⭐ 完全独立 | ⭐⭐⭐ 需要协调 |
| **扩展性** | ⭐⭐⭐⭐⭐ 独立扩展 | ⭐⭐⭐ 受限于前端 |
| **配置复杂度** | ⭐⭐⭐ 需要两个 DNS | ⭐⭐⭐⭐ 只需一个 DNS |
| **CORS 配置** | ⭐⭐⭐⭐⭐ 简单 | ⭐⭐⭐⭐ 简单 |
| **SSL 证书** | ⭐⭐⭐ 需要两个 | ⭐⭐⭐⭐⭐ 只需一个 |
| **常见做法** | ⭐⭐⭐⭐⭐ 行业标准 | ⭐⭐⭐ 较少使用 |

## 💡 推荐

**保持当前架构（子域名）**，因为：
1. ✅ 你已经部署在 Vercel（前端）和 Oracle Cloud（后端）
2. ✅ 完全独立，互不影响
3. ✅ 符合行业最佳实践
4. ✅ 未来扩展更容易

**如果一定要改**，可以使用 Vercel Rewrites（方案 1），这样：
- 用户只看到一个域名 `omnidoc.info`
- 但 API 请求会被代理到 `api.omnidoc.info`
- 对用户透明，但后端仍然独立

## 🔧 如何切换？

如果你想改为路径方式，告诉我，我可以：
1. 更新 Vercel 配置
2. 更新前端环境变量
3. 更新 CORS 配置
4. 更新所有文档

但目前建议**保持子域名架构**，这是更好的长期方案。

