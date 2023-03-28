from __future__ import annotations
import cenpy
from shapely import wkt

class Tracts():
    def __init__(self, varDict: dict[str, str], city:str, state:str):
        self.varDict = varDict
        self.city = city
        self.state = state

        acs = cenpy.products.ACS()
        df = acs.from_place(f'{self.city}, {self.state}',
                            variables=[item for item in varDict.keys()],
                            level="tract",
                            return_bounds=False)
        df = df.rename(columns = self.varDict)
        df = df.to_crs("EPSG:4326")
        self.df = df

    def get_proportions(self, portions: dict[str:str], total: str):
        df = self.df
        for portion in portions.items():
            df[portion[1]] = df[portion[0]] / df[total]
        self.df = df

if __name__ == "__main__":
    # test init

    # VARIABLES OF INTEREST
    # B02008_001E = White alone or in combination with one or more races
    # B02009_001E = Black alone or in combination with one or more races
    # B02001_002E = White alone
    # B01003_001E = Total Population
    # B19013_001E = median household income in the past 12 months
    # B02001_003E = black alone
    # B25105_001E = median housing cost in the past 12 months
    varDict = {"B02001_002E": "white_alone",
               "B02008_001E":  "white_some",
               "B02001_003E": "black_alone",
               "B02009_001E": "black_some",
               "B01003_001E": "total_population",
               "B19013_001E": "median_household_income",
               "B25105_001E": "median_housing_cost",
               }
    city = "Chicago"
    state = "IL"
    censusDf = Tracts(varDict, city, state)



    print(censusDf.df.head())