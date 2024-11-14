from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse
import os
import subprocess
from pathlib import Path

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
        # Save the uploaded PDF to the input directory
        input_file_path = INPUT_DIR / file.filename
        with open(input_file_path, "wb") as input_file:
            content = await file.read()
            input_file.write(content)

        # Run the audiveris Docker container to process the file
        output_file_path = OUTPUT_DIR / (file.filename + "_output.xml")
        command = [
            "docker", "run", "--rm",
            "-v", f"{INPUT_DIR.resolve()}:/input",
            "-v", f"{OUTPUT_DIR.resolve()}:/output",
            "toprock/audiveris"
        ]
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            return JSONResponse(status_code=500, content={"error": "Audiveris processing failed", "details": result.stderr})

        # Return the processed file
        if output_file_path.exists():
            return FileResponse(output_file_path, media_type="application/mxl", filename=output_file_path.name)
        else:
            return JSONResponse(status_code=500, content={"error": "Output file not found"})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
