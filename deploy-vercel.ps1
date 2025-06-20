# Vercel Deployment Automation Script
Write-Host "🚀 Vercel Frontend Deployment Setup" -ForegroundColor Green
Write-Host ""

# Display current configuration
Write-Host "📋 Current Configuration:" -ForegroundColor Cyan
Write-Host "Backend API URL: https://crypto-gex-dashboard-v2-production.up.railway.app" -ForegroundColor Yellow
Write-Host "GitHub Repository: https://github.com/otter2002/crypto-gex-dashboard-v2" -ForegroundColor Yellow
Write-Host ""

# Check if Vercel CLI is installed
try {
    $vercelVersion = vercel --version 2>$null
    if ($vercelVersion) {
        Write-Host "✅ Vercel CLI is installed: $vercelVersion" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Vercel CLI not found. Installing..." -ForegroundColor Yellow
        npm install -g vercel
    }
} catch {
    Write-Host "⚠️  Vercel CLI not found. Please install manually:" -ForegroundColor Yellow
    Write-Host "   npm install -g vercel" -ForegroundColor White
}

Write-Host ""
Write-Host "📋 Manual Deployment Steps (if CLI not available):" -ForegroundColor Cyan
Write-Host "1. Open: https://vercel.com/new" -ForegroundColor White
Write-Host "2. Import GitHub repository: otter2002/crypto-gex-dashboard-v2" -ForegroundColor White
Write-Host "3. Configure project settings:" -ForegroundColor White
Write-Host "   - Framework Preset: Create React App" -ForegroundColor Yellow
Write-Host "   - Root Directory: frontend" -ForegroundColor Yellow
Write-Host "   - Build Command: npm run build" -ForegroundColor Yellow
Write-Host "   - Output Directory: build" -ForegroundColor Yellow
Write-Host "4. Add Environment Variable:" -ForegroundColor White
Write-Host "   Name: REACT_APP_API_URL" -ForegroundColor Yellow
Write-Host "   Value: https://crypto-gex-dashboard-v2-production.up.railway.app" -ForegroundColor Yellow
Write-Host "5. Click Deploy" -ForegroundColor White
Write-Host ""

Write-Host "🔗 Quick Links:" -ForegroundColor Cyan
Write-Host "Vercel New Project: https://vercel.com/new" -ForegroundColor Blue
Write-Host "GitHub Repository: https://github.com/otter2002/crypto-gex-dashboard-v2" -ForegroundColor Blue
Write-Host "Railway Backend: https://crypto-gex-dashboard-v2-production.up.railway.app" -ForegroundColor Blue
Write-Host ""

Write-Host "✅ Ready for Vercel deployment!" -ForegroundColor Green 