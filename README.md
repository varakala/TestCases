# Swagger Test Case Generator

An AI-powered Python tool that generates QA test cases from any Swagger/OpenAPI specification. It parses all endpoints, uses Ollama (Mistral model) to generate comprehensive test cases, and exports them to a formatted Excel file.

## Features

- Supports Swagger 2.0 and OpenAPI 3.x specifications (JSON and YAML)
- Generates test cases covering:
  - Positive / happy path tests
  - Negative tests (invalid inputs, missing required fields)
  - Boundary value tests
  - Authentication / authorization tests
  - Edge cases
- Exports to Excel with:
  - Color-coded priorities (High / Medium / Low)
  - Auto-filters and frozen header row
  - Summary sheet with breakdowns by priority and endpoint
- Progress tracking in the terminal

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.com/) installed and running
- Mistral model pulled in Ollama

## Setup

1. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Pull and start the Mistral model:

   ```bash
   ollama pull mistral
   ollama serve
   ```

## Usage

```bash
# Basic usage (generates test_cases_<timestamp>.xlsx)
python app.py <swagger_url>

# Custom output file
python app.py <swagger_url> -o output.xlsx
```

### Examples

```bash
# Petstore sample API
python app.py https://petstore.swagger.io/v2/swagger.json

# With custom output path
python app.py https://petstore.swagger.io/v2/swagger.json -o petstore_tests.xlsx
```

## Project Structure

```
├── app.py              # CLI entry point
├── swagger_parser.py   # Fetches and parses Swagger/OpenAPI specs
├── test_generator.py   # Generates test cases via Ollama + Mistral
├── excel_exporter.py   # Exports test cases to formatted Excel
├── requirements.txt    # Python dependencies
└── README.md
```

## Excel Output

The generated Excel file contains two sheets:

**Test Cases** — one row per test case with columns:

| Column | Description |
|---|---|
| Test Case ID | Sequential ID (TC_0001, TC_0002, ...) |
| Endpoint | HTTP method and path |
| Tags | API tags from the spec |
| Test Scenario | Short scenario name |
| Test Description | Detailed description |
| Preconditions | Setup needed before testing |
| Test Steps | Step-by-step instructions |
| Test Data | Input data to use |
| Expected Result | Expected outcome |
| Priority | High / Medium / Low |
| Test Type | Positive / Negative / Boundary / Security / Edge Case |

**Summary** — aggregated counts by priority and endpoint.
