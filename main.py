from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse, FileResponse
import subprocess
from pathlib import Path

INPUT_DIR = Path("./input")
OUTPUT_DIR = Path("./output")

INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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

        command = [
            "docker", "run", "--rm",
            "-v", f"{INPUT_DIR.resolve()}:/input",
            "-v", f"{OUTPUT_DIR.resolve()}:/output",
            "toprock/audiveris"
        ]
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            return JSONResponse(status_code=500, content={"error": "Audiveris processing failed", "details": result.stderr})

        output_folder_path = OUTPUT_DIR / file.filename.replace(".pdf", "")
        mxl_file_path = output_folder_path / f"{file.filename.replace('.pdf', '.mxl')}"

        if mxl_file_path.exists():
            return FileResponse(mxl_file_path, media_type="application/vnd.recordare.musicxml+xml", filename=mxl_file_path.name)
        else:
            return JSONResponse(status_code=500, content={"error": "MXL file not found in output folder"})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
