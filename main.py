from connector import Connector
from config import API_KEY

year = 2019
varlist = ["NAME", "B02015_009E","B02015_009M"]
connector = Connector(api_key = API_KEY, varlist = varlist, year = year)
response = connector.data
print(response.status_code)