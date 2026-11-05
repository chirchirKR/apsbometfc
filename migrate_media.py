
import os
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.utils import timezone

from apsbometfc.storage_backends import SupabaseMediaStorage


# Local media folder
media_root = Path(settings.MEDIA_ROOT)

# Supabase storage
storage = SupabaseMediaStorage()

uploaded = 0
failed = 0

print(f"Source: {media_root}")
print("Starting media migration...\n")

for root, dirs, files in os.walk(media_root):
    for filename in files:

        local_path = Path(root) / filename

        # Preserve the exact relative path
        relative_path = local_path.relative_to(media_root).as_posix()

        try:
            with open(local_path, "rb") as source:
                django_file = File(source, name=filename)

                # Call _save directly to preserve the original filename
                storage._save(relative_path, django_file)

            uploaded += 1
            print(f"UPLOADED: {relative_path}")

        except Exception as error:
            failed += 1
            print(f"FAILED: {relative_path}")
            print(f"Reason: {error}")

print("\nMigration finished.")
print(f"Uploaded: {uploaded}")
print(f"Failed: {failed}")

