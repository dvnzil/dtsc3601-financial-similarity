"""
FastAPI service around pipeline.joblib.
Run locally with: uvicorn serve:app --reload
"""
from typing import List

import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from pipeline_def import RAW_COLUMNS  # noqa: F401 (needed for unpickling)

BUNDLE_PATH = "pipeline.joblib"
N_RESULTS = 5  # nearest neighbors to return, excluding self-match

app = FastAPI(title="Financial Ratio Similarity Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontend-delta-beryl-97.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_bundle = None
_load_error = None

try:
    _bundle = joblib.load(BUNDLE_PATH)
except Exception as exc:  # noqa: BLE001
    _load_error = str(exc)


def get_bundle():
    if _bundle is None:
        raise HTTPException(
            status_code=503,
            detail=f"Model bundle failed to load: {_load_error}",
        )
    return _bundle


class CompanyFinancials(BaseModel):
    total_current_assets: float = Field(..., gt=0, alias="Total current assets")
    total_assets: float = Field(..., gt=0, alias="Total assets")
    total_current_liabilities: float = Field(..., gt=0, alias="Total current liabilities")
    total_liabilities: float = Field(..., gt=0, alias="Total liabilities")
    total_debt: float = Field(..., gt=0, alias="Total debt")
    total_shareholders_equity: float = Field(..., gt=0, alias="Total shareholders equity")
    revenue: float = Field(..., gt=0, alias="Revenue")
    net_income: float = Field(..., gt=0, alias="Net Income")

    model_config = {"populate_by_name": True}


class SimilarCompany(BaseModel):
    ticker: str
    distance: float


class SimilarResponse(BaseModel):
    results: List[SimilarCompany]


@app.get("/info")
def info():
    bundle = get_bundle()
    return bundle["metadata"]


@app.post("/similar", response_model=SimilarResponse)
def similar(company: CompanyFinancials):
    bundle = get_bundle()
    pipeline = bundle["pipeline"]
    tickers = bundle["tickers"]

    raw_row = [[
        company.total_current_assets,
        company.total_assets,
        company.total_current_liabilities,
        company.total_liabilities,
        company.total_debt,
        company.total_shareholders_equity,
        company.revenue,
        company.net_income,
    ]]

    transformed = pipeline[:-1].transform(raw_row)
    knn = pipeline.named_steps["knn"]
    distances, indices = knn.kneighbors(transformed, n_neighbors=N_RESULTS)

    results = [
        SimilarCompany(ticker=tickers[idx], distance=float(dist))
        for dist, idx in zip(distances[0], indices[0])
    ]

    return SimilarResponse(results=results)
