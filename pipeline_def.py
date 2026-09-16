import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

# Raw dollar-figure columns this pipeline expects, in this exact order.
RAW_COLUMNS = [
    "Total current assets",
    "Total assets",
    "Total current liabilities",
    "Total liabilities",
    "Total debt",
    "Total shareholders equity",
    "Revenue",
    "Net Income",
]

RATIO_NAMES = [
    "current_ratio",
    "debt_to_equity",
    "liabilities_to_assets",
    "net_margin",
    "equity_ratio",
]


class FinancialRatioTransformer(BaseEstimator, TransformerMixin):
    """Turns raw balance-sheet / income-statement dollar figures into
    scale-independent financial ratios, so a $1B company and a $10M
    company can be compared on the same footing instead of the
    comparison just tracking company size.
    """

    def __init__(self, eps: float = 1e-6):
        # __init__ only assigns its arguments — no computation here.
        self.eps = eps

    def fit(self, X, y=None):
        # Nothing to learn for this step (it's pure arithmetic), but the
        # sklearn contract requires fit to return self.
        return self

    def transform(self, X):
        X = np.asarray(X, dtype=float)
        (current_assets, total_assets, current_liab, total_liab,
         total_debt, equity, revenue, net_income) = X.T

        current_ratio = current_assets / (current_liab + self.eps)
        debt_to_equity = total_debt / (equity + self.eps)
        liabilities_to_assets = total_liab / (total_assets + self.eps)
        net_margin = net_income / (revenue + self.eps)
        equity_ratio = equity / (total_assets + self.eps)

        return np.column_stack([
            current_ratio,
            debt_to_equity,
            liabilities_to_assets,
            net_margin,
            equity_ratio,
        ])

    def get_feature_names_out(self, input_features=None):
        return np.array(RATIO_NAMES)
