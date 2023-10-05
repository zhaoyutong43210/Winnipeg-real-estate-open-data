import pandas as pd
import pathlib


class data_analyser():

    def __init__(self) -> None:
        self._data__ = 0
        self.data_path = pathlib.Path().absolute().parents[1] / "Winnipeg_real_estate_open_data"

    def load_sell_data(self):
        file = self.data_path / 'combined_data.csv'
        data = pd.read_csv(file)
        return data

    def load_access_data(self):
        file = self.data_path / 'access_parcel' / 'Assessment_Parcels_cleaned.csv'
        data = pd.read_csv(file)

        return data
    

