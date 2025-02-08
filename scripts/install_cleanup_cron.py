#!/usr/bin/env python3
"""
Cron Job Installer for Context File Cleanup

This script:
1. Creates a cron job to run cleanup_expired_bypasses.py
2. Sets up logging for the cron job
3. Configures appropriate permissions
"""

import os
import sys
import stat
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("cron_setup.log"), logging.StreamHandler()],
)


def create_wrapper_script():
    """Create a wrapper script that sets up the environment for the cron job."""
    workspace_dir = os.getcwd()
    wrapper_path = os.path.join(workspace_dir, "scripts", "cleanup_wrapper.sh")

    wrapper_content = f"""#!/bin/bash
cd {workspace_dir}
export PATH=/usr/local/bin:$PATH
python3 scripts/cleanup_expired_bypasses.py >> logs/cleanup.log 2>&1
"""

    try:
        # Create logs directory
        os.makedirs(os.path.join(workspace_dir, "logs"), exist_ok=True)

        # Write wrapper script
        with open(wrapper_path, "w") as f:
            f.write(wrapper_content)

        # Make wrapper executable
        os.chmod(wrapper_path, stat.S_IRWXU)

        logging.info(f"Created wrapper script at {wrapper_path}")
        return wrapper_path
    except Exception as e:
        logging.error(f"Failed to create wrapper script: {str(e)}")
        raise


def install_cron_job(wrapper_path):
    """Install the cron job to run every hour."""
    cron_command = f"0 * * * * {wrapper_path}"

    try:
        # Get existing crontab
        existing_crontab = subprocess.check_output(["crontab", "-l"]).decode()
    except subprocess.CalledProcessError:
        existing_crontab = ""

    # Check if job already exists
    if wrapper_path in existing_crontab:
        logging.info("Cron job already installed")
        return

    # Add new job
    new_crontab = existing_crontab.strip() + f"\n{cron_command}\n"

    try:
        # Write new crontab
        process = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE)
        process.communicate(new_crontab.encode())

        if process.returncode == 0:
            logging.info("Successfully installed cron job")
        else:
            raise Exception(f"Crontab process returned code {process.returncode}")
    except Exception as e:
        logging.error(f"Failed to install cron job: {str(e)}")
        raise


def verify_installation():
    """Verify that the cron job was installed correctly."""
    try:
        crontab = subprocess.check_output(["crontab", "-l"]).decode()
        if "cleanup_wrapper.sh" in crontab:
            logging.info("Verified cron job installation")
            return True
        else:
            logging.error("Cron job not found in crontab")
            return False
    except Exception as e:
        logging.error(f"Failed to verify cron job: {str(e)}")
        return False


def main():
    try:
        print("Setting up cleanup cron job...")

        # Create wrapper script
        wrapper_path = create_wrapper_script()

        # Install cron job
        install_cron_job(wrapper_path)

        # Verify installation
        if verify_installation():
            print("\nCron job successfully installed!")
            print("Cleanup will run every hour")
            print("Logs will be written to: logs/cleanup.log")
        else:
            print("\nFailed to verify cron job installation")
            sys.exit(1)

    except Exception as e:
        print(f"\nError setting up cron job: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
