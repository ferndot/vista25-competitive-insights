import os
from datetime import datetime
from loguru import logger

from models.job import JobStatusEnum
from services.news_fetcher import NewsFetcher
from agents.signal_detector import SignalDetector


# In-memory storage for job status (in production, use Redis or database)
job_status: dict[str, dict] = {}

async def fetch_news_task(job_id: str, company_names: list[str], days_back: int):
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
                            article.text, 
                            article.link, 
                            article.published
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