# Quick Cloud Shell Setup - Manual File Creation

If you prefer to create files manually in Cloud Shell instead of uploading, follow these steps:

## 📁 Essential Files to Create

### 1. Create Project Structure
```bash
mkdir -p Misinfo/backend_service
mkdir -p Misinfo/social_source  
mkdir -p Misinfo/chrome_extension
cd Misinfo
```

### 2. Backend Service Files

#### backend_service/main.py
```bash
cat > backend_service/main.py << 'EOF'
# Copy the content from your local main.py file here
# [Content too long for this example - copy from your local file]
EOF
```

#### backend_service/requirements.txt
```bash
cat > backend_service/requirements.txt << 'EOF'
fastapi
uvicorn
python-dotenv
google-cloud-firestore
google-cloud-storage
python-multipart
EOF
```

#### backend_service/Dockerfile
```bash
cat > backend_service/Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
EOF
```

### 3. Social Source Files

#### social_source/requirements.txt
```bash
cat > social_source/requirements.txt << 'EOF'
tweepy
google-api-python-client
python-dotenv
requests
EOF
```

#### social_source/youtube.py
```bash
cat > social_source/youtube.py << 'EOF'
# Copy the content from your local youtube.py file here
# [Content would be copied from your local file]
EOF
```

### 4. Chrome Extension Files

#### chrome_extension/manifest.json
```bash
cat > chrome_extension/manifest.json << 'EOF'
{
  "manifest_version": 3,
  "name": "Misinformation Collector",
  "version": "1.0",
  "permissions": ["activeTab", "scripting", "storage"],
  "background": {
    "service_worker": "background.js"
  },
  "action": {
    "default_popup": "popup.html"
  }
}
EOF
```

## 🚀 Automated Alternative

Instead of manual creation, you can:

1. **Make deploy.sh executable and run it:**
```bash
chmod +x deploy.sh
./deploy.sh
```

2. **Or follow the detailed step-by-step guide in CLOUD_DEPLOYMENT.md**

## ⚡ Super Quick Start (Recommended)

The fastest way is to:

1. **Upload your entire project as a zip file to Cloud Shell**
2. **Extract and run the deployment script:**
```bash
unzip Misinfo.zip
cd Misinfo
chmod +x deploy.sh
./deploy.sh
```

This will handle everything automatically!
