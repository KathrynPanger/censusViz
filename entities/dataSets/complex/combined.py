from __future__ import annotations
from census import Census
import enum
import pandas as pd
import geopandas as gpd

class UnitOfAnalysis(enum.Enum):
    TRACT = Enum.auto()
    FACILITY = Enum.auto()

class Combined():
    def __init__(self, census, facilities, unitOfAnalysis):
        self.census = census
        self.facilities = facilities
        assert self.census.city.lower() == self.facilities.city.lower()

    def get_meters_to_nearest_facility(self):
        census_cartesian = self.census.df.to_crs("EPSG:2953")
        facilities_cartesian = self.facilities.df.to_crs("EPSG:2953")
        census_to_facilities = census_cartesian.sjoin_nearest(facilities_cartesian, how="left",
                                                      distance_col="meters_to_nearest_facility")
        # If emissions in data, sort by emissions to get "nearest, then most pollutant plant"
        if self.census.varDict["62. ON-SITE RELEASE TOTAL"]:
            census_to_facilities = census_to_facilities.sort_values(by=[self.census.varDict["62. ON-SITE RELEASE TOTAL"]], ascending=False)
        else:
            print('First nearest facility kept. To instead keep most pollutant nearest facility, include \"ON-SITE RELEASE TOTAL\" in census variable list')

        # drop duplicates for every tract which is equidistant from more than one facility (default creates more rows)
        census_to_facilities = census_to_facilities.drop_duplicates(subset="GEOID", keep="first")
        census_to_facilities = census_to_facilities[["GEOID", "meters_to_nearest_facility"]]
        if not self.census_to_facilities:
            self.census_to_facilities = census_to_facilities
        else:
            self.census_to_facilities = self.census_to_facilities.join(census_to_facilities, on = "GEOID")

    def get_facilities_in_tract(self):
        # facilities_in_tract = gpd.sjoin(self.facilities.df, self.census.df, how="left", op='intersects')
        # # Add a field with 1 as a constant value
        # facilities_in_tract['number_of_facilities_in_tract'] = 1
        # # Group data
        # facilities_in_tract = facilities_in_tract.groupby('GEOID').agg({'number_of_facilities_in_tract': 'sum'}).reset_index()
        # census_to_facilities = self.census.df.merge(facilities_in_tract, on="GEOID", how="left").fillna(value=0)
        pass


    def get_proportions(self, portions: portionsDict: dict[str:str], total: str):
        df = self.census.df
        for portion in portions.items():
            df[portion[1] = df[portion[0]] / df[total]]
        self.census.df = df