import pandas as pd
import numpy as np

def bin_numeric_single(df, col, bins_no, labels_name, show_bin_range=bool):
    if show_bin_range is True:
        df[col + '_bins'] = pd.cut(df[col], bins=bins_no, labels=labels_name)
        df[col+'_bins_range'] = pd.cut(df[col], bins=bins_no)
    else:
        df[col + '_bins'] = pd.cut(df[col], bins=bins_no, labels=labels_name)
    return df

def bin_numeric_multi(df, cols, bins_no, labels_name, show_bin_range=False):
    for col in cols:
        df[col + '_bins'] = pd.cut(df[col], bins=bins_no, labels=labels_name)

        if show_bin_range:
            df[col + '_bins_range'] = pd.cut(df[col], bins=bins_no)

    return df


# Chatgpt output to see how complex i need to get in the futre
def bin_numeric_adv(
    df,
    cols,
    bins,
    labels=None,
    show_bin_range=False,
    suffix="_bin",
    method="equal_width"  # "equal_width" or "quantile"
):
    """
    Robust numeric binning for multiple columns with catch-all bins.

    Parameters:
        df (pd.DataFrame): input dataframe
        cols (str or list): columns to bin
        bins (int, list, or dict):
            - int: number of bins (equal width or quantile)
            - list: explicit bin edges
            - dict: column -> bin spec
        labels (list or dict, optional): labels per column
        show_bin_range (bool): add Interval objects columns
        suffix (str): suffix for new columns
        method (str): "equal_width" or "quantile"

    Returns:
        pd.DataFrame: dataframe with binned columns
    """

    if isinstance(cols, str):
        cols = [cols]

    df = df.copy()

    for col in cols:
        # --- Determine bins for this column ---
        if isinstance(bins, dict):
            if col not in bins:
                raise ValueError(f"No bins specified for column '{col}' in bins dict.")
            col_bins = bins[col]
        else:
            col_bins = bins

        # --- Determine labels ---
        if labels is None:
            labels_for_col = None
        elif isinstance(labels, dict):
            labels_for_col = labels.get(col, None)
        else:
            labels_for_col = labels  # same labels for all cols

        # --- Auto-generate labels if None ---
        if labels_for_col is None and isinstance(col_bins, int):
            labels_for_col = [f"Bin{i}" for i in range(1, col_bins + 1)]

        # --- Determine actual bin edges ---
        if isinstance(col_bins, int):
            if method == "equal_width":
                min_val = df[col].min()
                max_val = df[col].max()
                edges = np.linspace(min_val, max_val, col_bins + 1)
            elif method == "quantile":
                edges = df[col].quantile(np.linspace(0, 1, col_bins + 1)).to_numpy()
            else:
                raise ValueError(f"Unknown method '{method}'")
        else:
            edges = col_bins

        # --- Extend bins to catch all out-of-range values ---
        edges = np.array(edges, dtype=float)
        edges[0] = -np.inf
        edges[-1] = np.inf

        # --- Bin the column ---
        df[f"{col}{suffix}"] = pd.cut(
            df[col],
            bins=edges,
            labels=labels_for_col,
            include_lowest=True,
            duplicates="drop"
        )

        # --- Optional range column ---
        if show_bin_range:
            df[f"{col}{suffix}_range"] = pd.cut(
                df[col],
                bins=edges,
                include_lowest=True,
                duplicates="drop"
            )

    return df

# df = pd.DataFrame({
#     "score": [5, 12, 18, 25, 33, 47, 52, 67, 81, 95],
#     "ltv_pct": [50, 120, 180, 25, 33, 47, 52, 67, 81, 95]
# })
#
# test = bin_numeric_adv(df, cols=["score","ltv_pct"], bins={"score":[0,5,10,14,20,100], "ltv_pct":4}, labels={'ltv_pct':['low', 'med','high','stupid']}, show_bin_range=True)
#
# print(test)
