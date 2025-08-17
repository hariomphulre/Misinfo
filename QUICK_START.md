# Quick Start Guide - Without Twitter API

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies

```bash
# Install backend dependencies
cd backend_service
pip install -r requirements.txt

# Install social source dependencies (for YouTube)
cd ../social_source  
pip install -r requirements.txt
```

### Step 2: Test YouTube Collection

```bash
# Go back to main directory
cd ..

# Test YouTube video collection
python collect.py --source youtube --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --no-backend --output test_result.json
```

### Step 3: Start Backend Service

```bash
cd backend_service
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 💡 What You Can Do Right Now

### 1. **Chrome Extension** (Recommended Start)
- Load the extension in Chrome
- Update `API_BASE_URL` in extension files to `http://localhost:8000`
- Collect content from any webpage!

### 2. **YouTube Video Analysis**
Your YouTube API is already configured! Try:
```bash
python collect.py --source youtube --url "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 3. **Direct API Usage**
Send any content directly:
```bash
curl -X POST "http://localhost:8000/collect" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "manual",
    "type": "text", 
    "content_text": "Sample misinformation content",
    "metadata": "{\"url\": \"https://example.com\"}"
  }'
```

### 4. **File Upload**
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@document.pdf" \
  -F "source=manual_upload"
```

## 🔧 Optional: Get Twitter API Later

If you want Twitter functionality later:
1. Apply for Twitter Developer access
2. Get a Bearer Token
3. Add it to your `.env` file
4. Uncomment the Twitter line in `.env`

## 🎯 Focus Areas Without Twitter

1. **Web Content Collection** - Chrome extension
2. **YouTube Analysis** - Video metadata and descriptions  
3. **File Analysis** - Upload and analyze documents
4. **Manual Data Entry** - Direct API usage
5. **Custom Integrations** - Build your own collectors

You have everything you need to start collecting and analyzing misinformation! 🚀
