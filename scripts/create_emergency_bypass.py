#!/usr/bin/env python3
"""
Emergency Bypass Manager

Creates or updates an emergency bypass for context file validation.
Usage: python3 create_emergency_bypass.py <hours> <reason>
Example: python3 create_emergency_bypass.py 24 "Urgent hotfix deployment"
"""

import os
import sys
import json
from datetime import datetime, timedelta


def create_emergency_bypass(hours, reason):
    """Create an emergency bypass that expires after specified hours."""
    bypass_file = os.path.join(os.getcwd(), "context", ".emergency_bypass")
    expiry = datetime.now() + timedelta(hours=hours)

    bypass_data = {
        "active": True,
        "expiry": expiry.isoformat(),
        "reason": reason,
        "created_at": datetime.now().isoformat(),
        "created_by": os.environ.get("USER", "unknown"),
    }

    # Create context directory if it doesn't exist
    os.makedirs(os.path.join(os.getcwd(), "context"), exist_ok=True)

    # Write bypass file
    with open(bypass_file, "w") as f:
        json.dump(bypass_data, f, indent=2)

    print("Emergency bypass created:")
    print(f"- Expires: {expiry}")
    print(f"- Reason: {reason}")
    print("\nDon't forget to:")
    print("1. Document this bypass in MAINTENANCE.md")
    print("2. Create a ticket to review changes after the emergency")
    print("3. Remove the bypass once the emergency is resolved")


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 create_emergency_bypass.py <hours> <reason>")
        sys.exit(1)

    try:
        hours = float(sys.argv[1])
        reason = " ".join(sys.argv[2:])
        create_emergency_bypass(hours, reason)
    except ValueError:
        print("Error: Hours must be a number")
        sys.exit(1)
    except Exception as e:
        print(f"Error creating bypass: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
