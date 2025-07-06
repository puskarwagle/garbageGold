# app/utils/logger.py

import os
from datetime import datetime
from typing import Union
from pprint import pprint
import traceback

LOG_FILE_PATH = os.path.abspath("app/linkedBot/logs/log.txt")

def ensure_log_dir_exists():
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

def log(message: Union[str, dict], pretty: bool = False):
    ensure_log_dir_exists()
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    output = f"{timestamp} {message}"

    try:
        # Print to terminal
        pprint(message) if pretty else print(output)

        # Append to log file
        with open(LOG_FILE_PATH, "a+", encoding="utf-8") as f:
            f.write(output + "\n")

    except Exception as e:
        print("🔥 Failed to write to log file:")
        traceback.print_exc()

def log_error(e: Exception, context: str = "Unknown"):
    ensure_log_dir_exists()
    error_msg = f"[ERROR] {context}: {str(e)}"
    log(error_msg)

    tb = traceback.format_exc()
    with open(LOG_FILE_PATH, "a+", encoding="utf-8") as f:
        f.write(tb + "\n")
