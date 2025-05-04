#!/usr/bin/env python3
import logging
from gui.main import InsuranceSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Run the insurance system application"""
    try:
        app = InsuranceSystem()
        app.run()
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise

if __name__ == "__main__":
    main() 