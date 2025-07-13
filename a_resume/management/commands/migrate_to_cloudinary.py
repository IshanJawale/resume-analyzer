from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from a_resume.models import ResumeAnalysis
import os
import cloudinary.uploader


class Command(BaseCommand):
    help = "Migrate existing resume files from local storage to Cloudinary"

    def handle(self, *args, **options):
        analyses = ResumeAnalysis.objects.all()
        migrated_count = 0
        error_count = 0

        for analysis in analyses:
            if analysis.file and hasattr(analysis.file, "path"):
                try:
                    # Get the local file path
                    local_path = analysis.file.path

                    if os.path.exists(local_path):
                        # Upload to Cloudinary with the same folder structure
                        folder_path = f"media/resumes/{analysis.user.id}"

                        result = cloudinary.uploader.upload(
                            local_path,
                            folder=folder_path,
                            public_id=os.path.splitext(analysis.filename)[0],
                            use_filename=True,
                            unique_filename=True,
                        )

                        # Update the file field to point to Cloudinary
                        analysis.file.name = f"{analysis.user.id}/{analysis.filename}"
                        analysis.save()

                        migrated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f"Migrated: {analysis.filename}")
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f"Local file not found: {local_path}")
                        )

                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f"Error migrating {analysis.filename}: {str(e)}"
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Migration complete. Migrated: {migrated_count}, Errors: {error_count}"
            )
        )
