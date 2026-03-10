#!/usr/bin/env bash

# Exit on error
set -o errexit

echo "--- Installing System Dependencies ---"

# Update and install required PDF/Document processing binaries
# Note: Render uses Ubuntu-based environments
apt-get update
apt-get install -y \
    libreoffice \
    ghostscript \
    tesseract-ocr \
    poppler-utils

echo "--- System Dependencies Installed ---"

# Install Python dependencies
echo "--- Installing Python Dependencies ---"
pip install -r backend/requirements.txt

echo "--- Build Complete ---"
