from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import uuid
from pathlib import Path
import shutil
import subprocess

app = FastAPI()

INPUT_DIR = "/input"
OUTPUT_DIR = "/output"

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Serwer działa poprawnie!"}

@app.post("/process")
async def process_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Zapisz plik do katalogu wejściowego
    input_filename = f"{uuid.uuid4()}.pdf"
    input_path = Path(INPUT_DIR) / input_filename
    with open(input_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Wygeneruj nazwę pliku wyjściowego
    output_musicxml = Path(OUTPUT_DIR) / f"{input_path.stem}.musicxml"

    # Sprawdź, czy plik został przetworzony przez Audiveris
    audiveris_command = [
        "/audiveris-extract/bin/Audiveris",
        "-batch",
        "-export",
        "-output", OUTPUT_DIR,
        input_path
    ]

    process = subprocess.run(audiveris_command)
    if process.returncode != 0:
        raise HTTPException(status_code=500, detail="Audiveris processing failed")

    if not output_musicxml.exists():
        raise HTTPException(status_code=500, detail="MusicXML file not generated")

    return FileResponse(output_musicxml, media_type="application/xml", filename=output_musicxml.name)
