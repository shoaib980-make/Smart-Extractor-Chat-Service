
import json
import time
from pathlib import Path

import requests


BASE_URL = "http://127.0.0.1:8000"
DATASET_FILE = Path(__file__).parent / "evaluation_dataset.json"
RESULTS_FILE = Path(__file__).parent / "evaluation_results.json"


def main():
    with open(DATASET_FILE, "r", encoding="utf-8") as file:
        documents = json.load(file)

    results = []
    successful = 0
    valid_json = 0
    schema_valid = 0

    required_fields = {
        "title": str,
        "summary": str,
        "keywords": list,
        "category": str,
    }

    for document in documents:
        print(f"Evaluating document {document['id']}...")
        start = time.time()

        try:
            response = requests.post(
                f"{BASE_URL}/extract",
                json={"text": document["text"]},
                timeout=120,
            )
            elapsed = round(time.time() - start, 2)

            if response.status_code != 200:
                results.append({
                    "id": document["id"],
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "elapsed_seconds": elapsed,
                })
                continue

            payload = response.json()

            # Support either a JSON string or an already-parsed object.
            extracted = payload.get("data", payload.get("result", payload))

            if isinstance(extracted, str):
                try:
                    extracted = json.loads(extracted)
                    valid_json += 1
                except json.JSONDecodeError:
                    results.append({
                        "id": document["id"],
                        "success": False,
                        "error": "Extraction result was not valid JSON",
                        "elapsed_seconds": elapsed,
                    })
                    continue
            elif isinstance(extracted, dict):
                valid_json += 1
            else:
                results.append({
                    "id": document["id"],
                    "success": False,
                    "error": "Unexpected extraction result type",
                    "elapsed_seconds": elapsed,
                })
                continue

            errors = []

            for field, expected_type in required_fields.items():
                if field not in extracted:
                    errors.append(f"Missing field: {field}")
                elif not isinstance(extracted[field], expected_type):
                    errors.append(f"Invalid type for field: {field}")

            if isinstance(extracted.get("keywords"), list):
                if not all(
                    isinstance(keyword, str)
                    for keyword in extracted["keywords"]
                ):
                    errors.append("Keywords must all be strings")

            for field in ("title", "summary", "category"):
                if isinstance(extracted.get(field), str):
                    if not extracted[field].strip():
                        errors.append(f"Empty field: {field}")

            is_schema_valid = not errors

            if is_schema_valid:
                schema_valid += 1
                successful += 1

            results.append({
                "id": document["id"],
                "success": is_schema_valid,
                "schema_errors": errors,
                "elapsed_seconds": elapsed,
                "extracted_data": extracted,
            })

        except requests.RequestException as error:
            elapsed = round(time.time() - start, 2)
            results.append({
                "id": document["id"],
                "success": False,
                "error": str(error),
                "elapsed_seconds": elapsed,
            })

    total = len(documents)

    summary = {
        "total_documents": total,
        "successful_extractions": successful,
        "valid_json_results": valid_json,
        "schema_valid_results": schema_valid,
        "success_rate_percent": round(successful / total * 100, 2) if total else 0,
        "valid_json_rate_percent": round(valid_json / total * 100, 2) if total else 0,
        "schema_valid_rate_percent": round(schema_valid / total * 100, 2) if total else 0,
    }

    output = {
        "summary": summary,
        "results": results,
    }

    with open(RESULTS_FILE, "w", encoding="utf-8") as file:
        json.dump(output, file, indent=2, ensure_ascii=False)

    print("\nEvaluation Summary")
    print(json.dumps(summary, indent=2))
    print(f"\nDetailed results saved to: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
