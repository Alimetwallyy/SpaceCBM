import pandas as pd


def calculate_cbm_from_df(df: pd.DataFrame, col_h: str, col_w: str, col_d: str, col_bin: str=None, round_decimals: int=3) -> pd.DataFrame:
    """
    Calculate CBM from DataFrame columns (units: cm -> m^3).

    Returns a dataframe with columns: BinID (if provided), Height_cm, Width_cm, Depth_cm, CBM_m3
    """
    # Validate columns
    for c in [col_h, col_w, col_d]:
        if c not in df.columns:
            raise ValueError(f"Column {c} not found in dataframe")

    out = pd.DataFrame()
    if col_bin and col_bin in df.columns:
        out['BinID'] = df[col_bin].astype(str)
    else:
        out['BinID'] = [f'Row{idx+1}' for idx in range(len(df))]

    out['Height_cm'] = pd.to_numeric(df[col_h], errors='coerce')
    out['Width_cm'] = pd.to_numeric(df[col_w], errors='coerce')
    out['Depth_cm'] = pd.to_numeric(df[col_d], errors='coerce')

    # Basic validation
    if out[['Height_cm','Width_cm','Depth_cm']].isnull().any().any():
        raise ValueError('One or more dimension values could not be converted to numbers. Check your columns.')

    # CBM calculation: convert cm -> m then multiply OR divide by 1e6
    out['CBM_m3'] = (out['Height_cm'] * out['Width_cm'] * out['Depth_cm']) / 1_000_000.0
    out['CBM_m3'] = out['CBM_m3'].round(round_decimals)

    return out
