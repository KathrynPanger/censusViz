from __future__ import annotations
import pandas as pd
import geopandas as gpd
from shapely import wkt


class TractsToFacilities():
    def __init__(self, tracts, facilities):
        self.tracts = tracts
        self.facilities = facilities
        # self.tracts.df['geometry'] = self.tracts.df['geometry'].apply(wkt.loads)
        assert self.tracts.city.lower() == self.facilities.city.lower()
        self.city = self.tracts.city
        self.state = self.tracts.state
        self.df = None

    def get_meters_to_nearest_facility(self):
        tracts_cartesian = self.tracts.df.to_crs("EPSG:2953")
        facilities_cartesian = self.facilities.df.to_crs("EPSG:2953")
        df = tracts_cartesian.sjoin_nearest(facilities_cartesian, how="left",
                                                      distance_col="meters_to_nearest_facility")
        # If emissions in data, sort by emissions to get "nearest, then most pollutant plant"
        if self.facilities.varDict["62. ON-SITE RELEASE TOTAL"]:
            df = df.sort_values(by=[self.facilities.varDict["62. ON-SITE RELEASE TOTAL"]], ascending=False)
        else:
            print('First nearest facility kept. To instead keep most pollutant nearest facility, include \"ON-SITE RELEASE TOTAL\" in tracts variable list')

        # drop duplicates for every tract which is equidistant from more than one facility (default creates more rows)
        df = df.drop_duplicates(subset="GEOID", keep="first")
        df = df[["GEOID", "meters_to_nearest_facility"]]
        if self.df is None:
            self.df = self.tracts.df.merge(df, on = "GEOID")
        else:
            self.df = self.df.merge(df, on = "GEOID")

    def get_facilities_in_tract(self):
        df = gpd.sjoin(self.facilities.df, self.tracts.df, how="left", op='intersects')
        # Add a field with 1 as a constant value
        df['number_of_facilities_in_tract'] = 1
        # Group data

        df = df.groupby('GEOID').agg({'number_of_facilities_in_tract': 'sum'}).reset_index()
        df["number_of_facilities_in_tract"] = df['number_of_facilities_in_tract'].astype("int64")
        df = df[["GEOID", "number_of_facilities_in_tract"]]
        df = self.tracts.df.merge(df, on="GEOID", how="left").fillna(value=0)

        if self.df is None:
            self.df = df
        else:
            df = df[["GEOID", "number_of_facilities_in_tract"]]
            self.df = self.df.merge(df, on = "GEOID")

    def get_exposure_vars(self):
        points_data = self.facilities.df
        polygon_data = self.tracts.df
        points = points_data["geometry"].tolist()
        outputs = points_data[self.facilities.varDict["62. ON-SITE RELEASE TOTAL"]].tolist()
        polygon_data["total_exposure"] = 0
        polygon_data["sum_of_distances"] = 0
        for i in range(len(points_data)):
            distances_to_one_point = polygon_data["geometry"].distance(points[i])
            exposure_to_one_point = distances_to_one_point.apply(
                lambda x: ((1 / x ** 2) * outputs[i]) if x != 0 else outputs[i])
            polygon_data["sum_of_distances"] += distances_to_one_point
            polygon_data["total_exposure"] += exposure_to_one_point
        df = polygon_data[["GEOID", "sum_of_distances", "total_exposure"]]

        if self.df is None:
            self.df = df
        else:
            self.df = self.df.merge(df, on="GEOID")

    def normalize(self, variables: list[str]):
        df = self.df
        for variable in variables:
            mean = df[variable].mean()
            std = df[variable].std()
            df[f"{variable}_normalized"] = (df[variable] - mean) / std
        self.df = df


if __name__ == "__main__":
    from tracts import Tracts
    from facilities import Facilities, Units
    # get tracts
    varDict = {"B02001_002E": "white_alone",
               "B02008_001E": "white_some",
               "B02001_003E": "black_alone",
               "B02009_001E": "black_some",
               "B01003_001E": "total_population",
               "B19013_001E": "median_household_income",
               "B25105_001E": "median_housing_cost",
               }
    city = "Chicago"
    state = "IL"
    tracts = Tracts(varDict, city, state)

    # get proportions on tracts
    portions = ["white_alone", "white_some", "black_alone", "black_some"]
    total = "total_population"
    tracts.get_proportions(portions, total)

   # get facilities
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

    facilities = Facilities(varDict, city, units=Units.GRAMS)

    # combine
    tractsToFacilities = TractsToFacilities(tracts, facilities)

    # get derived vars
    tractsToFacilities.get_meters_to_nearest_facility()
    tractsToFacilities.get_facilities_in_tract()
    tractsToFacilities.get_exposure_vars()

    # normalize
    normalList = ["proportion_white_alone",
                  "proportion_white_some",
                  "proportion_black_alone",
                  "proportion_black_some",
                  "median_household_income",
                  "meters_to_nearest_facility",
                  "number_of_facilities_in_tract",
                  "total_exposure"]
    tractsToFacilities.normalize(normalList)



    # write data to outfile
    tractsToFacilities.df.to_csv("../data/city/chicago/chicago.csv")

