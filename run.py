import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from xhs.cli import main  # noqa: E402

main()
