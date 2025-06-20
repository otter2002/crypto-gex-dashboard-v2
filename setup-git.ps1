# PowerShell script: Setup Git repository and push to GitHub
Write-Host "🚀 Starting Git repository setup..." -ForegroundColor Green

# Check if already initialized
if (Test-Path ".git") {
    Write-Host "⚠️  Git repository already exists" -ForegroundColor Yellow
} else {
    Write-Host "📁 Initializing Git repository..." -ForegroundColor Blue
    git init
}

# Configure Git user info (requires user input)
Write-Host "📝 Configuring Git user info..." -ForegroundColor Blue
$userName = Read-Host "Enter your Git username"
$userEmail = Read-Host "Enter your Git email"

git config user.name $userName
git config user.email $userEmail

# Add all files
Write-Host "📝 Adding files to staging area..." -ForegroundColor Blue
git add .

# Commit changes
Write-Host "💾 Committing changes..." -ForegroundColor Blue
git commit -m "Initial commit: Crypto GEX Dashboard with deployment config"

# Set main branch name
git branch -M main

Write-Host "✅ Git setup completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Create new repository on GitHub" -ForegroundColor White
Write-Host "2. Run the following commands to connect to GitHub (replace YOUR_USERNAME):" -ForegroundColor White
Write-Host "   git remote add origin https://github.com/YOUR_USERNAME/crypto-gex-dashboard-v2.git" -ForegroundColor Yellow
Write-Host "   git push -u origin main" -ForegroundColor Yellow
Write-Host "3. Follow the guide in deploy.md to deploy to Railway and Vercel" -ForegroundColor White 