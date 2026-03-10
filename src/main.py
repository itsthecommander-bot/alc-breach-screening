"""
Reads email addresses from a CSV file, invokes the
ScreeningService to query the APIs, and writes
the results to an output CSV file. 
"""

import csv
import logging
import re
from src.screening_service import ScreeningService
from src.logger_config import setup_logging

setup_logging()

INPUT_FILE = "email_list.csv"
OUTPUT_FILE = "output_result.csv"


EMAIL_REGEX = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)

def is_valid_email(email: str) -> bool:
    """
    Return True if the provided string is a valid email address.
    """
    if not email:
        return False
    return bool(EMAIL_REGEX.match(email.strip()))


def process_emails(primary_provider=None):
    """
    Read emails from the input CSV, check them against breach APIs,
    and write the results to the output CSV file.
    """
    logging.info("Starting email breach processing job")

    service = ScreeningService(primary_provider=primary_provider)
    results = []
    breach_domain_counter = {}

    try:
        with open(INPUT_FILE, "r", newline="", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)

            if not reader.fieldnames or "email_address" not in reader.fieldnames:
                logging.error("Input CSV missing required 'email_address' header")
                raise ValueError("Invalid CSV format")

            for row in reader:
                email = row.get("email_address", "").strip()

                if not is_valid_email(email):
                    logging.warning(f"Invalid email format detected — skipping: {email}")
                    continue

                try:
                    logging.info(f"Processing {email}")
                    result = service.check_email(email)

                    breached = result.get("breached", False)
                    sources = result.get("sources", [])
                    breach_count = result.get("breach_count", 0)
                    provider = result.get("provider", "Unknown")

                    logging.debug(
                        f"{email} | Provider={provider} | "
                        f"Breached={breached} | Count={breach_count}"
                    )

                    for source in set(sources):
                        breach_domain_counter[source] = breach_domain_counter.get(source, 0) + 1

                    results.append({
                        "email_address": email,
                        "breached": breached,
                        "breach_count": breach_count,
                        "provider_used": provider,
                        "site_where_breached": ";".join(sources)
                    })

                except Exception as e:
                    logging.error(f"Failed processing {email}: {e}")
                    results.append({
                        "email_address": email,
                        "breached": False,
                        "breach_count": 0,
                        "provider_used": "Error",
                        "site_where_breached": ""
                    })

    except FileNotFoundError:
        logging.critical(f"Input file '{INPUT_FILE}' not found")
        raise

    logging.info("Writing results to output CSV")

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as outfile:
        fieldnames = [
            "email_address",
            "breached",
            "breach_count",
            "provider_used",
            "site_where_breached"
        ]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    logging.info("Processing complete")

    print("\n--- Analyst Summary ---")
    print(f"Total Valid Emails Processed: {len(results)}")
    print(f"Total Breached Emails: {sum(r['breached'] for r in results)}")

    print("\nTop Breach Sources:")
    for domain, count in sorted(
        breach_domain_counter.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]:
        print(f"{domain}: {count}")

def choose_provider():
    print("\nSelect primary provider:")
    print("1. LeakCheck")
    print("2. IntelX")

    while True:
        choice = input("Enter choice (1 or 2): ").strip()

        if choice == "1":
            return "LeakCheck"
        elif choice == "2":
            return "IntelX"
        else:
            print("Invalid selection. Please enter 1 or 2.")


if __name__ == "__main__":
    selected_provider = choose_provider()
    process_emails(primary_provider=selected_provider)