# Google Drive Tool Plugin for Dataiku

This Dataiku plugin provides a visual agent tool for interacting with Google Drive. It allows you to search for files, get file details, and download files from your Google Drive.

## Features

- **Search for files**: Search for files in your Google Drive using text queries
- **Get file details**: Retrieve detailed information about a specific file
- **Download files**: Download files from your Google Drive, including Google Docs exported in different formats
- **Upload files**: Upload files to your Google Drive
- **Delete files**: Delete files from your Google Drive
- **Get file content**: Retrieve the content of a file from Google Drive

## Installation

1. Download the plugin ZIP file
2. In Dataiku, go to the Plugins section
3. Click on "Import plugin" and select the downloaded ZIP file
4. Restart Dataiku

## Configuration

### Authentication

The plugin uses OAuth 2.0 for authentication with Google Drive. You need to follow these steps to set it up:

1. **Create a Google Cloud Project**:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project.

2. **Enable the Google Drive API**:
   - In the Google Cloud Console, navigate to the "API & Services" > "Library".
   - Search for "Google Drive API" and enable it for your project.

3. **Configure OAuth Consent Screen**:
   - Go to "API & Services" > "OAuth consent screen".
   - Fill in the required information and save.

4. **Create OAuth 2.0 Credentials**:
   - Navigate to "API & Services" > "Credentials".
   - Click on "Create Credentials" and select "OAuth client ID".
   - Choose "Desktop app" as the application type.
   - Save the generated client ID and client secret.

5. **Configure the Credentials in the Plugin**:
   - In Dataiku, go to the plugin's settings page.
   - Add a preset (Applications > Plugins > Googledrive > Settings > Google Single Sign On).
   - Paste the client ID and client secret generated in the previous step.

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

### Upload Files

To upload a file to Google Drive:

1. Configure the Google Drive authentication
2. Use the "upload_file" action with a file_path parameter
3. Optionally, specify a folder_id to upload the file to a specific folder

### Delete Files

To delete a file from Google Drive:

1. Configure the Google Drive authentication
2. Use the "delete_file" action with a file_id parameter

### Get File Content

To get the content of a file from Google Drive:

1. Configure the Google Drive authentication
2. Use the "get_file_content" action with a file_id parameter
3. Optionally, specify a mime_type parameter

## License

This plugin is licensed under the Apache Software License.

## Support

For support, please contact the plugin author or create an issue in the plugin repository. 