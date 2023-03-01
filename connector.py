from typing import List

class Connector():
    def __init__ (self, api_key, year: int, varlist:List[str]):
        self.api_key = api_key
        self.year = year
        self.varlist = varlist
        self.endPoint = endPoint