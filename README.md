# Project Description

This project is a backend service designed for processing PDF files containing sheet music. The service uses [Audiveris](https://github.com/Audiveris/audiveris), an open-source Optical Music Recognition (OMR) software, to convert uploaded PDFs into MusicXML files that can be downloaded by users.

## How It Works
- Users upload PDF files via the web interface.
- The service runs the [Audiveris Docker image](https://hub.docker.com/r/toprock/audiveris) to process the files.
- The generated MusicXML files are sent back to the user for download.

## Prerequisites
- Docker must be installed and running on your system.
- The `toprock/audiveris` Docker image must be pulled beforehand. You can do this by running:
  ```bash
  docker pull toprock/audiveris
  ```

## Usage
1. Clone this repository.
2. Ensure Docker is installed and the `toprock/audiveris` image is available.
3. Run the application using:
   ```bash
   uvicorn main:app --reload
   ```
4. Access the service at `http://127.0.0.1:8000`.

## License
This project uses [Audiveris](https://github.com/Audiveris/audiveris), which is licensed under the GNU Affero General Public License (AGPL) version 3. To comply with the AGPL, we provide information on how to access the original Audiveris source code [here](https://github.com/Audiveris/audiveris).

The source code for this backend service is also included in this repository under the AGPL license.
