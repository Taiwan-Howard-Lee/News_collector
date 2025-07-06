import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScrapingScheduler:
    """Manages automated scraping schedules using APScheduler."""
    
    def __init__(self):
        """Initialize the scheduler."""
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        
    def start(self):
        """Start the scheduler."""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("Scraping scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Scraping scheduler stopped")
    
    def add_scraping_job(self, job_function, schedule_type='cron', **schedule_args):
        """
        Add a scraping job to the scheduler.
        
        Args:
            job_function: Function to execute
            schedule_type: Type of schedule ('cron', 'interval', 'date')
            **schedule_args: Schedule parameters
        """
        try:
            if schedule_type == 'cron':
                trigger = CronTrigger(**schedule_args)
            else:
                trigger = schedule_type
                
            self.scheduler.add_job(
                func=job_function,
                trigger=trigger,
                id=f'scraping_job_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                name='News Scraping Job',
                replace_existing=True
            )
            logger.info(f"Added scraping job with {schedule_type} schedule")
            
        except Exception as e:
            logger.error(f"Error adding scraping job: {e}")
    
    def setup_default_schedule(self, scraping_function):
        """
        Set up the default scraping schedule.
        
        Args:
            scraping_function: Function to execute for scraping
        """
        # Run scraping every 30 minutes during business hours (8 AM - 8 PM)
        self.add_scraping_job(
            job_function=scraping_function,
            schedule_type='cron',
            minute='*/30',
            hour='8-20',
            day_of_week='mon-fri'
        )
        
        # Run once daily at 6 AM for comprehensive update
        self.add_scraping_job(
            job_function=scraping_function,
            schedule_type='cron',
            hour=6,
            minute=0
        )
        
        logger.info("Default scraping schedule configured")
    
    def get_jobs(self):
        """Get all scheduled jobs."""
        return self.scheduler.get_jobs()
    
    def remove_job(self, job_id):
        """Remove a specific job."""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed job: {job_id}")
        except Exception as e:
            logger.error(f"Error removing job {job_id}: {e}")
    
    def pause_job(self, job_id):
        """Pause a specific job."""
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"Paused job: {job_id}")
        except Exception as e:
            logger.error(f"Error pausing job {job_id}: {e}")
    
    def resume_job(self, job_id):
        """Resume a specific job."""
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"Resumed job: {job_id}")
        except Exception as e:
            logger.error(f"Error resuming job {job_id}: {e}")
    
    def get_job_status(self):
        """Get status of all jobs."""
        jobs = self.get_jobs()
        status = []
        
        for job in jobs:
            status.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        
        return status 