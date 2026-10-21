import sys
from pathlib import Path

# Add python_lab to Python path so Vercel can resolve llm_service, structured_extractor, etc.
python_lab_dir = Path(__file__).resolve().parent.parent / "python_lab"
if str(python_lab_dir) not in sys.path:
    sys.path.insert(0, str(python_lab_dir))

from main import app  # noqa: E402
