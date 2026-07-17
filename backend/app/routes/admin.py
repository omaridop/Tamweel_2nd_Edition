import os
from tempfile import NamedTemporaryFile
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, UploadFile, File
from app.main import get_current_user, logger
from app.knowledge_ingester import ingest_document

# Upload validation constants
_ALLOWED_EXTENSIONS = {".pdf", ".txt"}
_MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

router = APIRouter()

@router.post("/api/v1/admin/upload-policy")
async def upload_policy(background_tasks: BackgroundTasks, file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """
    Receives a policy document, saves it temporarily, and queues it for ingestion.
    """
    try:
        # Enforce sponsor/admin-only access
        if current_user.get("role") != "sponsor":
            raise HTTPException(status_code=403, detail="Admin access required to upload policy documents.")

        suffix = os.path.splitext(file.filename or "")[1].lower()
        if suffix not in _ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Unsupported file type '{suffix}'. Only PDF and TXT are accepted.")

        # Enforce max file size (10 MB)
        content = await file.read()
        if len(content) > _MAX_FILE_SIZE_BYTES:
            raise HTTPException(status_code=413, detail="File too large. Maximum allowed size is 10 MB.")

        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)  # content already read above
            tmp_path = tmp.name
        
        # Ingest the document in the background to not block the response
        def safe_ingest_document(file_path: str, original_filename: str):
            try:
                file_size = os.path.getsize(file_path)
                logger.info(f"Starting background ingestion for {original_filename} (size: {file_size} bytes)")
                ingest_document(file_path)
            except Exception as e:
                logger.error(f"Background ingestion failed for {original_filename}", exc_info=True)

        background_tasks.add_task(safe_ingest_document, tmp_path, file.filename)
        
        return {"message": "File upload started and queued for ingestion", "filename": file.filename}
    except Exception as e:
        logger.error(f"Upload Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to upload policy")
