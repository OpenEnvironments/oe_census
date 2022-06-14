import sys
import os
import re
import requests
import pandas as pd
import geopandas as gpd
from bs4 import BeautifulSoup

def oe_get_shapes(geoabbrev, year):
    """
    This function generates a pandas geodataframe with the requested geography's mappable shapes.

    :param geoabbrev: the abbreviation for the requested geo like 'TRACT', 'BG', 'BLOCK'
    :type addresses: str

    :param year: the year of the TIGER/Line publication. '2020' or 2020
    :type vintage: str or int

    :returns shapes: a dataframe with the requested geoabbrev's geographic shapes with select other attributes.

    """

    # Known geo levels
    new_geo_levels = []
    geo_levels = {}
    geo_levels['States'] = "STATE"
    geo_levels['Counties'] = "COUNTY"
    geo_levels['County Subdivisions'] = "CCD"
    geo_levels['State Legislative Districts - Upper'] = "SLDU"
    geo_levels['State Legislative Districts - Lower'] = "SLDL"
    geo_levels['Combined Statistical Areas'] = "CSA"
    geo_levels['Census Tracts'] = "TRACT"
    geo_levels['Census Block Groups'] = "BG"
    geo_levels['Census Blocks'] = "BLOCK"
    geo_levels['Congressional Districts'] = "CONG"
    geo_levels['Incorporated Places'] = "INCP"
    geo_levels['Census Designated Places'] = "CDP"
    geo_levels['Zip Code Tabulation Areas'] = "ZCTA"

    # parameter testing
    if not isinstance(geoabbrev, str):
            sys.exit("The first parameter (geoabbr) is a" + str(type(geoabbrev)) + " but should be a string.")
    if not isinstance(year, str):
            try:
                year = str(year)
                assert year > 2000 and year < 3000
            except:
                sys.exit("The second parameter (year) that follows is invalid: " + str(year))
    if geoabbrev not in list(geo_levels.values()):
        sys.exit("Requested geography '" + geoabbrev + "' is not in the support geography list:" + " ".join(list(geo_levels.values())))

    try:
        url = r'https://www2.census.gov/geo/tiger/TIGER'+ year + '/'+geoabbrev+'/'
        front_page = requests.get(url,verify=True)
        soup = BeautifulSoup(front_page.content,'html.parser')
        zipfiles = soup.find_all("a",href=re.compile(r"zip"))
        ziplist = [os.path.join(url,i['href']) for i in zipfiles]
    except:
        sys.exit("Faild to find the site with shape files for "+geoabbrev+" of "+year+":"+url)

    print("Getting the " + str(len(ziplist)) + " shape files for",geoabbrev,"of",year,":")  

    shapelist = []
    for surl in ziplist:
        print("    ",surl)
        shapelist.append(gpd.read_file(surl))
    return pd.concat(shapelist)
