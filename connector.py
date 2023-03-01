from typing import List
import requests


class Connector():
    def __init__ (self, api_key, year: int, varlist:List[str]):
        self.api_key = api_key
        self.year = year
        self.varlist = varlist
        self.base = "https://api.census.gov/data"
        self.dataset = "/acs/acs1"

        def get_data(self):
            # build the url
            url = self.base + self.dataset + "?get=" + ",".join(self.varlist) + "&for=state:*&key=" + self.api_key
            print(url)
            # get the data
            response = requests.get(url)
            # convert to json
           # data = response.json()
            # convert to dataframe
            #df = pd.DataFrame(data[1:], columns=data[0])
            # # convert to numeric
            # df = df.apply(pd.to_numeric, errors='ignore')
            # # convert to csv
            # df.to_csv("data/acs1_{}_{}.csv".format(self.year, self.varlist[0]), index=False)
            return response
        
        self.data = get_data(self)