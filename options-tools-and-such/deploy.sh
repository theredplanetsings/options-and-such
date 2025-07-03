#!/bin/bash

# Quick deployment script for Options Dashboard

echo "🚀 Options Dashboard Deployment Helper"
echo "======================================"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Initialize git repository if not already done
if [ ! -d ".git" ]; then
    echo "📝 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: Options Dashboard"
fi

echo ""
echo "Choose your deployment platform:"
echo "1) Streamlit Community Cloud (Recommended - Free)"
echo "2) Heroku"
echo "3) Railway"
echo ""

read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🌟 Streamlit Community Cloud Deployment"
        echo "======================================"
        echo "1. Push this code to GitHub:"
        echo "   - Create a new repository on GitHub"
        echo "   - Run: git remote add origin https://github.com/yourusername/your-repo.git"
        echo "   - Run: git push -u origin main"
        echo ""
        echo "2. Visit: https://share.streamlit.io"
        echo "3. Connect your GitHub account"
        echo "4. Select your repository and 'app.py'"
        echo "5. Your app will be live in minutes!"
        ;;
    2)
        echo ""
        echo "🔥 Heroku Deployment"
        echo "==================="
        if ! command -v heroku &> /dev/null; then
            echo "❌ Heroku CLI not found. Install from: https://devcenter.heroku.com/articles/heroku-cli"
            exit 1
        fi
        
        read -p "Enter your app name: " app_name
        
        echo "Creating Heroku app..."
        heroku create $app_name
        
        echo "Deploying to Heroku..."
        git push heroku main
        
        echo "✅ App deployed! Visit: https://$app_name.herokuapp.com"
        ;;
    3)
        echo ""
        echo "🚂 Railway Deployment"
        echo "===================="
        echo "1. Visit: https://railway.app"
        echo "2. Connect your GitHub account"
        echo "3. Import this repository"
        echo "4. Railway will auto-deploy your app!"
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        ;;
esac
