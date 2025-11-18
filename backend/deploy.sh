#!/bin/bash

# Healthcare Backend Deployment Script for Cloud Run
# This script builds and deploys the backend to Google Cloud Run

set -e

# Load environment variables from .env file
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
fi

# Configuration
PROJECT_ID="braided-tracker-478502-b2"
REGION="europe-west1"
SERVICE_NAME="careagents-backend"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== CareAgents Backend Deployment ===${NC}"
echo -e "${YELLOW}Project ID: ${PROJECT_ID}${NC}"
echo -e "${YELLOW}Region: ${REGION}${NC}"
echo -e "${YELLOW}Service: ${SERVICE_NAME}${NC}"
echo ""

# Verify required environment variables
if [ -z "$GOOGLE_API_KEY" ]; then
    echo -e "${RED}Error: GOOGLE_API_KEY is not set${NC}"
    echo "Please ensure it's defined in your .env file"
    exit 1
fi
echo -e "${GREEN}✓ GOOGLE_API_KEY is set${NC}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed${NC}"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Authenticate with GCP (if needed)
# echo -e "${GREEN}Step 1: Checking GCP authentication...${NC}"
# if ! gcloud auth print-access-token &> /dev/null; then
#     echo "Not authenticated. Running gcloud auth login..."
#     gcloud auth login
# fi

# Set the project
# echo -e "${GREEN}Step 2: Setting GCP project...${NC}"
# gcloud config set project ${PROJECT_ID}

# # Enable required APIs
# echo -e "${GREEN}Step 3: Enabling required APIs...${NC}"
# gcloud services enable cloudbuild.googleapis.com
# gcloud services enable run.googleapis.com
# gcloud services enable containerregistry.googleapis.com

# Build the Docker image
echo -e "${GREEN}Step 4: Building Docker image...${NC}"
gcloud builds submit --tag ${IMAGE_NAME}  .

# Deploy to Cloud Run
echo -e "${GREEN}Step 5: Deploying to Cloud Run...${NC}"
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --set-env-vars="DB_HOST=34.77.160.92,DB_PORT=5432,DB_NAME=healthcare_db,DB_USER=postgres,DB_PASSWORD=DB-bnb-890,DB_SSL=,DB_POOL_MIN_SIZE=10,DB_POOL_MAX_SIZE=20,DB_TIMEOUT=60,DB_COMMAND_TIMEOUT=60" \
  --set-env-vars="GOOGLE_API_KEY=${GOOGLE_API_KEY}" \
  --set-env-vars="GCS_BUCKET_NAME=db-bnb" \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10 \
  --min-instances 0 \
  --timeout 300 \
  --port 8080

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --format 'value(status.url)')

echo ""
echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo -e "${GREEN}Backend URL: ${SERVICE_URL}${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Test the backend: curl ${SERVICE_URL}/health"
echo "2. Update frontend VITE_API_BASE_URL to: ${SERVICE_URL}/api/v1"
echo "3. Deploy the frontend with the new backend URL"
