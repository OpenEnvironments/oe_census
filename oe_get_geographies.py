import pandas as pd
import requests
import json
import datetime
import sys


def oe_get_geographies(addresses, requested_geography, vintage='Census2010_Current', benchmark='Public_AR_Current'):
    """
    This function takes a pandas dataframe of addresses with ID, street and zip
    then calls the Census geocoder to return the requested geography's GEOID on each.

    :param addresses: pandas DataFrame with at least 3 columns: ID, street and zipcode
    :type addresses: pandas DataFrame

    :param vintage: the census or survey the data is linked to.
    :type vintage: str

    :param benchmark: time period when we created the snapshot of the data (usually done twice yearly).
    :type benchmark: str

    :returns responses: a dataframe with the requested IDs, query status and requested geography found for each.

    """

    endpoint = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"
    responseformat = "json"

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
    geo_levels['Census Blocks'] = "BLOCK"
    geo_levels['Congressional Districts'] = "CONG"
    geo_levels['Incorporated Places'] = "INCP"
    geo_levels['Census Designated Places'] = "CDP"

    # parameter testing
    if not isinstance(addresses, pd.DataFrame):
            print("The first parameter (addresses) is a", type(addresses)," but should be a pandas dataframe. ")
            sys.exit(0)
    if not isinstance(requested_geography, str):
            print("The second parameter (geography) is a", type(requested_geography)," but should be a pandas dataframe. ")
            sys.exit(0)
    for c in ["ID","street","zipcode"]:
        if c not in addresses.columns:
            print("Column '"+c+"' is required but missing from the submitted address list.")
            sys.exit(0)
    if requested_geography not in geo_levels:
            print("Requested geography '"+requested_geography+"' is not in the support geography list:",list(geo_levels.keys()))
            sys.exit(0)

    # ready to start, initialize ...
    counter = 0
    responses = []

    start = datetime.datetime.now()
    print("Geocoding",addresses.shape[0],"addresses:", end=" ")

    # for each address in the set, stop at limit
    for index, address in addresses.iterrows():
        counter +=1
        respdict = {}
        respdict["ID"] = address["ID"]

        # prepare the request string
        straddr = address['street'].split("#",1)[0].split(",",1)[0].replace(' ', '+')
        req = "/?"
        req += "address="+ straddr + '%2C+'
        req += address['zipcode']
        req += "&benchmark=" + benchmark
        req += "&vintage=" + vintage
        req += "&format=" + responseformat

        keepgoing = True
        status = "Not set"
        result = "Dunno"
        # progressive steps, each of which needs a trap for any failures
        print(address["ID"],end=",")
        if keepgoing:
            try:
                tries = 1
                while True:
                    if tries > 3:
                        # Three unsuccessful tries causes a fail within this try block
                        assert False
                    try:
                        response = requests.get((endpoint + req).lower())
                        assert response.status_code == 200
                        break
                    except:
                        tries += 1
            except:
                status = "request attempt failed"
                result = endpoint + req
                keepgoing = False
        if keepgoing:
            try:
                assert response.status_code == 200 
            except:
                status = "Non 200 status code"
                result = response
                keepgoing = False
        if keepgoing:
            if response.text[0:5] == "<?xml":
                status = "XML response from census endpoint"
                result = response
                keepgoing = False
        if keepgoing:
            try:
                js = json.loads(response.text)
            except:
                status = "JSON load of response text failed"
                result = response
                keepgoing = False
        if keepgoing:
            if len(js["result"]["addressMatches"]) == 0:
                status = "No addresses matched"
                result = js
                keepgoing = False
        if keepgoing:
            for geo in js["result"]["addressMatches"][0]["geographies"]:
                geo_search = geo
                if (geo[0]>="0" and geo[0]<="9"):
                    geo_search=geo[geo.find(" ")+1:99]
                if geo_search not in list(geo_levels.keys()):
                    new_geo_levels.append(geo)
                else:
                    if geo == requested_geography:
                        status = geo +" found"
                        result = js["result"]["addressMatches"][0]["geographies"][geo][0]['GEOID']
        respdict["status"] = status
        respdict["result"] = result
        responses.append(respdict)
    print()
    print()
    if len(new_geo_levels) > 0:
        print("New geographies:", new_geo_levels)
    return pd.DataFrame(responses)
