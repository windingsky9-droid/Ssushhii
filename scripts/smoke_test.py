from pathlib import Path
import sys

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
load_dotenv(ROOT / ".env")

from factorweave_client import FactorWeaveClient  # noqa: E402


def main() -> None:
    client = FactorWeaveClient()
    print("Factor Weave connection: authenticated")

    rows = client.features("AAPL")
    first = rows[0] if isinstance(rows, list) and rows else rows
    print("AAPL feature sample:", first)

    context = client.market_context()
    print("Market context:", context)


if __name__ == "__main__":
    main()
