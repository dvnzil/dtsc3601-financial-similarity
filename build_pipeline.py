"""
Run this once, locally, to produce pipeline.joblib.
That file is what serve.py loads — nothing gets fit at API boot time.
"""
from datetime import datetime, timezone

import joblib
import pandas as pd
import sklearn
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

from pipeline_def import FinancialRatioTransformer, RAW_COLUMNS

RAW_CSV = "2018_Financial_Data.csv"
CLEAN_CSV = "company_financials_clean.csv"
N_NEIGHBORS = 6  # 1 self-match + 5 real neighbors


def clean_data() -> pd.DataFrame:
    df = pd.read_csv(RAW_CSV)
    df = df.rename(columns={df.columns[0]: "ticker"})
    df = df[["ticker"] + RAW_COLUMNS].dropna()
    df = df.drop_duplicates(subset="ticker")
    # drop rows where ratios would be nonsensical (zero/negative base figures)
    df = df[
        (df["Total assets"] > 0)
        & (df["Revenue"] > 0)
        & (df["Total shareholders equity"] != 0)
    ]
    df.to_csv(CLEAN_CSV, index=False)
    return df


def build() -> None:
    df = clean_data()
    X = df[RAW_COLUMNS].values

    pipeline = Pipeline([
        ("ratios", FinancialRatioTransformer()),
        ("scaler", StandardScaler()),
        ("knn", NearestNeighbors(n_neighbors=N_NEIGHBORS)),
    ])
    pipeline.fit(X)

    bundle = {
        "pipeline": pipeline,
        "tickers": df["ticker"].tolist(),
        "raw_data": df.to_dict(orient="records"),
        "metadata": {
            "steps": [name for name, _ in pipeline.steps],
            "built_at": datetime.now(timezone.utc).isoformat(),
            "sklearn_version": sklearn.__version__,
            "n_companies": len(df),
            "raw_columns": RAW_COLUMNS,
        },
    }
    joblib.dump(bundle, "pipeline.joblib")
    print(f"fitted on {len(df)} companies")
    print(bundle["metadata"])


if __name__ == "__main__":
    build()
