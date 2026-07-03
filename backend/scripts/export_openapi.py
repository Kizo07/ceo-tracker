"""Export the FastAPI OpenAPI spec to a JSON file.

Used by the frontend codegen pipeline and by CI to detect contract drift:
  python scripts/export_openapi.py --out ../../openapi.json

The app is imported (no server started); models/services are NOT instantiated,
so heavy spaCy/FinBERT/torch models are not loaded.
"""
import argparse
import json
import os
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Export the OpenAPI spec.")
    parser.add_argument(
        "--out",
        default="../../openapi.json",
        help="Output path (default: repo-root openapi.json).",
    )
    args = parser.parse_args()

    # Ensure the backend package is importable when run from anywhere.
    backend_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(backend_root))
    os.environ.setdefault("DATABASE_URL", "sqlite://")

    from app.main import app  # noqa: E402  (import after sys.path setup)

    spec = app.openapi()
    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote OpenAPI spec ({len(json.dumps(spec))} bytes) -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
