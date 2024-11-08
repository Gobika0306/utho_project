from django.db import models
from .storage_backends import UthoCloudStorage

class MediaFile(models.Model):
    # Use UthoCloudStorage as the custom storage backend
    file = models.FileField(upload_to='media/', storage=UthoCloudStorage)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
