from django.core.files.storage import Storage
from django.conf import settings
import requests
from io import BytesIO
import logging
from urllib.parse import urljoin


class UthoCloudStorage(Storage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = settings.UTHO_API_KEY
        self.api_secret = settings.UTHO_API_SECRET
        self.endpoint_url = settings.UTHO_ENDPOINT_URL
        self.bucket_name = settings.UTHO_BUCKET_NAME
        self.subfolder = settings.UTHO_SUBFOLDER
        self.dc_zone = settings.UTHO_DC_ZONE

    def _get_headers(self):
        return {
            'Authorization': f"Bearer {self.api_key}",
            'Content-Type': 'multipart/form-data',
        }

    def _build_file_url(self, name):
        # Constructs a URL to access a specific file in Utho Cloud within the subfolder
        return f"{self.endpoint_url}/{self.bucket_name}/{self.dc_zone}/{self.subfolder}/{name}".replace('//', '/')

    def _open(self, name, mode='rb'):
        # Downloads file content from Utho Cloud as a file-like object
        download_url = self._build_file_url(name)
        try:
            logging.info(f"Opening file from Utho Cloud: {download_url}")
            response = requests.get(download_url, headers=self._get_headers())
            response.raise_for_status()
            return BytesIO(response.content)
        except requests.RequestException as e:
            logging.error(f"Failed to open file from Utho Cloud: {e}")
            raise IOError(f"Failed to open file from Utho Cloud: {e}")

    def _save(self, name, content):
    # Ensure proper file path and correct URL construction
        file_path = f"{self.subfolder}/{name}".lstrip('/')  # Remove leading slash if it exists
        upload_url = f"{self.endpoint_url}/upload/{self.bucket_name}/{self.dc_zone}/{file_path}"
        file_bytes = content.read()  # Read the file content

        try:
            logging.info(f"Uploading file to Utho Cloud: {upload_url}")
            files = {'file': (name, file_bytes)}  # Ensure file is named correctly in form data
            response = requests.post(upload_url, headers=self._get_headers(), files=files, timeout=30)
            response.raise_for_status()  # Raise an error if the response code is not 2xx
            logging.info(f"Uploaded file '{file_path}' to Utho Cloud successfully.")
            return name  # Return the file name after upload
        except requests.RequestException as e:
            logging.error(f"Failed to upload file to Utho Cloud: {e}")
            raise IOError(f"Failed to save file to Utho Cloud: {e}")


    def exists(self, name):
        # Checks if a file exists in the bucket within the subfolder
        check_url = f"{self.endpoint_url}/exists/{self.bucket_name}/{self.dc_zone}/{self.subfolder}/{name}"
        try:
            logging.info(f"Checking if file exists: {check_url}")
            response = requests.get(check_url, headers=self._get_headers())
            return response.status_code == 200
        except requests.RequestException as e:
            logging.error(f"Failed to check if file exists: {e}")
            return False

    def url(self, name):
        # Constructs a URL to access a specific file in the subfolder
        return self._build_file_url(name)

    def delete(self, name):
        # Deletes a file from the bucket within the subfolder
        delete_url = f"{self.endpoint_url}/delete/{self.bucket_name}/{self.dc_zone}/{self.subfolder}/{name}"
        try:
            logging.info(f"Deleting file from Utho Cloud: {delete_url}")
            response = requests.delete(delete_url, headers=self._get_headers())
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Failed to delete file from Utho Cloud: {e}")
            raise IOError(f"Failed to delete file from Utho Cloud: {e}")

    def size(self, name):
        # Retrieves the size of a file in bytes within the subfolder
        size_url = f"{self.endpoint_url}/size/{self.bucket_name}/{self.dc_zone}/{self.subfolder}/{name}"
        try:
            logging.info(f"Retrieving file size: {size_url}")
            response = requests.get(size_url, headers=self._get_headers())
            response.raise_for_status()
            return response.json().get('size')
        except requests.RequestException as e:
            logging.error(f"Failed to retrieve file size: {e}")
            return None

    def upload_file(self, name, file):
        """
        Custom method to upload a file directly to Utho Cloud.
        :param name: The name of the file to upload
        :param file: A file-like object containing the file to upload
        :return: The URL of the uploaded file
        """
        file_path = f"{self.subfolder}/{name}".lstrip('/')  # Ensure no leading slash
        upload_url = f"{self.endpoint_url}/upload/{self.bucket_name}/{self.dc_zone}/{file_path}"
        try:
            logging.info(f"Uploading custom file '{name}' to Utho Cloud: {upload_url}")
            files = {'file': (name, file)}
            response = requests.post(upload_url, headers=self._get_headers(), files=files, timeout=30)
            response.raise_for_status()
            logging.info(f"Uploaded custom file '{name}' to Utho Cloud successfully.")
            return self._build_file_url(name)
        except requests.RequestException as e:
            logging.error(f"Failed to upload custom file to Utho Cloud: {e}")
            raise IOError(f"Failed to upload custom file to Utho Cloud: {e}")
