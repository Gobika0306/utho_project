from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import MediaFile
from .serializers import MediaFileSerializer
from .storage_backends import UthoCloudStorage
import logging

class MediaFileViewSet(viewsets.ModelViewSet):
    # Queryset to fetch all media files from the database
    queryset = MediaFile.objects.all()
    
    # Serializer used to convert model data into JSON
    serializer_class = MediaFileSerializer
    
    def perform_create(self, serializer):
        # Handle file upload to custom storage (UthoCloud)
        file = self.request.FILES.get('file')
        
        if file:
            # Log file details
            logging.info(f"Received file: {file.name} (size: {file.size} bytes)")
            
            # Initialize UthoCloudStorage
            storage = UthoCloudStorage()
            
            try:
                # Save the file to UthoCloud
                file_url = storage.save(file.name, file)  # Save the file to Utho Cloud storage
                logging.info(f"File uploaded successfully. URL: {file_url}")
                
                # Save the file URL to the database
                serializer.save(file=file_url)
            except Exception as e:
                logging.error(f"Error uploading file: {e}")
                raise OSError(f"Failed to save file: {e}")
        else:
            logging.error("No file received in request.")
            serializer.save()  # If no file is provided, just save the record

