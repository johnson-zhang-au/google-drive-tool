# Google Drive Tool Plugin for Dataiku

This Dataiku plugin provides a visual agent tool for interacting with Google Drive. It allows you to search for files, get file details, and download files from your Google Drive.

## Features

- **Search for files**: Search for files in your Google Drive using text queries
- **Get file details**: Retrieve detailed information about a specific file
- **Download files**: Download files from your Google Drive, including Google Docs exported in different formats

## Installation

1. Download the plugin ZIP file
2. In Dataiku, go to the Plugins section
3. Click on "Import plugin" and select the downloaded ZIP file
4. Restart Dataiku

## Configuration

### Authentication

The plugin uses OAuth 2.0 for authentication with Google Drive. You need to:

1. Create a Google Cloud project
2. Enable the Google Drive API
3. Configure OAuth consent screen
4. Create OAuth 2.0 credentials
5. Configure the credentials in the plugin

### Parameter Sets

The plugin includes the following parameter sets:

- **Google Drive Authentication**: Contains the OAuth 2.0 credentials for authenticating with Google Drive

## Usage

### Search for Files

To search for files in your Google Drive:

1. Configure the Google Drive authentication
2. Use the "search_files" action with a query parameter
3. The tool will return a list of files matching the query

### Get File Details

To get details about a specific file:

1. Configure the Google Drive authentication
2. Use the "get_file_details" action with a file_id parameter
3. The tool will return detailed information about the file

### Download Files

To download a file from your Google Drive:

1. Configure the Google Drive authentication
2. Use the "download_file" action with a file_id parameter
3. Optionally, specify a mime_type parameter to export Google Docs in a specific format
4. The tool will return the file content and metadata

## License

This plugin is licensed under the Apache Software License.

## Support

For support, please contact the plugin author or create an issue in the plugin repository. 