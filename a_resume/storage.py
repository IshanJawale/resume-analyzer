from cloudinary_storage.storage import MediaCloudinaryStorage
import os


class ResumeCloudinaryStorage(MediaCloudinaryStorage):
    """Custom Cloudinary storage for resume files"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _get_public_id(self, name):
        """Generate public ID with media/resumes/ prefix"""
        if not name.startswith("media/resumes/"):
            # Ensure the file is stored in media/resumes/ folder
            name = f"media/resumes/{name}"
        return super()._get_public_id(name)

    def url(self, name):
        """Generate URL for the file"""
        if not name.startswith("media/resumes/"):
            name = f"media/resumes/{name}"
        return super().url(name)
