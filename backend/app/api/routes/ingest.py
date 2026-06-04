import os
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.dependencies import get_ingestion_pipeline
from app.config import settings
from app.core.models import FileType, IngestionJob
from app.services.ingestion.pipeline import IngestionPipeline
from app.utils.logging import get_logger
from app.utils.security import SecurityValidator

router = APIRouter()
logger = get_logger(__name__)


@router.post("/ingest", response_model=IngestionJob)
async def ingest_file(
    file: UploadFile = File(...),
    pipeline: IngestionPipeline = Depends(get_ingestion_pipeline),
) -> IngestionJob:
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")

        SecurityValidator.validate_file_type(file.filename, settings.allowed_file_types)

        file_extension = file.filename.split(".")[-1].lower()
        if file_extension == "pdf":
            file_type = FileType.PDF
        elif file_extension in ["mp3", "wav"]:
            file_type = FileType.AUDIO
        elif file_extension in ["csv", "xlsx", "xls"]:
            file_type = FileType.SPREADSHEET
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_extension}")

        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_path = upload_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info("file_uploaded", filename=file.filename, size=file.size)

        job = await pipeline.ingest_file(str(file_path), file_type)

        return job

    except HTTPException:
        raise
    except Exception as e:
        logger.error("file_upload_failed", filename=file.filename, error=str(e))
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


@router.post("/ingest-sample-data")
async def ingest_sample_data(
    pipeline: IngestionPipeline = Depends(get_ingestion_pipeline),
) -> dict:
    try:
        sample_dir = Path(settings.sample_data_dir)
        if not sample_dir.exists():
            raise HTTPException(status_code=404, detail="Sample data directory not found")

        jobs = []

        pdf_dir = sample_dir / "pdfs"
        if pdf_dir.exists():
            for pdf_file in pdf_dir.glob("*.pdf"):
                job = await pipeline.ingest_file(str(pdf_file), FileType.PDF)
                jobs.append(job)

        audio_dir = sample_dir / "audio"
        if audio_dir.exists():
            for audio_file in audio_dir.glob("*.mp3"):
                job = await pipeline.ingest_file(str(audio_file), FileType.AUDIO)
                jobs.append(job)

        spreadsheet_dir = sample_dir / "spreadsheets"
        if spreadsheet_dir.exists():
            for sheet_file in list(spreadsheet_dir.glob("*.xlsx")) + list(
                spreadsheet_dir.glob("*.csv")
            ):
                job = await pipeline.ingest_file(str(sheet_file), FileType.SPREADSHEET)
                jobs.append(job)

        logger.info("sample_data_ingested", jobs=len(jobs))

        return {
            "message": f"Ingested {len(jobs)} sample files",
            "jobs": [job.model_dump() for job in jobs],
        }

    except Exception as e:
        logger.error("sample_data_ingestion_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Sample data ingestion failed: {str(e)}")
