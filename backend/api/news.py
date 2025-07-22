import uuid
import os
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, field_validator
from loguru import logger

from services.news_fetcher import NewsFetcher
from agents.signal_detector import SignalDetector

router = APIRouter()

# In-memory storage for job status (in production, use Redis or database)
job_status: Dict[str, Dict] = {}


class JobStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class NewsFetchRequest(BaseModel):
    company_names: List[str]
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


class JobStatus(BaseModel):
    job_id: str
    status: JobStatusEnum
    progress: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    results: Optional[Dict] = None
    error: Optional[str] = None


async def fetch_news_task(job_id: str, company_names: List[str], days_back: int):
    """Background task to fetch news and extract signals for multiple companies"""
    try:
        logger.info(f"Starting news fetch job {job_id} for {len(company_names)} companies")
        
        # Initialize services
        detector = SignalDetector(api_key=os.environ["OPENAI_API_KEY"])
        fetcher = NewsFetcher()

        # Update status to running
        job_status[job_id]["status"] = JobStatusEnum.RUNNING
        job_status[job_id]["progress"] = f"Starting analysis for {len(company_names)} companies..."
        
        all_signals = []
        company_results = {}
        total_articles = 0
        
        for i, company_name in enumerate(company_names):
            try:
                job_status[job_id]["progress"] = f"Scanning {company_name} ({i+1}/{len(company_names)})..."
                logger.info(f"Scanning {company_name}...")
                
                # Fetch articles for this company
                articles = fetcher.fetch_multiple_sources(company_name, days_back)
                total_articles += len(articles)

                # Extract signals from each article
                company_signals = []
                for article in articles:
                    try:
                        signal = detector.extract_with_metadata(
                            company_name, 
                            article["text"], 
                            article["link"], 
                            article["published"]
                        )
                        
                        if signal:
                            signal_dict = signal.model_dump()
                            company_signals.append(signal_dict)
                            all_signals.append(signal_dict)
                            logger.info(f"Found signal for {company_name}: {signal.type.value} - {signal.title}")
                            
                    except Exception as e:
                        logger.warning(f"Failed to extract signal from article for {company_name}: {str(e)}")
                        continue
                
                # Store per-company results
                company_results[company_name] = {
                    "article_count": len(articles),
                    "signal_count": len(company_signals),
                    "signals": company_signals
                }
                
            except Exception as e:
                logger.error(f"Error processing {company_name}: {str(e)}")
                company_results[company_name] = {
                    "article_count": 0,
                    "signal_count": 0,
                    "signals": [],
                    "error": str(e)
                }
        
        # Create signal summary (like demo_runner.py)
        signal_summary = None
        if all_signals:
            # Group signals by type
            by_type = {}
            for signal in all_signals:
                signal_type = signal['type']
                by_type.setdefault(signal_type, []).append(signal)
            
            signal_summary = {
                "total_signals": len(all_signals),
                "total_companies": len(company_names),
                "companies_with_signals": len([c for c in company_results.values() if c["signal_count"] > 0]),
                "by_type": {
                    signal_type: {
                        "count": len(type_signals),
                        "signals": [
                            {
                                "company_name": s["company_name"],
                                "title": s["title"],
                                "action": s["action"],
                                "impact": s["impact"],
                                "confidence": s["confidence"]
                            } 
                            for s in type_signals
                        ]
                    }
                    for signal_type, type_signals in by_type.items()
                }
            }
        
        # Create combined results
        results = {
            "companies": company_results,
            "summary": signal_summary
        }
        
        # Update status to completed
        job_status[job_id]["status"] = JobStatusEnum.COMPLETED
        job_status[job_id]["completed_at"] = datetime.now()
        job_status[job_id]["results"] = results
        
        job_status[job_id]["progress"] = f"Completed! Found {total_articles} articles and {len(all_signals)} signals"
        
        logger.info(f"Completed news fetch job {job_id} - found {total_articles} articles and {len(all_signals)} signals")
        
    except Exception as e:
        logger.error(f"Error in news fetch job {job_id}: {str(e)}")
        job_status[job_id]["status"] = JobStatusEnum.FAILED
        job_status[job_id]["error"] = str(e)
        job_status[job_id]["completed_at"] = datetime.now()

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