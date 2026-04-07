import argparse
import sys
import os
from datetime import datetime


from input_layer.swagger_parser import extract_endpoints, fetch_swagger_spec

from ai_processing.llm_client import generate_test_cases
from output_layer.output_writer import export_to_excel

def main():
    parser = argparse.ArgumentParser(
        description="Generate QA test cases from a Swagger/OpenAPI spec using AI (Ollama + Mistral)"
    )

    parser.add_argument('swagger_url', help='URL to the Swagger/OpenAPI JSON or YAML spec')
    parser.add_argument(
        '-o', '--output',
        help='Output Excel file path (default: test_cases_<timestamp>.xlsx)',
        default=None,
    )

    args = parser.parse_args()

    # Default output filename
    if args.output is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"test_cases_{timestamp}.xlsx"

    print(f"Fetching Swagger spec from: {args.swagger_url}")
    try:
        spec = fetch_swagger_spec(args.swagger_url)
    except Exception as e:
        print(f"Error fetching Swagger spec: {e}")
        sys.exit(1)

    title = spec.get("info", {}).get("title", "Unknown API")
    version = spec.get("info", {}).get("version", "")
    print(f"API: {title} (v{version})")

    endpoints = extract_endpoints(spec)
    print(f"Found {len(endpoints)} endpoints\n")

    if not endpoints:
        print("No endpoints found in the spec.")
        sys.exit(1)

    all_test_cases = []
    for i, endpoint in enumerate(endpoints, 1):
        label = f"{endpoint['method']} {endpoint['path']}"
        print(f"[{i}/{len(endpoints)}] Generating test cases for: {label} ...", end=" ", flush=True)

        try:
            cases = generate_test_cases(endpoint)
            all_test_cases.extend(cases)
            print(f"-> {len(cases)} test cases")
        except Exception as e:
            print(f"-> Error: {e}")

    if not all_test_cases:
        print("\nNo test cases were generated.")
        sys.exit(1)

    print(f"\nTotal test cases generated: {len(all_test_cases)}")
    print(f"Saving to: {args.output}")

    export_to_excel(all_test_cases, args.output)
    print(f"Done! Excel file saved: {os.path.abspath(args.output)}")


if __name__ == "__main__":
    main()
