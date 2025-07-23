import os
import requests
from datetime import datetime, timedelta
from loguru import logger

from models.model import Result, SourceType
from .base import DataSource


class RapidAPIJobsSource(DataSource):
    """RapidAPI Jobs data source for employment-related business signals"""
    
    platform_name = "RapidAPI Jobs"
    platform_id = "rapidapi_jobs"
    
    def get_headers(self):
        return {
            "x-rapidapi-key": os.environ.get("RAPIDAPI_KEY"),
            "x-rapidapi-host": "jsearch.p.rapidapi.com"
        }
    
    def fetch(self, company_name: str, days_back: int = 7) -> list[Result]:
        """Fetch recent job postings for a company as business signals"""
        logger.info(f"Fetching job data for {company_name} from RapidAPI Jobs")
        
        try:
            # Search for jobs at the company
            jobs_data = self.search_jobs(company_name, page=1)
            
            if not jobs_data or 'data' not in jobs_data:
                logger.warning(f"No job data found for {company_name}")
                return []
            
            results = []
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            for job in jobs_data.get('data', [])[:10]:  # Limit to first 10 jobs
                try:
                    # Parse job posted date
                    job_posted_date = self._parse_job_date(job.get('job_posted_at_datetime_utc'))
                    
                    if not job_posted_date or job_posted_date < cutoff_date:
                        continue
                    
                    # Create descriptive text for signal analysis
                    text_parts = []
                    if job.get('job_title'):
                        text_parts.append(f"Job Title: {job['job_title']}")
                    if job.get('employer_name'):
                        text_parts.append(f"Company: {job['employer_name']}")
                    if job.get('job_description'):
                        cleaned_desc = self._clean_html(job['job_description'])
                        text_parts.append(f"Description: {cleaned_desc[:500]}")  # Limit description length
                    if job.get('job_employment_type'):
                        text_parts.append(f"Employment Type: {job['job_employment_type']}")
                    if job.get('job_city') and job.get('job_state'):
                        text_parts.append(f"Location: {job['job_city']}, {job['job_state']}")
                    
                    full_text = ". ".join(text_parts)
                    
                    result = Result(
                        title=job.get('job_title', f'Job at {company_name}'),
                        link=job.get('job_apply_link', ''),
                        published=job.get('job_posted_at_datetime_utc', ''),
                        published_on=job_posted_date,
                        source_type=SourceType.industry,  # Job postings are industry signals
                        text=full_text,
                        platform=self.platform_id,
                        platform_name=self.platform_name
                    )
                    
                    results.append(result)
                    
                except Exception as e:
                    logger.debug(f"Error processing job posting: {e}")
                    continue
            
            logger.info(f"Found {len(results)} recent job postings for {company_name}")
            return results
            
        except Exception as e:
            logger.error(f"Error fetching job data for {company_name}: {e}")
            return []
    
    def _parse_job_date(self, date_string):
        """Parse job posted date from various formats"""
        if not date_string:
            return None
            
        try:
            # Try ISO format first
            if 'T' in date_string:
                dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
                # Convert to naive datetime (remove timezone info)
                return dt.replace(tzinfo=None)
            
            # Try other common formats
            from dateutil import parser as date_parser
            dt = date_parser.parse(date_string)
            # Convert to naive datetime if it has timezone info
            if dt.tzinfo is not None:
                dt = dt.replace(tzinfo=None)
            return dt
            
        except Exception:
            return None
    
    def get_company_salary(self, company, job_title):
        """Get salary data for a company and job title"""
        url = "https://jsearch.p.rapidapi.com/company-job-salary"
        params = {
            "company": company,
            "job_title": job_title,
            "location_type": "ANY",
            "years_of_experience": "ALL"
        }
        return requests.get(url, headers=self.get_headers(), params=params).json()
    
    def get_estimated_salary(self, job_title, location):
        """Get estimated salary for a job title and location"""
        url = "https://jsearch.p.rapidapi.com/estimated-salary"
        params = {
            "job_title": job_title,
            "location": location,
            "location_type": "ANY",
            "years_of_experience": "ALL"
        }
        return requests.get(url, headers=self.get_headers(), params=params).json()
    
    def get_job_details(self, job_id):
        """Get detailed information about a specific job"""
        url = "https://jsearch.p.rapidapi.com/job-details"
        params = {
            "job_id": job_id,
            "country": "us"
        }
        return requests.get(url, headers=self.get_headers(), params=params).json()
    
    def search_jobs(self, query, page=1):
        """Search for jobs matching a query"""
        url = "https://jsearch.p.rapidapi.com/search"
        params = {
            "query": query,
            "page": str(page),
            "num_pages": "1",
            "country": "us",
            "date_posted": "all"
        }
        return requests.get(url, headers=self.get_headers(), params=params).json()
