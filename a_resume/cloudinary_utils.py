"""
Cloudinary utilities for handling file operations
"""

import os

import cloudinary.api
import cloudinary.uploader
from django.conf import settings


def upload_resume_to_cloudinary(file, user_id, filename):
    """
    Upload a resume file to Cloudinary in the media/resumes folder

    Args:
        file: The file object to upload
        user_id: The user ID for folder organization
        filename: The original filename

    Returns:
        dict: Cloudinary upload result
    """
    try:
        folder_path = f"media/resumes/{user_id}"

        result = cloudinary.uploader.upload(
            file,
            folder=folder_path,
            public_id=os.path.splitext(filename)[0],
            use_filename=True,
            unique_filename=True,
            resource_type="raw",  # Use raw for PDFs and documents
            type="upload",  # Make files publicly accessible
            access_mode="public",  # Ensure public access
        )

        return result
    except Exception as e:
        raise Exception("Failed to upload to Cloudinary") from e  # nosec B608


def delete_resume_from_cloudinary(public_id):
    """
    Delete a resume file from Cloudinary

    Args:
        public_id: The Cloudinary public ID of the file

    Returns:
        dict: Cloudinary deletion result
    """
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result
    except Exception as e:
        raise Exception("Failed to delete from Cloudinary") from e  # nosec B608


def get_cloudinary_url(public_id, transformation=None):
    """
    Get the URL for a file stored in Cloudinary

    Args:
        public_id: The Cloudinary public ID
        transformation: Optional transformation parameters

    Returns:
        str: The Cloudinary URL
    """
    try:
        if transformation:
            return cloudinary.CloudinaryImage(public_id).build_url(**transformation)
        else:
            return cloudinary.CloudinaryImage(public_id).build_url()
    except Exception as e:
        raise Exception("Failed to generate Cloudinary URL") from e  # nosec B608
