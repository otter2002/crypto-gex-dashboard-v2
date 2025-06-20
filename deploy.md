# 部署指南

## 1. GitHub 仓库设置

### 1.1 创建GitHub仓库
1. 访问 [GitHub](https://github.com) 并登录
2. 点击 "New repository"
3. 仓库名称: `crypto-gex-dashboard-v2`
4. 选择 "Public" 或 "Private"
5. 不要初始化README（我们已经有了）
6. 点击 "Create repository"

### 1.2 推送代码到GitHub
```bash
# 在项目根目录执行
git init
git add .
git commit -m "Initial commit: Crypto GEX Dashboard"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/crypto-gex-dashboard-v2.git
git push -u origin main
```

## 2. Railway 后端部署

### 2.1 连接Railway
1. 访问 [Railway](https://railway.app) 并登录
2. 点击 "New Project"
3. 选择 "Deploy from GitHub repo"
4. 选择你的 `crypto-gex-dashboard-v2` 仓库
5. 选择 `backend` 目录作为根目录

### 2.2 配置环境变量
在Railway项目设置中添加：
```
PORT=8000
```

### 2.3 获取Railway URL
部署完成后，Railway会提供一个URL，例如：
`https://your-app-name.railway.app`

## 3. Vercel 前端部署

### 3.1 连接Vercel
1. 访问 [Vercel](https://vercel.com) 并登录
2. 点击 "New Project"
3. 导入你的GitHub仓库 `crypto-gex-dashboard-v2`
4. 设置项目配置：
   - Framework Preset: Create React App
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `build`

### 3.2 配置环境变量
在Vercel项目设置中添加：
```
REACT_APP_API_URL=https://your-app-name.railway.app
```
（将 `your-app-name.railway.app` 替换为你的Railway URL）

### 3.3 部署
点击 "Deploy" 开始部署

## 4. 验证部署

### 4.1 测试后端API
访问你的Railway URL：
- `https://your-app-name.railway.app/` - 应该返回 `{"message": "GEX API is running"}`
- `https://your-app-name.railway.app/gex?currency=BTC` - 应该返回GEX数据

### 4.2 测试前端
访问你的Vercel URL，应该能看到完整的仪表板界面。

## 5. 自动部署

设置完成后，每次推送到GitHub的main分支都会自动触发：
- Railway重新部署后端
- Vercel重新部署前端

## 6. 故障排除

### 6.1 CORS错误
如果前端无法访问后端API，检查：
- Railway的CORS设置是否正确
- 环境变量 `REACT_APP_API_URL` 是否正确设置

### 6.2 构建失败
- 检查 `package.json` 中的依赖是否正确
- 检查 `requirements.txt` 是否包含所有必要的Python包

### 6.3 API连接失败
- 确认Railway应用正在运行
- 检查Railway的日志以查看错误信息 