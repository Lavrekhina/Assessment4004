import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/insurance_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

# Create logger
logger = logging.getLogger('insurance_system')

def log_error(error_message, exc_info=None):
    """Log error messages with optional exception info"""
    logger.error(error_message, exc_info=exc_info)

def log_info(info_message):
    """Log informational messages"""
    logger.info(info_message)

def log_debug(debug_message):
    """Log debug messages"""
    logger.debug(debug_message)

def log_warning(warning_message):
    """Log warning messages"""
    logger.warning(warning_message)