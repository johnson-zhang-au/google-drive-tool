import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from io import BytesIO
from utils.logging import logger

class GoogleDriveUtils:
    """
    Utility class for interacting with Google Drive.
    """
    
    @staticmethod
    def create_drive_service(access_token):
        """
        Create a Google Drive service.
        
        Args:
            access_token: The OAuth 2.0 access token.
            
        Returns:
            A Google Drive service object.
        """
        try:
            # Create credentials object
            credentials = Credentials(access_token)
            
            # Build the Drive API service
            drive_service = build('drive', 'v3', credentials=credentials)
            logger.info("Google Drive service created successfully")
            return drive_service
        except Exception as e:
            logger.error(f"Failed to create Google Drive service: {str(e)}")
            raise
    
    @staticmethod
    def search_files(drive_service, query, page_size=10):
        """
        Search for files in Google Drive.
        
        Args:
            drive_service: The Google Drive service.
            query: The search query.
            page_size: The maximum number of results to return.
            
        Returns:
            A list of files matching the query.
        """
        try:
            # Execute the search with the original query
            logger.debug(f"Executing search with query: {query}, page_size: {page_size}")
            results = drive_service.files().list(
                q=query,
                pageSize=page_size,
                fields="files(id, name, mimeType, modifiedTime, size)"
            ).execute()
            
            files = results.get('files', [])
            logger.info(f"Found {len(files)} files matching the query (requested: {page_size})")
            
            # Format the results
            formatted_files = []
            for file in files:
                formatted_files.append({
                    "id": file.get('id'),
                    "name": file.get('name'),
                    "mime_type": file.get('mimeType'),
                    "modified_time": file.get('modifiedTime'),
                    "size": file.get('size')
                })
            
            return formatted_files
        except Exception as e:
            logger.error(f"Error searching for files: {str(e)}")
            raise
    
    @staticmethod
    def list_files(drive_service, folder_id=None, page_size=10):
        """
        List files in Google Drive or in a specific folder.
        
        Args:
            drive_service: The Google Drive service.
            folder_id: The ID of the folder to list files from (optional).
            page_size: The maximum number of results to return.
            
        Returns:
            A list of files in the specified folder or root.
        """
        try:
            # Build the query
            query = f"'{folder_id}' in parents" if folder_id else None
            
            # Execute the list operation
            logger.debug(f"Listing files with folder_id: {folder_id}, page_size: {page_size}")
            results = drive_service.files().list(
                q=query,
                pageSize=page_size,
                fields="files(id, name, mimeType, modifiedTime, size)"
            ).execute()
            
            files = results.get('files', [])
            logger.info(f"Found {len(files)} files (requested: {page_size})")
            
            # Format the results
            formatted_files = []
            for file in files:
                formatted_files.append({
                    "id": file.get('id'),
                    "name": file.get('name'),
                    "mime_type": file.get('mimeType'),
                    "modified_time": file.get('modifiedTime'),
                    "size": file.get('size')
                })
            
            return formatted_files
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            raise
    
    @staticmethod
    def get_file_details(drive_service, file_id):
        """
        Get details of a file in Google Drive.
        
        Args:
            drive_service: The Google Drive service.
            file_id: The ID of the file.
            
        Returns:
            A dictionary containing the file details.
        """
        try:
            # Get the file details
            logger.debug(f"Getting details for file with ID: {file_id}")
            file = drive_service.files().get(
                fileId=file_id,
                fields="id, name, mimeType, modifiedTime, size, description, webViewLink"
            ).execute()
            
            logger.info(f"Retrieved details for file: {file.get('name')}")
            
            # Format the file details
            file_details = {
                "id": file.get('id'),
                "name": file.get('name'),
                "mime_type": file.get('mimeType'),
                "modified_time": file.get('modifiedTime'),
                "size": file.get('size'),
                "description": file.get('description'),
                "web_view_link": file.get('webViewLink')
            }
            
            return file_details
        except Exception as e:
            logger.error(f"Error getting file details: {str(e)}")
            raise
    
    @staticmethod
    def get_file_content(drive_service, file_id, mime_type=None):
        """
        Get the content of a text-based file from Google Drive.
        Supports text files and Google Apps documents (excluding drawings).
        
        Args:
            drive_service: The Google Drive service.
            file_id: The ID of the file.
            mime_type: The MIME type for exporting Google Docs (optional).
            
        Returns:
            A dictionary containing the file content and metadata.
        """
        try:
            # Get the file details first
            logger.debug(f"Getting details for file with ID: {file_id}")
            file = drive_service.files().get(
                fileId=file_id,
                fields="id, name, mimeType"
            ).execute()
            
            file_name = file.get('name')
            file_mime_type = file.get('mimeType')
            
            # Check if the file is a Google Apps document (excluding drawings)
            is_google_app = file_mime_type.startswith('application/vnd.google-apps')
            is_drawing = file_mime_type == 'application/vnd.google-apps.drawing'
            
            # Check if the file is a text-based file
            is_text = file_mime_type.startswith('text/') or file_mime_type in [
                'application/json',
                'application/xml',
                'application/javascript',
                'application/x-yaml',
                'application/x-httpd-php',
                'application/x-sh',
                'application/x-python',
                'application/x-ruby',
                'application/x-java',
                'application/x-c++',
                'application/x-csharp',
                'application/x-html',
                'application/x-css',
                'application/x-markdown',
                'application/x-csv',
                'application/x-tsv',
                'application/x-tex',
                'application/x-latex',
                'application/x-rtf',
                'application/x-plain'
            ]
            
            # If not a text file or Google App (or is a drawing), raise an error
            if not (is_text or (is_google_app and not is_drawing)):
                raise ValueError(f"File type {file_mime_type} is not supported. Only text files and Google Apps documents (excluding drawings) are supported.")
            
            # If a specific MIME type is requested and the file is a Google Doc, export it
            if is_google_app:
                # Determine the export MIME type based on the Google App type
                if mime_type:
                    export_mime_type = mime_type
                else:
                    if file_mime_type == "application/vnd.google-apps.document":
                        export_mime_type = "text/markdown"
                    elif file_mime_type == "application/vnd.google-apps.spreadsheet":
                        export_mime_type = "text/csv"
                    elif file_mime_type == "application/vnd.google-apps.presentation":
                        export_mime_type = "text/plain"
                    else:
                        export_mime_type = "text/plain"
                
                logger.debug(f"Exporting Google Doc with ID {file_id} as {export_mime_type}")
                content = drive_service.files().export(
                    fileId=file_id,
                    mimeType=export_mime_type
                ).execute()
                
                # For text-based MIME types, convert to string
                if export_mime_type.startswith('text/'):
                    content = content.decode('utf-8')
            else:
                # Download the file content
                logger.debug(f"Downloading file with ID: {file_id}")
                request = drive_service.files().get_media(fileId=file_id)
                file_content = BytesIO()
                downloader = MediaIoBaseDownload(file_content, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                
                content = file_content.getvalue()
                
                # For text-based MIME types, convert to string
                if is_text:
                    content = content.decode('utf-8')
            
            logger.info(f"Retrieved content for file: {file_name}")
            
            return {
                "file_name": file_name,
                "mime_type": mime_type or file_mime_type,
                "content": content
            }
        except Exception as e:
            logger.error(f"Error getting file content: {str(e)}")
            raise
    
    @staticmethod
    def download_file(drive_service, file_id, mime_type=None):
        """
        Download a file from Google Drive.
        
        Args:
            drive_service: The Google Drive service.
            file_id: The ID of the file.
            mime_type: The MIME type for exporting Google Docs.
            
        Returns:
            A dictionary containing the file content and metadata.
        """
        try:
            # Get the file details first
            logger.debug(f"Getting details for file with ID: {file_id}")
            file = drive_service.files().get(
                fileId=file_id,
                fields="id, name, mimeType"
            ).execute()
            
            file_name = file.get('name')
            file_mime_type = file.get('mimeType')
            
            # If a specific MIME type is requested and the file is a Google Doc, export it
            if mime_type and file_mime_type.startswith('application/vnd.google-apps'):
                logger.debug(f"Exporting Google Doc with ID {file_id} as {mime_type}")
                content = drive_service.files().export(
                    fileId=file_id,
                    mimeType=mime_type
                ).execute()
                
                # For text-based MIME types, convert to string
                if mime_type.startswith('text/') or mime_type == 'application/json':
                    content = content.decode('utf-8')
            else:
                # Download the file content
                logger.debug(f"Downloading file with ID: {file_id}")
                request = drive_service.files().get_media(fileId=file_id)
                file_content = BytesIO()
                downloader = MediaIoBaseDownload(file_content, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                
                content = file_content.getvalue()
                
                # For text-based MIME types, convert to string
                if file_mime_type.startswith('text/') or file_mime_type == 'application/json':
                    content = content.decode('utf-8')
            
            logger.info(f"Downloaded file: {file_name}")
            
            return {
                "file_name": file_name,
                "mime_type": mime_type or file_mime_type,
                "content": content
            }
        except Exception as e:
            logger.error(f"Error downloading file: {str(e)}")
            raise
    
    @staticmethod
    def upload_file(drive_service, file_path, folder_id=None):
        """
        Upload a file to Google Drive.
        
        Args:
            drive_service: The Google Drive service.
            file_path: The path to the file to upload.
            folder_id: The ID of the folder to upload to (optional).
            
        Returns:
            The ID of the uploaded file.
        """
        try:
            # Create file metadata
            file_metadata = {'name': os.path.basename(file_path)}
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Create media
            media = MediaFileUpload(file_path, resumable=True)
            
            # Upload the file
            logger.debug(f"Uploading file: {file_path}")
            file = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            file_id = file.get('id')
            logger.info(f"Uploaded file with ID: {file_id}")
            
            return file_id
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            raise
    
    @staticmethod
    def delete_file(drive_service, file_id):
        """
        Delete a file from Google Drive.
        
        Args:
            drive_service: The Google Drive service.
            file_id: The ID of the file to delete.
            
        Returns:
            True if the file was deleted successfully.
        """
        try:
            # Delete the file
            logger.debug(f"Deleting file with ID: {file_id}")
            drive_service.files().delete(fileId=file_id).execute()
            logger.info(f"Deleted file with ID: {file_id}")
            
            return True
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            raise 