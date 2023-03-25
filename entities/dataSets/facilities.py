from __future__ import annotations
import pandas as pd
import geopandas as gpd
from shapely import wkt

class Facilities():
    def __init__(self, varDict: dict[str, str], city:str):
        self.varDict = varDict
        self.city = city.upper()

        # convert to geopandas, lat-long geometry
        df = pd.read_csv("../../data/raw/epa_tri_toxic_waste_2019.csv")
        df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["13. LONGITUDE"],
                                                              df["12. LATITUDE"])).set_crs("EPSG:4326")
        # select only data from specified city, variables
        df = df.loc[df["6. CITY"] == self.city]
        df = df.rename(columns=self.varDict)
        df = df[[item for item in varDict.values()]]

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
    facilities = Facilities(varDict, city)
    print(facilities.df.head())
    print(facilities.df["units"].unique())

