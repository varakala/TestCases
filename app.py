import argparse
import sys
import os
from datetime import datetime
import logging

from input_layer.swagger_parser import extract_endpoints, fetch_swagger_spec
from ai_processing.llm_client import generate_test_cases
from output_layer.output_writer import export_to_excel
from validation_layer.validationrules import generate_validation_test_cases

from logging_config import setup_logging

# --------------------
# Logging setup
# --------------------
setup_logging()
logger = logging.getLogger(__name__)


def main():
    logger.info("Application started")

    parser = argparse.ArgumentParser(
        description="Generate QA test cases from a Swagger/OpenAPI spec using AI (Ollama + Mistral)"
    )

    parser.add_argument(
        "swagger_url",
        help="URL to the Swagger/OpenAPI JSON or YAML spec"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output Excel file path (default: test_cases_<timestamp>.xlsx)",
        default=None,
    )

    args = parser.parse_args()

    logger.info("Arguments received | swagger_url=%s | output=%s",
                args.swagger_url, args.output)

    # Default output filename
    if args.output is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"test_cases_{timestamp}.xlsx"
        logger.info("Output file not provided, generated default | output=%s", args.output)

    # --------------------
    # Fetch Swagger spec
    # --------------------
    logger.info("Fetching Swagger spec")

    try:
        spec = fetch_swagger_spec(args.swagger_url)
        logger.info("Swagger spec fetched successfully")
    except Exception:
        logger.exception("Failed to fetch Swagger spec")
        sys.exit(1)

    title = spec.get("info", {}).get("title", "Unknown API")
    version = spec.get("info", {}).get("version", "N/A")

    logger.info("API identified | title=%s | version=%s", title, version)

    # --------------------
    # Extract endpoints
    # --------------------
    endpoints = extract_endpoints(spec)
    logger.info("Endpoints extracted | count=%d", len(endpoints))

    if not endpoints:
        logger.error("No endpoints found in Swagger spec")
        sys.exit(1)

    # --------------------
    # Generate test cases
    # --------------------
    all_test_cases = []

    for index, endpoint in enumerate(endpoints, start=1):
        label = f"{endpoint.get('method')} {endpoint.get('path')}"

        logger.info(
            "Processing endpoint [%d/%d] | %s",
            index,
            len(endpoints),
            label
        )

        try:
            # Switch easily between LLM or rule-based
            # cases = generate_validation_test_cases(endpoint)
            cases = generate_test_cases(endpoint)

            all_test_cases.extend(cases)

            logger.info(
                "Test cases generated | endpoint=%s | count=%d",
                label,
                len(cases)
            )

        except Exception:
            logger.exception(
                "Failed to generate test cases | endpoint=%s",
                label
            )

    if not all_test_cases:
        logger.error("No test cases were generated")
        sys.exit(1)

    logger.info("Total test cases generated | count=%d", len(all_test_cases))
    logger.info("Exporting test cases to Excel | file=%s", args.output)

    # --------------------
    # Export to Excel
    # --------------------
    try:
        export_to_excel(all_test_cases, args.output)
        logger.info(
            "Excel file saved successfully | path=%s",
            os.path.abspath(args.output)
        )
    except Exception:
        logger.exception("Failed to export test cases to Excel")
        sys.exit(1)

    logger.info("Application completed successfully")


if __name__ == "__main__":
    main()