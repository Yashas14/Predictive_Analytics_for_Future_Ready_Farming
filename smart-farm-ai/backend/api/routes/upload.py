"""CSV upload for future retraining."""

from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from backend.utils.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/data", tags=["Data"])


@router.post("/upload")
async def upload_data(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """Save a CSV so it can be used for retraining later."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")
    
    try:
        # Save uploaded file
        upload_dir = settings.abs_data_dir / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / file.filename
        content = await file.read()
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info("data_uploaded", filename=file.filename, size_bytes=len(content))
        
        # Optionally trigger retraining in background
        # if background_tasks:
        #     background_tasks.add_task(retrain_model, file_path)
        
        return {
            "status": "success",
            "message": f"File '{file.filename}' uploaded successfully",
            "file_path": str(file_path),
            "size_bytes": len(content),
            "retrain_triggered": False
        }
    
    except Exception as e:
        logger.error("upload_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/datasets")
async def list_datasets():
    """List CSVs available in the data directory."""
    data_dir = settings.abs_data_dir
    
    datasets = []
    if data_dir.exists():
        for f in data_dir.rglob("*.csv"):
            datasets.append({
                "name": f.name,
                "path": str(f.relative_to(data_dir)),
                "size_bytes": f.stat().st_size,
            })
    
    return {"datasets": datasets, "data_dir": str(data_dir)}
