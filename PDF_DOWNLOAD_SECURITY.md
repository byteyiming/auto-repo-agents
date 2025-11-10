# PDF 下载安全配置指南

## 问题描述

浏览器在下载 PDF 文件时提示"不安全"，可能的原因：

1. **MIME 类型不正确**：使用 `application/octet-stream` 而不是 `application/pdf`
2. **缺少安全头**：没有设置适当的安全响应头
3. **HTTP 连接**：使用 HTTP 而不是 HTTPS（开发环境常见）
4. **内容处置头**：没有正确设置 `Content-Disposition` 头

## 解决方案

### 1. 正确的 MIME 类型

已更新代码以根据文件扩展名设置正确的 MIME 类型：

```python
media_type_map = {
    '.pdf': 'application/pdf',
    '.html': 'text/html',
    '.md': 'text/markdown',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.txt': 'text/plain',
}
```

### 2. 安全响应头

已添加以下安全头：

- **Content-Type**：正确的 MIME 类型
- **Content-Disposition**：`attachment; filename="..."` 用于下载
- **X-Content-Type-Options**：`nosniff` 防止 MIME 类型嗅探

### 3. HTTPS 配置（生产环境）

对于生产环境，建议使用 HTTPS：

```python
# 使用 uvicorn 运行 HTTPS
uvicorn.run(app, host="0.0.0.0", port=443, ssl_keyfile="key.pem", ssl_certfile="cert.pem")
```

或者使用反向代理（如 Nginx）处理 HTTPS。

## 代码更改

### 更新前

```python
return FileResponse(
    path=file_path,
    filename=file_path.name,
    media_type='application/octet-stream'
)
```

### 更新后

```python
# Determine media type based on file extension
media_type_map = {
    '.pdf': 'application/pdf',
    '.html': 'text/html',
    '.md': 'text/markdown',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.txt': 'text/plain',
}

file_ext = file_path.suffix.lower()
media_type = media_type_map.get(file_ext, 'application/octet-stream')

# Set appropriate headers for secure PDF download
headers = {}

# For PDF files, set content-disposition for download
if file_ext == '.pdf':
    headers['Content-Disposition'] = f'attachment; filename="{file_path.name}"'
    headers['Content-Type'] = 'application/pdf'
    headers['X-Content-Type-Options'] = 'nosniff'
else:
    headers['Content-Disposition'] = f'inline; filename="{file_path.name}"'

return FileResponse(
    path=file_path,
    filename=file_path.name,
    media_type=media_type,
    headers=headers
)
```

## 验证修复

### 1. 检查响应头

使用浏览器开发者工具检查响应头：

```
Content-Type: application/pdf
Content-Disposition: attachment; filename="document.pdf"
X-Content-Type-Options: nosniff
```

### 2. 测试下载

1. 访问下载端点：`http://localhost:8000/api/download/{project_id}/{doc_type}`
2. 检查浏览器是否提示不安全
3. 验证 PDF 文件是否可以正常打开

### 3. 使用 curl 测试

```bash
curl -I http://localhost:8000/api/download/project_001/technical_documentation
```

应该看到正确的 `Content-Type: application/pdf` 头。

## 生产环境建议

### 1. 使用 HTTPS

```python
# 使用 SSL 证书
uvicorn.run(
    app,
    host="0.0.0.0",
    port=443,
    ssl_keyfile="/path/to/key.pem",
    ssl_certfile="/path/to/cert.pem"
)
```

### 2. 使用反向代理

使用 Nginx 作为反向代理：

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. 添加更多安全头

```python
headers = {
    'Content-Type': 'application/pdf',
    'Content-Disposition': f'attachment; filename="{file_path.name}"',
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Content-Security-Policy': "default-src 'self'",
}
```

## 故障排除

### 问题 1：浏览器仍然提示不安全

**可能原因**：
1. 使用 HTTP 而不是 HTTPS
2. 证书问题（如果使用 HTTPS）
3. 浏览器缓存

**解决方案**：
1. 清除浏览器缓存
2. 使用 HTTPS（生产环境）
3. 检查证书是否有效

### 问题 2：PDF 无法打开

**可能原因**：
1. PDF 文件损坏
2. MIME 类型不正确
3. 文件编码问题

**解决方案**：
1. 检查 PDF 文件是否完整
2. 验证 MIME 类型设置
3. 检查文件权限

### 问题 3：下载文件名不正确

**可能原因**：
1. `Content-Disposition` 头设置不正确
2. 文件名包含特殊字符
3. 编码问题

**解决方案**：
1. 检查 `Content-Disposition` 头
2. 对文件名进行 URL 编码
3. 使用 `filename*` 参数支持 Unicode

## 总结

已修复 PDF 下载安全问题：

- ✅ **正确的 MIME 类型**：使用 `application/pdf` 而不是 `application/octet-stream`
- ✅ **安全响应头**：添加 `X-Content-Type-Options: nosniff`
- ✅ **内容处置头**：正确设置 `Content-Disposition`
- ✅ **文件类型检测**：根据文件扩展名自动设置 MIME 类型

**注意**：如果仍然看到"不安全"提示，可能是因为：
1. 使用 HTTP 而不是 HTTPS（开发环境正常）
2. 浏览器安全设置
3. 需要清除浏览器缓存

在生产环境中，建议使用 HTTPS 以提供完全安全的下载体验。

