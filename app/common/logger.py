import logging
import os 
from datetime import datetime

LOGS_PATH='logs_data'
os.makedirs(LOGS_PATH,exist_ok=True)

LOGS_FILE=os.path.join(
    LOGS_PATH,
    f"logs_{datetime.now().strftime("%Y -%m -%d")}.log"
)

logging.basicConfig(filename=LOGS_FILE,
                    format="%(asctime)s -%(levelname)s -%(message)s",
                    level=logging.INFO)

def get_logger(name):
    logger=logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger
