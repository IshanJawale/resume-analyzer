#!/bin/bash

set -o errexit  # exit on error

echo "Installing system dependencies..."
# Install tesseract for OCR support
apt-get update
apt-get install -y tesseract-ocr tesseract-ocr-eng poppler-utils

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Build completed successfully!"
