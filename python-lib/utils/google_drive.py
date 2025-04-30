import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
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
            # Format the search query
            escaped_query = query.replace("'", "\\'")
            formatted_query = f"fullText contains '{escaped_query}'"
            
            # Execute the search
            logger.debug(f"Executing search with query: {formatted_query}")
            results = drive_service.files().list(
                q=formatted_query,
                pageSize=page_size,
                fields="files(id, name, mimeType, modifiedTime, size)"
            ).execute()
            
            files = results.get('files', [])
            logger.info(f"Found {len(files)} files matching the query")
            
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