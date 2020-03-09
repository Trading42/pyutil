import os
import pathlib
import pandas as pd


def folder_stamped(date=None, *args):
    date = date or pd.Timestamp("today")
    folder = os.path.join(os.path.join(*args), "{t}".format(t=date.strftime("%Y%m%d")))
    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
    return folder
