# Misinformation Collector

A comprehensive system for collecting and analyzing content from various sources including social media platforms and web pages.

## Project Structure

```
Misinfo/
├── backend_service/          # FastAPI backend service
├── chrome_extension/         # Chrome browser extension
├── social_source/           # Social media data collectors
├── collect.py              # Main CLI integration script
├── .env.template          # Environment configuration template
└── README.md             # This file
```

## Features

- **Backend Service**: FastAPI-based REST API for data collection and storage
- **Chrome Extension**: Browser extension for collecting web page content
- **Social Media Integration**: Collectors for Twitter and YouTube
- **Cloud Storage**: Integration with Google Cloud Firestore and Storage
- **Error Handling**: Comprehensive error handling and logging

## Setup Instructions

### 1. Environment Setup

1. Copy the environment template:
   ```bash
   cp .env.template .env
   ```

2. Fill in your actual API keys and configuration in `.env`:
   - `GCS_BUCKET_NAME`: Your Google Cloud Storage bucket name
   - `GOOGLE_APPLICATION_CREDENTIALS`: Path to your service account JSON file
   - `TWITTER_BEARER_TOKEN`: Your Twitter API bearer token
   - `YOUTUBE_API_KEY`: Your YouTube Data API key
   - `API_BASE_URL`: Your deployed backend service URL

### 2. Backend Service Setup

1. Navigate to the backend service directory:
   ```bash
   cd backend_service
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run locally:
   ```bash
   uvicorn main:app --reload
   ```

4. Deploy to Google Cloud Run (optional):
   ```bash
   gcloud run deploy misinformation-collector --source .
   ```

### 3. Social Source Components Setup

1. Navigate to the social source directory:
   ```bash
   cd social_source
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 4. Chrome Extension Setup

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked" and select the `chrome_extension` folder
4. Update the `API_BASE_URL` in both `background.js` and `popup.html` with your actual backend URL

## Usage

### Using the CLI Tool

Collect a Twitter tweet:
```bash
python collect.py --source twitter --url "https://twitter.com/user/status/1234567890"
```

Collect a YouTube video:
```bash
python collect.py --source youtube --url "https://www.youtube.com/watch?v=VIDEO_ID"
```

Save results to file:
```bash
python collect.py --source twitter --id "1234567890" --output results.json
```

### Using the Chrome Extension

1. Click the extension icon in your browser
2. Click "Collect Page Content" to extract and send page content to the backend

### Using the Backend API Directly

Send content via POST request:
```bash
curl -X POST "https://your-api-url/collect" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "manual",
    "type": "text",
    "content_text": "Sample content",
    "metadata": "{\"url\": \"https://example.com\"}"
  }'
```

## API Endpoints

- `POST /collect`: Collect text/data content
- `POST /upload`: Upload file content
- `GET /health`: Health check endpoint

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GCS_BUCKET_NAME` | Google Cloud Storage bucket name | Yes |
| `GOOGLE_APPLICATION_CREDENTIALS` | Service account JSON file path | Yes |
| `TWITTER_BEARER_TOKEN` | Twitter API bearer token | For Twitter features |
| `YOUTUBE_API_KEY` | YouTube Data API key | For YouTube features |
| `API_BASE_URL` | Backend service URL | For social source integration |

### Google Cloud Setup

1. Create a Google Cloud project
2. Enable Firestore and Cloud Storage APIs
3. Create a service account with appropriate permissions
4. Download the service account JSON key
5. Create a Cloud Storage bucket

### Social Media API Setup

#### Twitter API
1. Apply for Twitter Developer access
2. Create a new app in the Twitter Developer Portal
3. Generate a Bearer Token

#### YouTube API
1. Enable YouTube Data API v3 in Google Cloud Console
2. Create API credentials (API key)

## Error Handling

The system includes comprehensive error handling:
- API rate limiting for social media platforms
- Network error handling with retries
- Validation of required environment variables
- Detailed logging for debugging

## Security Considerations

- Never commit API keys or credentials to version control
- Use environment variables for all sensitive configuration
- Consider implementing authentication for the backend API
- Review and limit permissions for service accounts

## Development

### Adding New Sources

1. Create a new Python file in `social_source/`
2. Implement functions following the pattern in `twitter.py` and `youtube.py`
3. Add integration to `collect.py`

### Testing

Run the backend service locally and test endpoints:
```bash
curl http://localhost:8000/health
```

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure all requirements are installed
2. **Authentication errors**: Verify API keys and service account permissions
3. **Network errors**: Check API URLs and network connectivity
4. **Extension not working**: Verify the API URL is updated in extension files

### Logs

Check application logs for detailed error information:
- Backend service logs through uvicorn
- Chrome extension logs in browser console
- Social source logs through Python logging

## License

This project is for educational and research purposes. Please ensure compliance with platform terms of service when collecting data.
