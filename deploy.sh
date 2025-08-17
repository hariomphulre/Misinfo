#!/bin/bash

# Automated Deployment Script for Google Cloud Shell
# Run this script in Google Cloud Shell to deploy your Misinformation Collector

set -e  # Exit on any error

echo "🚀 Starting Misinformation Collector Deployment..."

# Configuration
PROJECT_ID="misinfo-469304"
REGION="us-central1"
SERVICE_NAME="misinformation-collector"
YOUTUBE_API_KEY="AIzaSyC6f4yN_NJowx1TXTlFD7crvNMcUtWp3h0"

echo "📋 Project Configuration:"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Service Name: $SERVICE_NAME"

# Step 1: Set up project
echo "🔧 Step 1: Setting up Google Cloud project..."
gcloud config set project $PROJECT_ID
echo "✅ Project set to: $(gcloud config get-value project)"

# Step 2: Enable APIs
echo "🔧 Step 2: Enabling required APIs..."
gcloud services enable run.googleapis.com \
    cloudbuild.googleapis.com \
    firestore.googleapis.com \
    storage-api.googleapis.com \
    storage-component.googleapis.com
echo "✅ APIs enabled"

# Step 3: Create storage bucket
echo "🔧 Step 3: Creating Cloud Storage bucket..."
BUCKET_NAME="misinfo-tool-bucket-$(date +%s)"
gsutil mb gs://$BUCKET_NAME || echo "Bucket might already exist"
gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME || echo "Permissions might already be set"
echo "✅ Bucket created: $BUCKET_NAME"

# Step 4: Initialize Firestore
echo "🔧 Step 4: Initializing Firestore database..."
echo "Choose Firestore mode:"
echo "  1) Native mode (recommended) - Full Firestore features"
echo "  2) Datastore mode - Compatible with Datastore SDKs"
read -p "Enter choice (1 or 2, default: 1): " FIRESTORE_MODE

case $FIRESTORE_MODE in
    2)
        echo "Creating Firestore database in Datastore mode..."
        gcloud firestore databases create --region=$REGION --type=datastore-mode || echo "Firestore database might already exist"
        echo "✅ Firestore initialized in Datastore mode"
        ;;
    *)
        echo "Creating Firestore database in Native mode..."
        gcloud firestore databases create --region=$REGION || echo "Firestore database might already exist"
        echo "✅ Firestore initialized in Native mode"
        ;;
esac

# Step 5: Create environment file
echo "🔧 Step 5: Creating environment configuration..."
mkdir -p backend_service
cat > backend_service/.env << EOF
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
GCS_BUCKET_NAME=$BUCKET_NAME
YOUTUBE_API_KEY=$YOUTUBE_API_KEY
EOF
echo "✅ Environment file created"

# Step 6: Deploy to Cloud Run
echo "🔧 Step 6: Deploying to Cloud Run..."
cd backend_service

gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GCS_BUCKET_NAME=$BUCKET_NAME,YOUTUBE_API_KEY=$YOUTUBE_API_KEY"

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')
echo "✅ Service deployed at: $SERVICE_URL"

cd ..

# Step 7: Update configuration files
echo "🔧 Step 7: Updating configuration with service URL..."

# Update main .env
cat > .env << EOF
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
GCS_BUCKET_NAME=$BUCKET_NAME
YOUTUBE_API_KEY=$YOUTUBE_API_KEY
API_BASE_URL=$SERVICE_URL
EOF

# Update social_source .env
mkdir -p social_source
cat > social_source/.env << EOF
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
YOUTUBE_API_KEY=$YOUTUBE_API_KEY
API_BASE_URL=$SERVICE_URL
EOF

echo "✅ Configuration updated"

# Step 8: Update Chrome extension
echo "🔧 Step 8: Updating Chrome extension..."
mkdir -p chrome_extension

# Create updated background.js (you'll need to paste your content here)
echo "⚠️  Chrome extension files need to be updated manually with the service URL:"
echo "   Replace 'YOUR_CLOUD_RUN_API_URL' with: $SERVICE_URL"

# Step 9: Test deployment
echo "🔧 Step 9: Testing deployment..."

echo "Testing health endpoint..."
if curl -f -s "$SERVICE_URL/health" > /dev/null; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
fi

echo "Testing data collection endpoint..."
RESPONSE=$(curl -s -X POST "$SERVICE_URL/collect" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "deployment_test",
    "type": "text",
    "content_text": "Deployment test content",
    "metadata": "{\"deployment\": true}"
  }')

if echo "$RESPONSE" | grep -q "success"; then
    echo "✅ Data collection test passed"
    echo "Response: $RESPONSE"
else
    echo "❌ Data collection test failed"
    echo "Response: $RESPONSE"
fi

# Final summary
echo ""
echo "🎉 Deployment Complete!"
echo "===================="
echo "📝 Important Information:"
echo "  • Service URL: $SERVICE_URL"
echo "  • Storage Bucket: gs://$BUCKET_NAME"
echo "  • Project ID: $PROJECT_ID"
echo "  • Region: $REGION"
echo ""
echo "🔗 Useful Links:"
echo "  • Cloud Console: https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME?project=$PROJECT_ID"
echo "  • Service Logs: gcloud run services logs tail $SERVICE_NAME --region=$REGION"
echo "  • Storage Browser: https://console.cloud.google.com/storage/browser/$BUCKET_NAME?project=$PROJECT_ID"
echo ""
echo "📋 Next Steps:"
echo "  1. Update Chrome extension files with your service URL"
echo "  2. Test YouTube collection: python3 collect.py --source youtube --url 'YOUTUBE_URL'"
echo "  3. Load Chrome extension in browser"
echo ""
echo "🔧 Management Commands:"
echo "  • View logs: gcloud run services logs tail $SERVICE_NAME --region=$REGION"
echo "  • Update service: gcloud run deploy $SERVICE_NAME --source ./backend_service --region=$REGION"
echo "  • Test health: curl $SERVICE_URL/health"

# Save important info to file
cat > deployment_info.txt << EOF
Misinformation Collector Deployment Info
=======================================
Deployed on: $(date)
Service URL: $SERVICE_URL
Storage Bucket: gs://$BUCKET_NAME
Project ID: $PROJECT_ID
Region: $REGION

Management Commands:
- View logs: gcloud run services logs tail $SERVICE_NAME --region=$REGION
- Update service: gcloud run deploy $SERVICE_NAME --source ./backend_service --region=$REGION
- Test health: curl $SERVICE_URL/health
EOF

echo "💾 Deployment info saved to: deployment_info.txt"
echo ""
echo "✅ All done! Your Misinformation Collector is running on Google Cloud!"
