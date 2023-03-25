from __future__ import annotations
import pandas as pd
import geopandas as gpd
import enum

class units(enum.Enum):
    GRAMS = "Grams"
    POUNDS = "Pounds"
    MIXED = "Mixed"

class Facilities():
    def __init__(self, varDict: dict[str, str], city:str, units = units.GRAMS):
        self.varDict = varDict
        self.city = city.upper()
        self.units = units

        # convert to geopandas, lat-long geometry
        df = pd.read_csv("../../../data/raw/epa_tri_toxic_waste_2019.csv")
        df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["13. LONGITUDE"],
                                                              df["12. LATITUDE"])).set_crs("EPSG:4326")

        # select only data from specified city
        df = df.loc[df["6. CITY"] == self.city]

        # convert all mixed unit columns to grams, if specified
        unitsDict = {units.GRAMS: 453.592, units.POUNDS: 1/453.592, units.MIXED: 1}
        df["conversion"] = df["47. UNIT OF MEASURE"].apply(lambda x: 1 if x == self.units else unitsDict[self.units])
        for i in range(47, 62):
            df.iloc[:, i] = df.iloc[:, i] * df["conversion"]

        #change units column to reflect this
        if self.units != units.MIXED:
            df["47. UNIT OF MEASURE"] = units.value

        # rename columns as specified by user
        df = df.rename(columns=self.varDict)
        # select only data from specified variables
        df = df[[item for item in varDict.values()]]

        # save final df
        self.df = df


if __name__ == "__main__":
    varDict = {
        "2. TRIFD": "trifd",
        "4. FACILITY NAME": "facility",
        "34. CHEMICAL": "chemical",
        "43. CARCINOGEN": "is_carcinogenic",
        "40. CLASSIFICATION": "classification",
        "41. METAL": "is_metal",
        "47. UNIT OF MEASURE": "units",
        "62. ON-SITE RELEASE TOTAL": "onsite_release_total",
        "geometry": "geometry",
               }
    city = "Chicago"
    facilities = Facilities(varDict, city, units = units.GRAMS)
    print(facilities.df.head())
    print(facilities.df["units"].unique())

