import pandas as pd
from datetime import datetime
import calendar
import re

# -----------------------------
# 1. Quarter parser
# -----------------------------
def parse_quarter_string(qtr_str, day_of_month="end"):
    match = re.match(r"Q(\d+)-(\d+)", qtr_str, flags=re.IGNORECASE)
    if match:
        quarter_year = int(match.group(2))
        if int(match.group(1)) == 1:
            quarter_month = 3
        elif int(match.group(1)) == 2:
            quarter_month = 6
        elif int(match.group(1)) == 3:
            quarter_month = 9
        else:
            quarter_month = 12

        if day_of_month == "start":
            date_day = 1
        elif day_of_month == "end" and quarter_month in [3, 12]:
            date_day = 31
        elif day_of_month == "end" and quarter_month in [6, 9]:
            date_day = 30
        else:
            date_day = int(day_of_month)

        return datetime(quarter_year, quarter_month, date_day)
    return None

# -----------------------------
# 2. Month-name parser
# -----------------------------
def parse_month_string(date_str, day_of_month="end", change_all_day_of_month=False):
    match_month = re.match(r"([A-Za-z]{3,})-?\s*(\d{2,4})", date_str, flags=re.IGNORECASE)
    if not match_month:
        return None

    month_str = match_month.group(1)
    year_str = match_month.group(2)
    date_year = _expand_two_digit_year(year_str)

    try:
        month_abbrev = month_str[:3].title()
        date_month = datetime.strptime(month_abbrev, "%b").month
    except ValueError:
        return None

    if change_all_day_of_month:
        if day_of_month == "start":
            date_day = 1
        elif day_of_month == "end":
            date_day = calendar.monthrange(date_year, date_month)[1]
        else:
            date_day = int(day_of_month)
    else:
        date_day = 1

    try:
        return datetime(date_year, date_month, date_day)
    except ValueError:
        return None

# -----------------------------
# 3. UK/US numeric parser
# -----------------------------
def parse_uk_us_numeric(date_str, region="UK", day_of_month="end", change_all_day_of_month=False):
    match_uk_us = re.match(r"^(\d{1,2})[\/\-.](\d{1,2})[\/\-.](\d{2,4})$", date_str)
    if not match_uk_us:
        return None

    date_year = _expand_two_digit_year(match_uk_us.group(3))

    if region.upper() == "UK":
        date_day = int(match_uk_us.group(1))
        date_month = int(match_uk_us.group(2))
    else:
        date_month = int(match_uk_us.group(1))
        date_day = int(match_uk_us.group(2))

    if change_all_day_of_month:
        if day_of_month == "start":
            date_day = 1
        elif day_of_month == "end":
            date_day = calendar.monthrange(date_year, date_month)[1]
        else:
            date_day = int(day_of_month)

    try:
        return datetime(date_year, date_month, date_day)
    except ValueError:
        return None

# -----------------------------
# 4. Compact numeric parser
# -----------------------------
def parse_compact_numeric(date_str, region="UK", day_of_month="end", change_all_day_of_month=False):
    match = re.match(r"^(\d{2})(\d{2})(\d{4})$", date_str)
    if not match:
        return None

    if region.upper() == "UK":
        date_day = int(match.group(1))
        date_month = int(match.group(2))
    else:
        date_month = int(match.group(1))
        date_day = int(match.group(2))

    date_year = int(match.group(3))

    if change_all_day_of_month:
        if day_of_month == "start":
            date_day = 1
        elif day_of_month == "end":
            date_day = calendar.monthrange(date_year, date_month)[1]
        else:
            date_day = int(day_of_month)

    try:
        return datetime(date_year, date_month, date_day)
    except ValueError:
        return None

# -----------------------------
# Helper: expand two-digit year
# -----------------------------
def _expand_two_digit_year(y):
    y = int(y)
    return 2000 + y if y < 100 else y

# -----------------------------
# 5. Final single-value parser
# -----------------------------
def parse_date_string(date_str, region="UK", day_of_month="end", change_all_day_of_month=False):
    if date_str is None:
        return pd.NaT

    date_str = str(date_str).strip()

    parsers = [
        lambda s: parse_uk_us_numeric(s, region, day_of_month, change_all_day_of_month),
        lambda s: parse_compact_numeric(s, region, day_of_month, change_all_day_of_month),
        lambda s: parse_month_string(s, day_of_month, change_all_day_of_month),
        lambda s: parse_quarter_string(s, day_of_month)
    ]

    for parser in parsers:
        date_out = parser(date_str)
        if date_out is not None:
            return date_out

    # fallback to pandas
    try:
        return pd.to_datetime(date_str, dayfirst=(region.upper() != "US"), errors="raise")
    except Exception:
        return pd.NaT


# 6. DataFrame-level parser

# DataFrame-level parser
def parse_date_columns_from_string(df, columns=None, region="UK", day_of_month="end",
                       change_all_day_of_month=False, suffix="_date_converted", inplace=False):
    # Auto-detect string/object columns if columns not specified
    if columns is None:
        columns = df.select_dtypes(include="object").columns.tolist()

    for col in columns:
        if inplace:
            df[col] = df[col].apply(
                lambda x: parse_date_string(x, region=region, day_of_month=day_of_month,
                                            change_all_day_of_month=change_all_day_of_month)
            )
        else:
            new_col = f"{col}{suffix}"
            df[new_col] = df[col].apply(
                lambda x: parse_date_string(x, region=region, day_of_month=day_of_month,
                                            change_all_day_of_month=change_all_day_of_month)
            )
    return df


# Lazy parser for all string columns
def parse_all_date_cols_from_string(df, region="UK", day_of_month="end", change_all_day_of_month=False):
    return parse_date_columns_from_string(df, columns=None, region=region, day_of_month=day_of_month,
                                          change_all_day_of_month=change_all_day_of_month, inplace=True)


