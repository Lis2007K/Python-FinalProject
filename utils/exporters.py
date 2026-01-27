import pandas as pd
from pathlib import Path


def export_to_csv(transactions, filename: str) -> str:
    """
    Exports a list of transaction objects to CSV.
    """
    data = [
        {
            "date": t.date,
            "type": t.ttype,
            "category": t.category,
            "amount": t.amount,
            "description": t.description
        }
        for t in transactions
    ]

    df = pd.DataFrame(data)

    export_dir = Path("exports")
    export_dir.mkdir(exist_ok=True)

    path = export_dir / filename
    df.to_csv(path, index=False)

    return str(path)
