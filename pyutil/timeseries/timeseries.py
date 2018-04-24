import pandas as pd


def adjust(ts: pd.Series) -> pd.Series:
    """
    adjust a (nav) series. Multiply the series with a constant such that the first entry is 1.0

    :param ts: series

    :return: adjusted series
    """
    c = ts.dropna()
    return c / c[c.index[0]]


def ytd(ts: pd.Series, today=None) -> pd.Series:
    """
    Extract year to date of a series or a frame

    :param ts: series or frame
    :param today: today, relevant for testing

    :return: ts or frame starting at the first day of today's year
    """
    today = today or pd.Timestamp("today")
    first_day_of_year = (today + pd.offsets.YearBegin(-1)).date()
    last_day_of_month = (today + pd.offsets.MonthEnd(0)).date()
    return ts.truncate(before=first_day_of_year, after=last_day_of_month)


def mtd(ts: pd.Series, today=None) -> pd.Series:
    """
    Extract month to date of a series or a frame

    :param ts: series or frame
    :param today: today, relevant for testing

    :return: ts or frame starting at the first day of today's month
    """
    today = today or pd.Timestamp("today")
    first_day_of_month = (today + pd.offsets.MonthBegin(-1)).date()
    return ts.truncate(before=first_day_of_month, after=today)


def consecutive(ts: pd.Series) -> pd.Series:
    d = pd.Series(index=ts.index)
    last = 0
    for i, t in ts.items():
        d[i], last = (last + 1, last + 1) if t else (0, 0)
    return d.apply(int)
