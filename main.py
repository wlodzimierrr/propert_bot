import time
import schedule
import subprocess
import os
import logging
from datetime import datetime, time as dtime

# Set up logging
def setup_logging():
    logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    log_file = os.path.join(logs_dir, f'property_alerts_{datetime.now().strftime("%Y-%m-%d")}.log')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def is_within_operating_hours():
    current_time = datetime.now().time()
    start_time = dtime(7, 0)  # 7 AM
    end_time = dtime(19, 0)   # 7 PM
    return start_time <= current_time <= end_time

def run_scraper():
    try:
        logging.info("Starting property scraper...")
        app_dir = os.path.abspath(os.path.dirname(__file__))
        scraper_path = os.path.join(app_dir, 'scraper.py')
        
        subprocess.run(['python', scraper_path], check=True)
        logging.info("Property scraper completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running scraper: {e}")
        return False

def run_sort():
    try:
        logging.info("Starting property sorter...")
        app_dir = os.path.abspath(os.path.dirname(__file__))
        sort_path = os.path.join(app_dir, 'sort.py')
        
        subprocess.run(['python', sort_path], check=True)
        logging.info("Property sorter completed successfully")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running sorter: {e}")

def job():
    if not is_within_operating_hours():
        logging.info("Outside operating hours (7 AM - 7 PM). Skipping job.")
        return
    
    logging.info("Starting scheduled job...")
    if run_scraper():
        run_sort()
    else:
        logging.error("Skipping sort.py due to scraper failure")
    
    logging.info("Scheduled job completed")

def main():
    setup_logging()
    logging.info("Property alerts system starting...")
    
    # Schedule the job to run every 15 minutes
    schedule.every(15).minutes.do(job)
    
    # Run the job immediately if within operating hours
    if is_within_operating_hours():
        job()
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
            time.sleep(300)

if __name__ == "__main__":
    main()