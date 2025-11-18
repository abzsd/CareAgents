#!/bin/bash

# Healthcare Frontend Deployment Script for Cloud Run
# This script builds and deploys the frontend to Google Cloud Run

set -e

# Configuration
PROJECT_ID="braided-tracker-478502-b2"
REGION="europe-west1"
SERVICE_NAME="careagents-frontend"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Backend URL (replace with your actual backend URL after deploying backend)
BACKEND_URL="https://careagents-backend-346759294104.europe-west1.run.app"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== CareAgents Frontend Deployment ===${NC}"
echo -e "${YELLOW}Project ID: ${PROJECT_ID}${NC}"
echo -e "${YELLOW}Region: ${REGION}${NC}"
echo -e "${YELLOW}Service: ${SERVICE_NAME}${NC}"
echo -e "${YELLOW}Backend URL: ${BACKEND_URL}${NC}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed${NC}"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if backend URL is set
if [ "${BACKEND_URL}" = "https://careagents-backend-xxxxx.run.app" ]; then
    echo -e "${RED}Error: Please set the BACKEND_URL environment variable${NC}"
    echo "Example: export BACKEND_URL=https://your-backend-url.run.app"
    exit 1
fi

# Authenticate with GCP (if needed)
echo -e "${GREEN}Step 1: Checking GCP authentication...${NC}"
if ! gcloud auth print-access-token &> /dev/null; then
    echo "Not authenticated. Running gcloud auth login..."
    gcloud auth login
fi

# # Set the project
# echo -e "${GREEN}Step 2: Setting GCP project...${NC}"
# gcloud config set project ${PROJECT_ID}

# Enable required APIs
# echo -e "${GREEN}Step 3: Enabling required APIs...${NC}"
# gcloud services enable cloudbuild.googleapis.com
# gcloud services enable run.googleapis.com
# gcloud services enable containerregistry.googleapis.com

# Build the Docker image with backend URL
echo -e "${GREEN}Step 4: Building Docker image...${NC}"
gcloud builds submit --tag ${IMAGE_NAME}  .

# Deploy to Cloud Run
echo -e "${GREEN}Step 5: Deploying to Cloud Run...${NC}"
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --set-env-vars="VITE_API_BASE_URL=${BACKEND_URL}" \
  --memory 512Mi \
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
echo -e "${GREEN}Frontend URL: ${SERVICE_URL}${NC}"
echo -e "${GREEN}Backend URL: ${BACKEND_URL}${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Open the frontend: ${SERVICE_URL}"
echo "2. Test the application end-to-end"
echo "3. Configure Firebase authentication with the new frontend URL"
