from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import glob
import shutil

app = FastAPI(title="Adyson Music API", version="1.0")

# CORS taaki Flutter app connect kar sake
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MUSIC_DIR = "music"

# Agar music folder nahi hai toh bana do
if not os.path.exists(MUSIC_DIR):
    os.makedirs(MUSIC_DIR)

@app.get("/")
def read_root():
    return {"message": "Adyson Backend is running! 🎵"}

# 1. Saare gaano ki list nikalne ke liye
@app.get("/api/songs")
def get_songs():
    songs = []
    for file_path in glob.glob(os.path.join(MUSIC_DIR, "*.mp3")):
        filename = os.path.basename(file_path)
        songs.append({
            "id": filename,
            "title": filename.replace(".mp3", "").replace("_", " ").title(),
            "artist": "Unknown Artist",
            "stream_url": f"/api/stream/{filename}",
            "download_url": f"/api/download/{filename}"
        })
    return {"songs": songs}

# 2. Gaana stream karne ke liye (Online sunne ke liye)
@app.get("/api/stream/{filename}")
def stream_song(filename: str):
    file_path = os.path.join(MUSIC_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Song not found")
    
    # FileResponse automatically HTTP Range requests handle karta hai (streaming ke liye zaroori hai)
    return FileResponse(file_path, media_type="audio/mpeg")

# 3. Gaana download karne ke liye (Offline sunne ke liye)
@app.get("/api/download/{filename}")
def download_song(filename: str):
    file_path = os.path.join(MUSIC_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Song not found")
    
    return FileResponse(
        file_path, 
        media_type="audio/mpeg", 
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# 4. Naya gaana upload karne ke liye (Tere laptop se)
@app.post("/api/upload")
async def upload_song(file: UploadFile = File(...)):
    if not file.filename.endswith(".mp3"):
        raise HTTPException(status_code=400, detail="Only MP3 files allowed")
    
    file_path = os.path.join(MUSIC_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"message": f"Successfully uploaded {file.filename}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.py", host="0.0.0.0", port=8000, reload=True)