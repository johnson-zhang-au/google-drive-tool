# This file is the implementation of Google Drive agent tool
from dataiku.llm.agent_tools import BaseAgentTool
from utils.logging import logger
from utils.google_drive import GoogleDriveUtils
import json
import os


class GoogleDriveTool(BaseAgentTool):
    def set_config(self, config, plugin_config):
        self.config = config
        self.google_drive_auth = self.config["google_drive_auth"]
        
        # Set up logging
        self.setup_logging()
        
        # Initialize the Google Drive service
        self.initialize_drive_service()

    def setup_logging(self):
        """
        Sets up the logging level.
        """
        # Get the logging level from the configuration, default to INFO
        logging_level = self.config.get("logging_level", "INFO")
        
        # Set the logging level
        logger.set_level(logging_level)

    def initialize_drive_service(self):
        """
        Initialize the Google Drive service.
        """
        try:
            # Get the access token from the configuration
            access_token = self.google_drive_auth["access_token"]
            
            # Create the Drive service using the utility class
            self.drive_service = GoogleDriveUtils.create_drive_service(access_token)
        except Exception as e:
            logger.error(f"Failed to initialize Google Drive service: {str(e)}")
            raise

    def get_descriptor(self, tool):
        logger.debug("Generating descriptor for the Google Drive tool.")
        return {
            "description": "Interacts with Google Drive to search for files, get file details, and download files",
            "inputSchema": {
                "$id": "https://dataiku.com/agents/tools/google-drive/input",
                "title": "Input for the Google Drive tool",
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["search_files", "get_file_details", "download_file", "list_files", "upload_file", "delete_file", "get_file_content"],
                        "description": "The action to perform (search_files, get_file_details, download_file, list_files, upload_file, delete_file, or get_file_content)"
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query for files (required for search_files action)"
                    },
                    "file_id": {
                        "type": "string",
                        "description": "Google Drive file ID (required for get_file_details, download_file, delete_file, and get_file_content actions)"
                    },
                    "mime_type": {
                        "type": "string",
                        "description": "MIME type for file download or export (optional for download_file and get_file_content actions)"
                    },
                    "folder_id": {
                        "type": "string",
                        "description": "Google Drive folder ID (optional for list_files action)"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file (required for upload_file action)"
                    },
                    "page_size": {
                        "type": "integer",
                        "description": "The maximum number of results to return",
                        "default": 10
                    }
                },
                "required": ["action"]
            }
        }

    def invoke(self, input, trace):
        args = input["input"]
        action = args["action"]

        logger.info(f"Invoking action: {action}")
        logger.debug(f"Input arguments: {args}")

        if action == "search_files":
            return self.search_files(args)
        elif action == "get_file_details":
            return self.get_file_details(args)
        elif action == "download_file":
            return self.download_file(args)
        elif action == "list_files":
            return self.list_files(args)
        elif action == "upload_file":
            return self.upload_file(args)
        elif action == "delete_file":
            return self.delete_file(args)
        elif action == "get_file_content":
            return self.get_file_content(args)
        else:
            logger.error(f"Invalid action: {action}")
            raise ValueError(f"Invalid action: {action}")

    def search_files(self, args):
        """
        Search for files in Google Drive.
        
        Args:
            args: Dictionary containing the search query.
            
        Returns:
            Dictionary containing the search results.
        """
        logger.info("Starting 'search_files' action.")
        logger.debug(f"Input arguments: {args}")
        if "query" not in args:
            logger.error("Missing required field: query")
            raise ValueError("Missing required field: query")

        try:
            # Get the search query
            query = args["query"]
            page_size = args.get("page_size", 10)
            
            # Use the utility class to search for files
            formatted_files = GoogleDriveUtils.search_files(self.drive_service, query, page_size)
            
            return {
                "output": {
                    "message": f"Found {len(formatted_files)} files matching the query (requested: {page_size})",
                    "files": formatted_files,
                    "requested_page_size": page_size,
                    "total_results": len(formatted_files)
                }
            }
        except Exception as e:
            logger.error(f"Error searching for files: {str(e)}")
            raise

    def list_files(self, args):
        """
        List files in Google Drive or in a specific folder.
        
        Args:
            args: Dictionary containing the folder ID.
            
        Returns:
            Dictionary containing the list of files.
        """
        logger.info("Starting 'list_files' action.")
        logger.debug(f"Input arguments: {args}")
        try:
            # Get the folder ID if provided
            folder_id = args.get("folder_id")
            page_size = args.get("page_size", 10)
            
            # Use the utility class to list files
            formatted_files = GoogleDriveUtils.list_files(self.drive_service, folder_id, page_size)
            
            return {
                "output": {
                    "message": f"Found {len(formatted_files)} files (requested: {page_size})",
                    "files": formatted_files,
                    "requested_page_size": page_size,
                    "total_results": len(formatted_files)
                }
            }
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            raise

    def get_file_details(self, args):
        """
        Get details of a file in Google Drive.
        
        Args:
            args: Dictionary containing the file ID.
            
        Returns:
            Dictionary containing the file details.
        """
        logger.info("Starting 'get_file_details' action.")
        logger.debug(f"Input arguments: {args}")
        if "file_id" not in args:
            logger.error("Missing required field: file_id")
            raise ValueError("Missing required field: file_id")

        try:
            # Get the file ID
            file_id = args["file_id"]
            
            # Use the utility class to get file details
            file_details = GoogleDriveUtils.get_file_details(self.drive_service, file_id)
            
            return {
                "output": {
                    "message": f"Retrieved details for file: {file_details['name']}",
                    "file": file_details
                }
            }
        except Exception as e:
            logger.error(f"Error getting file details: {str(e)}")
            raise

    def get_file_content(self, args):
        """
        Get the content of a file from Google Drive.
        
        Args:
            args: Dictionary containing the file ID and optional MIME type.
            
        Returns:
            Dictionary containing the file content and metadata.
        """
        logger.info("Starting 'get_file_content' action.")
        logger.debug(f"Input arguments: {args}")
        if "file_id" not in args:
            logger.error("Missing required field: file_id")
            raise ValueError("Missing required field: file_id")

        try:
            # Get the file ID and MIME type
            file_id = args["file_id"]
            mime_type = args.get("mime_type")
            
            # Use the utility class to get file content
            file_data = GoogleDriveUtils.get_file_content(self.drive_service, file_id, mime_type)
            
            return {
                "output": {
                    "message": f"Retrieved content for file: {file_data['file_name']}",
                    "file_name": file_data["file_name"],
                    "mime_type": file_data["mime_type"],
                    "content": file_data["content"]
                }
            }
        except Exception as e:
            logger.error(f"Error getting file content: {str(e)}")
            raise

    def download_file(self, args):
        """
        Download a file from Google Drive.
        
        Args:
            args: Dictionary containing the file ID and optional MIME type.
            
        Returns:
            Dictionary containing the file content and metadata.
        """
        logger.info("Starting 'download_file' action.")
        logger.debug(f"Input arguments: {args}")
        if "file_id" not in args:
            logger.error("Missing required field: file_id")
            raise ValueError("Missing required field: file_id")

        try:
            # Get the file ID and MIME type
            file_id = args["file_id"]
            mime_type = args.get("mime_type")
            
            # Use the utility class to download the file
            file_data = GoogleDriveUtils.download_file(self.drive_service, file_id, mime_type)
            
            return {
                "output": {
                    "message": f"Downloaded file: {file_data['file_name']}",
                    "file_name": file_data["file_name"],
                    "mime_type": file_data["mime_type"],
                    "content": file_data["content"]
                }
            }
        except Exception as e:
            logger.error(f"Error downloading file: {str(e)}")
            raise
            
    def upload_file(self, args):
        """
        Upload a file to Google Drive.
        
        Args:
            args: Dictionary containing the file path and optional folder ID.
            
        Returns:
            Dictionary containing the uploaded file ID.
        """
        logger.info("Starting 'upload_file' action.")
        logger.debug(f"Input arguments: {args}")
        if "file_path" not in args:
            logger.error("Missing required field: file_path")
            raise ValueError("Missing required field: file_path")

        try:
            # Get the file path and folder ID
            file_path = args["file_path"]
            folder_id = args.get("folder_id")
            
            # Use the utility class to upload the file
            file_id = GoogleDriveUtils.upload_file(self.drive_service, file_path, folder_id)
            
            return {
                "output": {
                    "message": f"Uploaded file with ID: {file_id}",
                    "file_id": file_id
                }
            }
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            raise
            
    def delete_file(self, args):
        """
        Delete a file from Google Drive.
        
        Args:
            args: Dictionary containing the file ID.
            
        Returns:
            Dictionary containing the result of the operation.
        """
        logger.info("Starting 'delete_file' action.")
        logger.debug(f"Input arguments: {args}")
        if "file_id" not in args:
            logger.error("Missing required field: file_id")
            raise ValueError("Missing required field: file_id")

        try:
            # Get the file ID
            file_id = args["file_id"]
            
            # Use the utility class to delete the file
            GoogleDriveUtils.delete_file(self.drive_service, file_id)
            
            return {
                "output": {
                    "message": f"Deleted file with ID: {file_id}",
                    "success": True
                }
            }
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            raise

