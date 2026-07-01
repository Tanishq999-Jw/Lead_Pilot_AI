from config.database import SessionLocal
from modules.database.models import ScrapingJob, Campaign
from sqlalchemy.orm import joinedload

JOB_ID = "3d383997-fa50-4637-b043-92e86d484754"

def main():
    db = SessionLocal()
    job = db.query(ScrapingJob).options(joinedload(ScrapingJob.campaign)).filter(ScrapingJob.id == JOB_ID).first()
    if not job:
        print(f"Job {JOB_ID} not found in database.")
        return
    print("--- ScrapingJob ---")
    print(f"ID: {job.id}")
    print(f"Campaign ID: {job.campaign_id}")
    print(f"Campaign Name: {job.campaign.campaign_name if job.campaign else 'N/A'}")
    print(f"Platform: {job.platform}")
    print(f"Category: {job.category}")
    print(f"Location: {job.location}")
    print(f"Status: {job.status}")
    print(f"Limit: {job.limit}")
    print(f"Enable Fallback: {job.enable_fallback}")
    print(f"Raw Queries (count): {len(job.raw_queries) if job.raw_queries else 0}")
    print(f"Total Loaded: {job.total_loaded}")
    print(f"Total Scraped: {job.total_scraped}")
    print(f"Total Saved: {job.total_saved}")
    print(f"Total Duplicates: {job.total_duplicates}")
    print(f"Total Failed: {job.total_failed}")
    print(f"Error Message: {job.error_message}")
    print(f"Started At: {job.started_at}")
    print(f"Completed At: {job.completed_at}")
    print(f"Created At: {job.created_at}")
    print(f"Updated At: {job.updated_at}")
    if job.raw_queries:
        print('\n--- Sample Raw Queries ---')
        for q in job.raw_queries[:10]:
            print(q)

if __name__ == '__main__':
    main()
