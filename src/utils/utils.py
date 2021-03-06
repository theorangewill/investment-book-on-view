from os import listdir, makedirs
from os.path import isfile, join, exists
from typing import Dict
import pandas as pd
from trade_confirmation.trade_confirmation import TradeConfirmation

def read_trade_confirmation(trade_confirmation_dir: str) -> Dict:
    """
    This function reads the trade confirmation files and validates them.
    """
    tc_files = [join(trade_confirmation_dir, file)
        for file in listdir(trade_confirmation_dir)
            if isfile(join(trade_confirmation_dir, file))
    ]
    papers = {}
    for file in tc_files:
        paper = TradeConfirmation(file)
        if not paper.date in papers:
            papers[paper.date] = []
        papers[paper.date].append(paper)
    return papers

def create_folder(folder: str) -> None:
    if not exists(folder):
        makedirs(folder)
    return folder

def get_dataframe(file: str, columns: list) -> pd.DataFrame:
    """
    This function reads a dataframe if it exists,
    or creates it by using the columns parameter otherwise
    """
    if exists(file):
        df = pd.read_csv(file, sep=';')
    else:
        df = pd.DataFrame(columns=columns)
    return df

def save_to_file(stage: str, df: pd.DataFrame, file: str) -> None:
    df_prev = get_dataframe(file, df.columns)
    tc_name = df["tc_name"].unique()[0]
    if not df_prev.loc[(df_prev["tc_name"] == tc_name)].empty:
        df_prev = df_prev.loc[~(df_prev["tc_name"] == tc_name)]
    df_prev = pd.concat([df_prev, df])
    df_prev = df_prev.sort_values(["date", "tc_name"])
    df_prev.to_csv(file, sep=';', index=False)
    