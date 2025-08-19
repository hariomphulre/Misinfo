# Misinformation Detection System - Complete Flow

## High-Level System Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │    │   Backend API   │    │   Storage Layer │    │  Analysis Layer │
│                 │    │                 │    │                 │    │                 │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Chrome Ext    │───►│ • FastAPI       │───►│ • Firebase RTDB │───►│ • Gemini AI     │
│ • Twitter API   │    │ • /collect      │    │ • GCS Bucket    │    │ • Vision API    │
│ • YouTube API   │    │ • /upload       │    │ • File Storage  │    │ • Risk Analysis │
│ • Reddit Scraper│    │ • /health       │    │ • Metadata      │    │ • Classification│
│ • Document Files│    │ • CORS Enabled  │    │ • Public URLs   │    │ • Reports       │
│ • Social Monitor│    │ • Error Handling│    │ • Backup        │    │ • Notifications │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Detailed Data Flow Diagrams

### 1. Chrome Extension Flow
```
User Action on Webpage
         │
         ▼
┌─────────────────────┐
│  Chrome Extension   │
│  • Extract content  │
│  • Get page URL     │
│  • Get page title   │
│  • Format metadata  │
└─────────────────────┘
         │
         ▼ POST /collect
┌─────────────────────┐
│   FastAPI Backend   │
│  • Validate data    │
│  • Process metadata │
│  • Generate doc_id  │
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│ Firebase Realtime DB│
│  content/           │
│    doc_123: {       │
│      source: "ext"  │
│      type: "text"   │
│      content_text   │
│      metadata: {}   │
│      status: "pend" │
│      timestamp      │
│    }                │
└─────────────────────┘
```

### 2. File Upload Flow
```
User Uploads File (PDF/Image/Video)
         │
         ▼
┌─────────────────────┐
│  Frontend/Extension │
│  • Select file      │
│  • Validate format  │
│  • Show progress    │
└─────────────────────┘
         │
         ▼ POST /upload
┌─────────────────────┐
│   FastAPI Backend   │
│  • Validate file    │
│  • Check file size  │
│  • Generate filename│
└─────────────────────┘
         │
         ▼
┌─────────────────────┐    ┌─────────────────────┐
│   GCS Bucket        │    │ Firebase Realtime DB│
│  • Store file       │    │  content/           │
│  • Make public      │    │    doc_456: {       │
│  • Generate URL     │◄───│      type: "file"   │
│  • Set permissions  │    │      file_url: GCS  │
│                     │    │      metadata: {}   │
│ files/              │    │      status: "pend" │
│   document.pdf      │    │    }                │
│   image.jpg         │    └─────────────────────┘
│   video.mp4         │
└─────────────────────┘
```

### 3. Social Media Collection Flow
```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Social APIs       │    │   Collectors        │    │   Backend API       │
├─────────────────────┤    ├─────────────────────┤    ├─────────────────────┤
│ • Twitter API v2    │───►│ twitter.py          │───►│ POST /collect       │
│ • YouTube Data API  │    │ • Bearer token auth │    │ • source: "twitter" │
│ • Reddit JSON API   │    │ • Rate limiting     │    │ • type: "tweet"     │
│ • RSS News Feeds    │    │ • Error handling    │    │ • content_text      │
└─────────────────────┘    │ • Data formatting   │    │ • metadata: {       │
                           └─────────────────────┘    │     tweet_id,       │
┌─────────────────────┐                               │     author,         │
│ Content Monitor     │                               │     metrics,        │
│ • Schedule tasks    │──────────────────────────────►│     url             │
│ • Every 30min       │                               │   }                 │
│ • Keyword filtering │                               └─────────────────────┘
│ • Trend analysis    │                                        │
└─────────────────────┘                                        ▼
                                                     ┌─────────────────────┐
                                                     │ Firebase Realtime DB│
                                                     │ content/            │
                                                     │   social_data_789   │
                                                     └─────────────────────┘
```

### 4. Document Processing Flow
```
Local Files Directory
         │
         ▼
┌─────────────────────┐
│ Document Processor  │
│ • Scan directory    │
│ • Identify formats  │
│ • Extract text      │
│ • Get metadata      │
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│   File Processing   │
│                     │
│ PDF → PyPDF2        │
│ DOCX → python-docx  │
│ Images → PIL/EXIF   │
│ Videos → OpenCV     │
└─────────────────────┘
         │
         ▼ POST /upload or /collect
┌─────────────────────┐
│   Backend API       │
│ • Text content      │
│ • Extracted metadata│
│ • File references   │
└─────────────────────┘
         │
         ▼
┌─────────────────────┐    ┌─────────────────────┐
│   GCS Storage       │    │ Firebase Database   │
│ (if binary files)   │    │ (metadata + text)   │
└─────────────────────┘    └─────────────────────┘
```

## Complete System Integration Flow

### Phase 1: Data Collection
```
Multiple Sources → Collectors → API Endpoints → Database Storage
                              ↓
                    ┌─────────────────────┐
                    │   Firebase RTDB     │
                    │                     │
                    │ /content            │
                    │   ├── text_data     │
                    │   ├── social_data   │
                    │   ├── file_refs     │
                    │   └── metadata      │
                    │                     │
                    │ Status: "pending"   │
                    └─────────────────────┘
                              ↓
                    ┌─────────────────────┐
                    │   GCS Bucket        │
                    │                     │
                    │ /files              │
                    │   ├── documents/    │
                    │   ├── images/       │
                    │   ├── videos/       │
                    │   └── archives/     │
                    │                     │
                    │ Public URLs         │
                    └─────────────────────┘
```

### Phase 2: Analysis Pipeline (Future Enhancement)
```
Firebase RTDB (pending status)
         │
         ▼ Trigger Function
┌─────────────────────┐
│  Analysis Service   │
│ • Gemini AI         │
│ • Vision API        │
│ • Risk Assessment   │
│ • Classification    │
└─────────────────────┘
         │
         ▼ Update status
┌─────────────────────┐
│ Firebase RTDB       │
│ Status: "analyzed"  │
│ Risk Score: 0.85    │
│ Classification: X   │
│ Confidence: 92%     │
└─────────────────────┘
```

## Data Storage Structure

### Firebase Realtime Database Structure
```json
{
  "content": {
    "chrome_ext_001": {
      "source": "chrome_extension",
      "type": "text",
      "content_text": "Article content here...",
      "metadata": {
        "url": "https://example.com/article",
        "title": "Article Title",
        "timestamp": "2025-08-18T10:30:00.000Z"
      },
      "status": "pending",
      "timestamp": "2025-08-18T10:30:00.000Z"
    },
    "twitter_002": {
      "source": "twitter",
      "type": "tweet",
      "content_text": "Tweet content...",
      "metadata": {
        "tweet_id": "123456789",
        "author": "@username",
        "metrics": {"likes": 150, "retweets": 25},
        "url": "https://twitter.com/user/status/123"
      },
      "status": "pending",
      "timestamp": "2025-08-18T10:31:00.000Z"
    },
    "file_upload_003": {
      "source": "document_processor",
      "type": "file",
      "file_url": "https://storage.googleapis.com/your-bucket/document.pdf",
      "content_text": "Extracted text from PDF...",
      "metadata": {
        "filename": "suspicious_document.pdf",
        "content_type": "application/pdf",
        "file_size": 1024000,
        "upload_timestamp": "2025-08-18T10:32:00.000Z"
      },
      "status": "pending",
      "timestamp": "2025-08-18T10:32:00.000Z"
    }
  }
}
```

### GCS Bucket Structure
```
your-misinformation-bucket/
├── documents/
│   ├── 2025/08/18/
│   │   ├── suspicious_document_001.pdf
│   │   ├── research_paper_002.docx
│   │   └── report_003.txt
├── images/
│   ├── 2025/08/18/
│   │   ├── screenshot_001.png
│   │   ├── meme_002.jpg
│   │   └── infographic_003.svg
├── videos/
│   ├── 2025/08/18/
│   │   ├── news_clip_001.mp4
│   │   └── social_video_002.mov
└── archives/
    └── batch_uploads/
        └── bulk_data_2025_08_18.zip
```

## API Endpoints Summary

### POST /collect
**Purpose**: Collect text-based content
**Input**: 
- source (chrome_extension, twitter, youtube, etc.)
- type (text, tweet, video, etc.)
- content_text 
- metadata (JSON)

**Flow**: Data → Validation → Firebase RTDB → Return doc_id

### POST /upload  
**Purpose**: Handle file uploads
**Input**:
- file (binary data)
- source (document_processor, manual_upload, etc.)

**Flow**: File → GCS Upload → Generate public URL → Firebase RTDB → Return file_url + doc_id

### GET /health
**Purpose**: System health check
**Output**: Service status and availability

## Benefits of This Architecture

1. **Scalability**: Firebase RTDB + GCS handle growth automatically
2. **Flexibility**: Multiple data sources supported
3. **Performance**: Files served directly from GCS CDN
4. **Cost-Effective**: Pay-as-you-use pricing
5. **Security**: IAM controls and access management
6. **Reliability**: Google Cloud's 99.9% uptime SLA
7. **Real-time**: Firebase RTDB supports real-time updates
8. **Analytics Ready**: Data structure supports ML analysis

This system flow ensures efficient collection, storage, and future analysis of misinformation data from multiple sources while maintaining performance and scalability.
