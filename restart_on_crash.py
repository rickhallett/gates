import subprocess
import time
import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('supervisor.log'),
        logging.StreamHandler()
    ]
)

def run_script():
    while True:
        try:
            logging.info("Starting main script...")
            # Replace 'main.py' with your script's name
            process = subprocess.run([sys.executable, 'main.py'], check=True)
            if process.returncode != 0:
                logging.error(f"Script exited with code {process.returncode}")
            else:
                logging.info("Script completed successfully")
                
        except subprocess.CalledProcessError as e:
            logging.error(f"Script crashed with error: {e}")
        except Exception as e:
            logging.error(f"Supervisor error: {e}")
            
        logging.info("Restarting in 10 seconds...")
        time.sleep(10)  # Wait before restarting

if __name__ == "__main__":
    run_script() 