import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, field_validator
from loguru import logger

from models.job import JobStatus, JobStatusEnum
from tasks.news import fetch_news_task, job_status

router = APIRouter()


class NewsFetchRequest(BaseModel):
    company_names: list[str]
    days_back: int = 7
    
    @field_validator('company_names')
    @classmethod
    def validate_company_names(cls, v):
        if not v or len(v) == 0:
            raise ValueError("At least one company name is required")
        if len(v) > 10:
            raise ValueError("Maximum 10 companies allowed")
        return [name.strip() for name in v if name.strip()]
    
    @field_validator('days_back')
    @classmethod
    def validate_days_back(cls, v):
        if v < 1 or v > 30:
            raise ValueError("days_back must be between 1 and 30")
        return v


class NewsFetchResponse(BaseModel):
    job_id: str
    message: str



@router.post("/jobs", response_model=NewsFetchResponse)
async def create_job(request: NewsFetchRequest, background_tasks: BackgroundTasks):
    """Start a news fetching and signal detection job"""
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())

    # Initialize job status
    job_status[job_id] = {
        "job_id": job_id,
        "status": JobStatusEnum.PENDING,
        "progress": "Job queued",
        "created_at": datetime.now(),
    }
    
    # Start background task
    background_tasks.add_task(
        fetch_news_task, 
        job_id, 
        request.company_names, 
        request.days_back
    )
    
    companies_str = ", ".join(request.company_names)
    logger.info(f"Started job {job_id} for companies: {companies_str}")
    
    return NewsFetchResponse(
        job_id=job_id,
        message=f"Analysis started for {len(request.company_names)} companies"
    )


@router.get("/jobs/{job_id}", response_model=JobStatus)
async def get_job(job_id: str):
    """Get the status and results of a job"""
    
    job_id_str = str(job_id)
    if job_id_str not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobStatus(**job_status[job_id_str])


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a job from memory"""
    
    job_id_str = str(job_id)
    if job_id_str not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    del job_status[job_id_str]
    return {"message": "Job deleted successfully"}