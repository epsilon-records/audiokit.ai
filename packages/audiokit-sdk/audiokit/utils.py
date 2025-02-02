import json
import traceback
from .logger import Logger
import os


def sanitize_artist_data(artist_data):
    """Ensure artist data has no None values to prevent processing errors."""
    for key, value in artist_data.items():
        if value is None:
            if isinstance(value, int):
                artist_data[key] = 0
            elif isinstance(value, str):
                artist_data[key] = "N/A"
            elif isinstance(value, list):
                artist_data[key] = []
            elif isinstance(value, dict):
                artist_data[key] = {}
    return artist_data


def handle_report_error(
    e: Exception, model_name: str, artist_data: dict, report_type: str
) -> str:
    """Shared error handler for report generation functions"""
    error_details = {
        "error": str(e),
        "traceback": traceback.format_exc(),
        "model": model_name,
        "artist_data": artist_data.get("stage_name", "Unknown Artist"),
        "report_type": report_type,
    }
    Logger.warning(
        f"Failed to generate {report_type}: {json.dumps(error_details, indent=2)}"
    )
    return f"{report_type} generation failed: {str(e)}"


async def save_emails_to_file(
    content: str, artist_name_slug: str, email_dir: str
) -> bool:
    """Save formatted emails to individual files.

    Each email must have both a To: and Subject: line to be considered valid.
    Emails are split based on the To: header marker.
    """
    try:
        os.makedirs(email_dir, exist_ok=True)
        Logger.info(f"Processing emails for {artist_name_slug}")

        # Split on email headers, preserving the header
        emails = []
        current_email = []
        lines = content.split("\n")

        for line in lines:
            if "**To:**" in line and current_email:
                # Found new email header, save previous email
                emails.append("\n".join(current_email))
                current_email = []
            current_email.append(line)

        # Add the last email if exists
        if current_email:
            emails.append("\n".join(current_email))

        valid_count = 0
        for idx, email in enumerate(emails, 1):
            if not email.strip():
                continue

            # Validate email has required headers
            if "**To:**" not in email or "**Subject:**" not in email:
                Logger.warning(
                    f"Skipping invalid email {idx} - missing required headers"
                )
                continue

            # Extract agency name from email
            agency_name = "unknown_agency"
            email_lines = email.split("\n")
            for line in email_lines:
                if "**To:**" in line:
                    email_part = line.split("**To:**")[1].strip()
                    if "@" in email_part:
                        domain = email_part.split("@")[1].split()[0].strip()
                        agency_name = domain.split(".")[0].replace("-", "_")
                        break

            filename = os.path.join(
                email_dir, f"{artist_name_slug}_booking_{agency_name}_{idx}.txt"
            )

            with open(filename, "w") as f:
                f.write(email.strip())
            valid_count += 1
            Logger.success(f"Saved valid email {idx} to {filename}")

        if valid_count == 0:
            Logger.warning("No valid emails found to save")
            return False

        Logger.success(f"Successfully saved {valid_count} valid emails to {email_dir}")
        return True

    except Exception as e:
        Logger.error(f"Failed to save emails: {str(e)}")
        return False
