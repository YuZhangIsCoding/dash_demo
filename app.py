from typing import Optional

import pandas as pd
from dash import Dash

app = Dash(__name__)
server = app.server

_df: Optional[pd.DataFrame] = None


def get_df(url: Optional[str] = None) -> pd.DataFrame:
    global _df
    if _df is not None:
        return _df
    elif url:
        _df = pd.read_csv(url)
        return _df
    else:
        raise ValueError("DataFrame not initialized")
