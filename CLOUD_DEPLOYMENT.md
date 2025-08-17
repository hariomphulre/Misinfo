# Google Cloud Deployment Guide - Step by Step

## 📋 Prerequisites
- Google Cloud account with billing enabled
- Project ID: `misinfo-469304` (from your .env file)
- YouTube API key already configured

## 🚀 Step-by-Step Cloud Shell Deployment

### Step 1: Open Google Cloud Shell
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click the Cloud Shell icon (>_) in the top right corner
3. Wait for Cloud Shell to initialize

### Step 2: Set Up Your Project
```bash
# Set your project ID
export PROJECT_ID=misinfo-469304

# Set the project as default
gcloud config set project $PROJECT_ID

# Verify project is set correctly
gcloud config get-value project
```

### Step 3: Enable Required APIs
```bash
# Enable necessary Google Cloud APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable storage-api.googleapis.com
gcloud services enable storage-component.googleapis.com
```

### Step 4: Create Cloud Storage Bucket
```bash
# Create storage bucket (must be globally unique)
export BUCKET_NAME=misinfo-tool-bucket-$(date +%s)
gsutil mb gs://$BUCKET_NAME

# Make bucket public for file access (optional - adjust for security)
gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME

# Save bucket name for later
echo "Your bucket name: $BUCKET_NAME"
```

### Step 5: Initialize Firestore Database
```bash
# Option A: Create Firestore database (Native mode - recommended)
gcloud firestore databases create --region=us-central1

# Option B: Create Firestore database with Datastore compatibility
# This enables Firestore's implementation of Datastore compatibility for server-side SDKs
# gcloud firestore databases create --region=us-central1 --type=datastore-mode

# Option C: Create Firestore database in Datastore mode (legacy)
# gcloud datastore indexes create --region=us-central1
```

**Choose your database mode:**
- **Native mode** (recommended): Full Firestore features, real-time updates, better querying
- **Datastore mode**: Compatible with existing Datastore applications, limited Firestore features

### Step 6: Clone/Upload Your Project to Cloud Shell

#### Option A: Upload from Local Machine
1. In Cloud Shell, click the "Upload file" button (folder icon with up arrow)
2. Create a zip file of your entire Misinfo project locally
3. Upload the zip file
4. Extract it:
```bash
unzip Misinfo.zip
cd Misinfo
```

#### Option B: Create Project Directly in Cloud Shell
```bash
# Create project directory
mkdir -p Misinfo/backend_service
mkdir -p Misinfo/social_source
mkdir -p Misinfo/chrome_extension
cd Misinfo
```

Then copy each file content using the Cloud Shell editor or create files as needed.

### Step 7: Set Up Environment Variables
```bash
# Create .env file for backend service
cat > backend_service/.env << EOF
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
GCS_BUCKET_NAME=$BUCKET_NAME
YOUTUBE_API_KEY=AIzaSyC6f4yN_NJowx1TXTlFD7crvNMcUtWp3h0
EOF

# Also create for social_source
cat > social_source/.env << EOF
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
YOUTUBE_API_KEY=AIzaSyC6f4yN_NJowx1TXTlFD7crvNMcUtWp3h0
API_BASE_URL=https://WILL_BE_UPDATED_AFTER_DEPLOYMENT
EOF
```

### Step 8: Deploy Backend Service to Cloud Run
```bash
# Navigate to backend service directory
cd backend_service

# Deploy to Cloud Run
gcloud run deploy misinformation-collector \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GCS_BUCKET_NAME=$BUCKET_NAME,YOUTUBE_API_KEY=AIzaSyC6f4yN_NJowx1TXTlFD7crvNMcUtWp3h0

# Get the service URL
export SERVICE_URL=$(gcloud run services describe misinformation-collector --region=us-central1 --format='value(status.url)')
echo "Your service is deployed at: $SERVICE_URL"
```

### Step 9: Update Configuration with Deployed URL
```bash
# Update social_source .env with actual service URL
cd ../social_source
sed -i "s|API_BASE_URL=https://WILL_BE_UPDATED_AFTER_DEPLOYMENT|API_BASE_URL=$SERVICE_URL|g" .env

# Also update the main .env file
cd ..
echo "API_BASE_URL=$SERVICE_URL" >> .env
```

### Step 10: Test Your Deployment
```bash
# Test health endpoint
curl $SERVICE_URL/health

# Test data collection endpoint (using form data)
curl -X POST "$SERVICE_URL/collect" \
  -F "source=test" \
  -F "type=text" \
  -F "content_text=Test deployment content" \
  -F "metadata={\"test\": true}"
```

### Step 11: Install Dependencies and Test Social Sources
```bash
# Install Python dependencies in Cloud Shell
cd social_source
pip3 install --user -r requirements.txt

# Test YouTube collection (replace with actual video ID)
cd ..
python3 collect.py --source youtube --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --output test_result.json

# Check the result
cat test_result.json
```

### Step 12: Set Up Chrome Extension
```bash
# Update Chrome extension files with your service URL
cd chrome_extension

# Update background.js
sed -i "s|const API_BASE_URL = \"https://YOUR_CLOUD_RUN_API_URL\";|const API_BASE_URL = \"$SERVICE_URL\";|g" background.js

# Update popup.html
sed -i "s|const API_BASE_URL = \"https://YOUR_CLOUD_RUN_API_URL\";|const API_BASE_URL = \"$SERVICE_URL\";|g" popup.html

echo "Chrome extension files updated with: $SERVICE_URL"
```

### Step 13: Download Updated Chrome Extension
```bash
# Create a zip file of the updated extension
cd chrome_extension
zip -r ../chrome_extension_updated.zip .
cd ..

# Download the zip file to your local machine using Cloud Shell's download feature
echo "Download chrome_extension_updated.zip from Cloud Shell to install locally"
```

## 🔧 Ongoing Management Commands

### View Logs
```bash
# View Cloud Run logs
gcloud run services logs read misinformation-collector --region=us-central1

# Follow logs in real-time
gcloud run services logs tail misinformation-collector --region=us-central1
```

### Update Service
```bash
# Redeploy with changes
cd backend_service
gcloud run deploy misinformation-collector \
    --source . \
    --region us-central1
```

### Check Firestore Data
```bash
# List collections
gcloud firestore collections list

# Export data (optional)
gcloud firestore export gs://$BUCKET_NAME/firestore-export
```

### Scale or Configure Service
```bash
# Set memory and CPU limits
gcloud run services update misinformation-collector \
    --region=us-central1 \
    --memory=1Gi \
    --cpu=1 \
    --concurrency=100
```

## 🎯 Testing Your Full System

### 1. Test Backend API
```bash
# Health check
curl $SERVICE_URL/health

# Data collection (using form data)
    curl -X POST "$SERVICE_URL/collect" \
    -F "source=manual" \
    -F "type=text" \
    -F "content_text=Sample content for testing" \
    -F "metadata={\"url\": \"https://example.com\"}"
```

### 2. Test YouTube Collection
```bash
python3 collect.py --source youtube --id "dQw4w9WgXcQ"
```

### 3. Test Chrome Extension
1. Download the updated extension zip from Cloud Shell
2. Extract it locally
3. Load in Chrome (chrome://extensions/ → Developer mode → Load unpacked)
4. Test on any webpage

## 📊 Monitor Your System

### Cloud Console Monitoring
1. Go to Cloud Run in Console
2. Click on your service
3. View metrics, logs, and revisions

### Cost Monitoring
```bash
# Check current usage
gcloud run services describe misinformation-collector --region=us-central1 --format="table(metadata.name,status.url,status.latestCreatedRevisionName)"
```

## 🔒 Security Considerations

### Secure Your API (Optional)
```bash
# Remove unauthenticated access and require authentication
gcloud run services remove-iam-policy-binding misinformation-collector \
    --region=us-central1 \
    --member="allUsers" \
    --role="roles/run.invoker"
```

### Set Up Identity and Access Management
```bash
# Create a service account for specific access
gcloud iam service-accounts create misinfo-collector-sa \
    --display-name="Misinformation Collector Service Account"
```

## 🚨 Troubleshooting

### Common Issues and Solutions

1. **Build Failures**:
```bash
# Check build logs
gcloud builds list --limit=5
gcloud builds log [BUILD_ID]
```

2. **Permission Issues**:
```bash
# Check current permissions
gcloud projects get-iam-policy $PROJECT_ID
```

3. **API Quota Issues**:
```bash
# Check API quotas
gcloud services list --enabled
```

4. **Service Not Responding**:
```bash
# Check service status
gcloud run services describe misinformation-collector --region=us-central1
```

## 📝 Important URLs to Save

After deployment, save these URLs:
- **Backend Service**: `echo $SERVICE_URL`
- **Storage Bucket**: `echo gs://$BUCKET_NAME`
- **Project Console**: `https://console.cloud.google.com/home/dashboard?project=$PROJECT_ID`

Your Misinformation Collector is now running on Google Cloud! 🚀
