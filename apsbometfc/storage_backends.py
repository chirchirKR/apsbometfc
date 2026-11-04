import os
import uuid
import posixpath
import mimetypes
from urllib.parse import quote

import requests

from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.utils.deconstruct import deconstructible


@deconstructible
class SupabaseMediaStorage(Storage):

    def __init__(self):
        self.url_base = os.environ["SUPABASE_URL"].rstrip("/")
        self.key = os.environ["SUPABASE_KEY"]
        self.bucket = os.environ.get("SUPABASE_BUCKET", "media")

        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
        }

    def _path(self, name):
        return quote(name.lstrip("/"), safe="/")

    def _object_url(self, name):
        return (
            f"{self.url_base}/storage/v1/object/"
            f"{self.bucket}/{self._path(name)}"
        )

    def _save(self, name, content):
        content_type = (
            getattr(content, "content_type", None)
            or mimetypes.guess_type(name)[0]
            or "application/octet-stream"
        )

        content.seek(0)

        headers = {
            **self.headers,
            "Content-Type": content_type,
            "x-upsert": "false",
            "Cache-Control": "3600",
        }

        response = requests.post(
            self._object_url(name),
            headers=headers,
            data=content.read(),
            timeout=120,
        )

        if not response.ok:
            print("SUPABASE STATUS:", response.status_code)
            print("SUPABASE ERROR:", response.text)
            
        response.raise_for_status()
        
        return name

    def _open(self, name, mode="rb"):
        response = requests.get(
            self._object_url(name),
            headers=self.headers,
            timeout=120,
        )

        response.raise_for_status()

        return ContentFile(response.content, name=name)

    def delete(self, name):
        if not name:
            return

        response = requests.delete(
            f"{self.url_base}/storage/v1/object/{self.bucket}",
            headers={
                **self.headers,
                "Content-Type": "application/json",
            },
            json={"prefixes": [name]},
            timeout=60,
        )

        response.raise_for_status()

    def exists(self, name):
        response = requests.head(
            self._object_url(name),
            headers=self.headers,
            timeout=30,
        )

        if response.status_code == 404:
            return False

        response.raise_for_status()
        return True

    def size(self, name):
        response = requests.head(
            self._object_url(name),
            headers=self.headers,
            timeout=30,
        )

        response.raise_for_status()
        return int(response.headers.get("Content-Length", 0))

    def get_available_name(self, name, max_length=None):
        folder, filename = posixpath.split(name)
        extension = posixpath.splitext(filename)[1]

        new_name = f"{uuid.uuid4().hex}{extension}"

        if folder:
            new_name = posixpath.join(folder, new_name)

        return new_name

    def url(self, name):
        return (
            f"{self.url_base}/storage/v1/object/public/"
            f"{self.bucket}/{self._path(name)}"
        )

    def listdir(self, path):
        response = requests.post(
            f"{self.url_base}/storage/v1/object/list/{self.bucket}",
            headers={
                **self.headers,
                "Content-Type": "application/json",
            },
            json={
                "prefix": path.strip("/") + "/" if path else "",
                "limit": 1000,
                "offset": 0,
            },
            timeout=60,
        )

        response.raise_for_status()

        folders = set()
        files = []

        for item in response.json():
            if item.get("id"):
                files.append(item["name"])
            else:
                folders.add(item["name"])

        return sorted(folders), sorted(files)