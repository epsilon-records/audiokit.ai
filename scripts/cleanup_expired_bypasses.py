#!/usr/bin/env python3
"""
Cleanup Script for Expired Emergency Bypasses

This script:
1. Checks for expired emergency bypasses
2. Logs them to MAINTENANCE.md
3. Removes expired bypass files
4. Can be run as a cron job
"""

import os
import sys
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("bypass_cleanup.log"), logging.StreamHandler()],
)


def append_to_maintenance_log(expired_bypass):
    """Add expired bypass info to MAINTENANCE.md."""
    maintenance_file = os.path.join(os.getcwd(), "context", "MAINTENANCE.md")
    entry = f"""
## Emergency Bypass Expired and Cleaned
- **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Original Reason**: {expired_bypass.get('reason', 'Unknown')}
- **Created By**: {expired_bypass.get('created_by', 'Unknown')}
- **Created At**: {expired_bypass.get('created_at', 'Unknown')}
- **Expired At**: {expired_bypass.get('expiry', 'Unknown')}
"""

    try:
        with open(maintenance_file, "a") as f:
            f.write(entry)
        logging.info(f"Added expired bypass info to {maintenance_file}")
    except Exception as e:
        logging.error(f"Failed to update MAINTENANCE.md: {str(e)}")


def cleanup_expired_bypasses():
    """Check and remove expired emergency bypasses."""
    bypass_file = os.path.join(os.getcwd(), "context", ".emergency_bypass")

    if not os.path.exists(bypass_file):
        logging.info("No emergency bypass file found")
        return

    try:
        with open(bypass_file, "r") as f:
            bypass_data = json.load(f)

        if not bypass_data.get("active", False):
            logging.info("Bypass is already inactive")
            os.remove(bypass_file)
            return

        expiry = datetime.fromisoformat(bypass_data.get("expiry", ""))

        if expiry <= datetime.now():
            logging.info(f"Found expired bypass from {bypass_data.get('created_at')}")
            append_to_maintenance_log(bypass_data)
            os.remove(bypass_file)
            logging.info("Removed expired bypass file")
        else:
            logging.info(f"Bypass is still active until {expiry}")

    except (json.JSONDecodeError, ValueError) as e:
        logging.error(f"Error reading bypass file: {str(e)}")
        os.remove(bypass_file)
        logging.info("Removed invalid bypass file")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")


def main():
    try:
        cleanup_expired_bypasses()
    except Exception as e:
        logging.error(f"Failed to clean up bypasses: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
