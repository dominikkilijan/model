from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse
from starlette.background import BackgroundTask
import os
import subprocess
from pathlib import Path
import uuid

# Define constants for input and output directories
INPUT_DIR = Path("./input")
OUTPUT_DIR = Path("./output")

# Ensure the directories exist
INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Create FastAPI app
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Server is running correctly"}

@app.post("/process")
async def process_pdf(file: UploadFile):
    try:
        # Generate a unique filename using UUID
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        input_file_path = INPUT_DIR / unique_filename

        # Save the uploaded PDF to the input directory
        with open(input_file_path, "wb") as input_file:
            content = await file.read()
            input_file.write(content)

        # Run the audiveris Docker container to process the file
        command = [
            "docker", "run", "--rm",
            "-v", f"{INPUT_DIR.resolve()}:/input",
            "-v", f"{OUTPUT_DIR.resolve()}:/output",
            "toprock/audiveris"
        ]
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            return JSONResponse(status_code=500, content={"error": "Audiveris processing failed", "details": result.stderr})

        # Locate the .mxl file in the output directory
        output_folder_name = unique_filename.replace(".pdf", "")
        output_folder_path = OUTPUT_DIR / output_folder_name
        mxl_file_path = output_folder_path / f"{unique_filename.replace('.pdf', '.mxl')}"

        if mxl_file_path.exists():
            # Define cleanup task
            def cleanup():
                try:
                    os.remove(input_file_path)
                    for file in output_folder_path.iterdir():
                        file.unlink()
                    output_folder_path.rmdir()
                except Exception as e:
                    print(f"Cleanup error: {e}")

            # Send the file as response with background cleanup
            return FileResponse(mxl_file_path, media_type="application/vnd.recordare.musicxml+xml", filename=mxl_file_path.name, background=BackgroundTask(cleanup))
        else:
            return JSONResponse(status_code=500, content={"error": "MXL file not found in output folder"})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
