import subprocess
import time
import sys
import logging
from modules.config import create_client
# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/supervisor.log'),
        logging.StreamHandler()
    ]
)

client = create_client()

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
            error = e
        except Exception as e:
            logging.error(f"Supervisor error: {e}")
            error = e
            
        client.send_message({
                "type": "stream",
                "to": "gates",
                "topic": "status",
                "content": f"Script crashed with error: {error}.\nRestarting script in 10 seconds..."
            })
          
        logging.info("Restarting in 10 seconds...")
        time.sleep(10)  # Wait before restarting

if __name__ == "__main__":
    run_script() 