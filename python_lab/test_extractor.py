
import json
from structured_extractor import extract_information

sample_text = """
FastAPI is a Python framework for building APIs.
It supports asynchronous programming and automatic
API documentation. Developers use it to build backend services.
"""
try:
    extract_information("   ")
except ValueError as error:
    print("Input validation passed:", error)
    
try:
    result = extract_information(sample_text)

    print("Extraction successful!")
    print(json.dumps(result, indent=2, ensure_ascii=False))

except (ValueError, RuntimeError) as error:
    print("Extraction failed:", error)
