# Automated Vercel Deployment Script
Write-Host "🚀 Starting Automated Vercel Deployment..." -ForegroundColor Green
Write-Host ""

# Check if we're in the frontend directory
if (-not (Test-Path "package.json")) {
    Write-Host "📁 Switching to frontend directory..." -ForegroundColor Blue
    Set-Location "frontend"
}

# Check if package.json exists
if (-not (Test-Path "package.json")) {
    Write-Host "❌ Error: package.json not found in frontend directory" -ForegroundColor Red
    exit 1
}

Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Blue
npm install

Write-Host "🔧 Setting up Vercel project..." -ForegroundColor Blue
Write-Host "Note: You may need to authenticate with Vercel in your browser" -ForegroundColor Yellow

# Create vercel.json if it doesn't exist
if (-not (Test-Path "vercel.json")) {
    Write-Host "📝 Creating vercel.json configuration..." -ForegroundColor Blue
    @"
{
  "buildCommand": "npm run build",
  "outputDirectory": "build",
  "framework": "create-react-app",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "env": {
    "REACT_APP_API_URL": "https://crypto-gex-dashboard-v2-production.up.railway.app"
  }
}
"@ | Out-File -FilePath "vercel.json" -Encoding UTF8
}

Write-Host ""
Write-Host "🚀 Deploying to Vercel..." -ForegroundColor Green
Write-Host "This will open your browser for authentication if needed" -ForegroundColor Yellow
Write-Host ""

# Deploy to Vercel
try {
    vercel --prod --yes
    Write-Host ""
    Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
    Write-Host "Your frontend should now be live on Vercel!" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "⚠️  Automated deployment failed. Please use manual deployment:" -ForegroundColor Yellow
    Write-Host "1. Open: https://vercel.com/new" -ForegroundColor White
    Write-Host "2. Import: https://github.com/otter2002/crypto-gex-dashboard-v2" -ForegroundColor White
    Write-Host "3. Set Root Directory: frontend" -ForegroundColor White
    Write-Host "4. Add Environment Variable: REACT_APP_API_URL = https://crypto-gex-dashboard-v2-production.up.railway.app" -ForegroundColor White
    Write-Host "5. Click Deploy" -ForegroundColor White
} 