import uuid
import logging
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from api.auth import DEBUG_MODE

router = APIRouter(tags=["System"])
logger = logging.getLogger(__name__)
UPLOAD_DIR = Path("backend/static/uploads")

@router.get("/health")
async def health_check():
    return {"status": "ok", "debug": DEBUG_MODE}

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    MAX_SIZE = 30 * 1024 * 1024
    try:
        content = await file.read()
        if len(content) > MAX_SIZE:
            raise HTTPException(status_code=413, detail="Файл слишком большой (макс. 30Мб)")
        
        ext = file.filename.split('.')[-1] if '.' in file.filename else 'file'
        new_filename = f"{uuid.uuid4()}.{ext}"
        
        file_path = UPLOAD_DIR / new_filename
        with open(file_path, "wb") as buffer:
            buffer.write(content)
            
        logger.info(f"Файл загружен: {file.filename} -> {new_filename}")
        return {
            "filename": file.filename,
            "file_url": f"/static/uploads/{new_filename}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка загрузки файла: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при сохранении файла")
