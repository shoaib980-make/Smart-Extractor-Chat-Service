import json


def validate_structured_output(response):
    data = json.loads(response)

    required_fields = {
        "title": str,
        "summary": str,
        "keywords": list,
        "category": str,
    }

    for field, expected_type in required_fields.items():
        if field not in data:
            raise ValueError(f"Missing field: {field}")

        if not isinstance(data[field], expected_type):
            raise ValueError(
                f"Field '{field}' must be a "
                f"{expected_type.__name__}"
            )

    if not all(
        isinstance(keyword, str)
        for keyword in data["keywords"]
    ):
        raise ValueError("Every keyword must be a string.")

    for field in ("title", "summary", "category"):
        if not data[field].strip():
            raise ValueError(
                f"Field '{field}' cannot be empty."
            )

    return data


def test_valid_structured_output():
    response = json.dumps({
        "title": "AI Developer Tool",
        "summary": "A tool that improves developer productivity.",
        "keywords": ["AI", "Python", "JavaScript"],
        "category": "Technology",
    })

    data = validate_structured_output(response)

    assert data["title"] == "AI Developer Tool"
    assert isinstance(data["keywords"], list)
    assert data["category"] == "Technology"


def test_invalid_json_is_rejected():
    response = "This is not valid JSON"

    try:
        validate_structured_output(response)
        assert False, "Expected invalid JSON to be rejected."
    except json.JSONDecodeError:
        pass


def test_missing_field_is_rejected():
    response = json.dumps({
        "title": "AI Tool",
        "summary": "An AI tool.",
        "keywords": ["AI"],
    })

    try:
        validate_structured_output(response)
        assert False, "Expected missing field to be rejected."
    except ValueError as error:
        assert "Missing field: category" in str(error)


def test_non_string_keyword_is_rejected():
    response = json.dumps({
        "title": "AI Tool",
        "summary": "An AI tool.",
        "keywords": ["AI", 123],
        "category": "Technology",
    })

    try:
        validate_structured_output(response)
        assert False, "Expected invalid keyword to be rejected."
    except ValueError as error:
        assert "Every keyword" in str(error)