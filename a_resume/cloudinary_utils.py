"""
Cloudinary utilities for handling file operations
"""
import cloudinary.uploader
import cloudinary.api
from django.conf import settings
import os

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
            resource_type="auto"  # Auto-detect file type
        )
        
        return result
    except Exception as e:
        raise Exception(f"Failed to upload to Cloudinary: {str(e)}")

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
        raise Exception(f"Failed to delete from Cloudinary: {str(e)}")

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
        raise Exception(f"Failed to generate Cloudinary URL: {str(e)}")
