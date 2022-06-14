import pandas as pd
import requests
import json
import sys
import datetime

def oe_append_ACS5(geocodes, varlist, year="2019"):
    """
    The Census API for the ACS 5 Year, 2019 vintage
    Needs at least state with optionally addl county, tract and blockgroup id
    And can accept variable lists less than 50
    Iterrate over the API requesting a variable list for each bg
    Example bg = "420912048003"  is  state=42 county=091 tract=204800 blockgroup=3

    This function accepts

    :param geocodes: data with at least 2 columns: ID and GEOID
    :type geocodes: pandas DataFrame

    :param year: 4 digit year of the ACS 5-year publication
    :type year: str

    :param varlist: a list of each variabel requested, in the B01001_001E naming format
    :type varlist: list

    :returns: a dataframe with columns for the requested IDs, query status and each varliable requested.

    """

    # parameter testing
    if not isinstance(geocodes, pd.DataFrame):
            print("The first parameter (geocodes) is a", type(geocodes)," but should be a pandas dataframe. ")
            sys.exit(1)
    if not isinstance(varlist, list):
            print("The second parameter (varlist) is a", type(varlist)," but should be a list. ")
            sys.exit(1)
    for c in ["ID","GEOID"]:
        if c not in geocodes.columns:
            print("Column '"+c+"' is required but missing from the submitted list.")
            sys.exit(1)

   # make a list of dictionaries on each API response
    censuslist = []

    # Census API has max vars for each request, so make len chunks of the varlist
    chunk = 0
    chunksize = 49

    # check the varlist against the ACS5 variabes available 
    try:
        req = requests.get("https://api.census.gov/data/"+year+"/acs/acs5/variables.json")
        assert req.status_code == 200
        js = json.loads(req.text)
    except:
        print("ACS5 is not available for requested year:",year)
        sys.exit(1)

    invalids = set(varlist) - set(js["variables"].keys())
    if len(invalids) > 0:
        print("These requested variables are not available from the Census ACS5 (see https://api.census.gov/data/"+year+"/acs/acs5/variables.json):")
        print(invalids)
        sys.exit(1)

    print("Adding ACS5 data for",geocodes.shape[0],"geocodes:", end=" ")
    for i,geo in geocodes.iterrows():
        print(" "+str(geo["ID"]), end="")
        censusdict = {}
        censusdict["ID"] = geo["ID"]
        censusdict["status"] = ""
        censusdict["GEOID"] = geo["GEOID"]
        chunk = 0
        while (chunk*chunksize) < len(varlist):
            print("/"+str(chunk),end="")
            vlistchunk = varlist[chunk*chunksize : min(chunk*chunksize+chunksize,len(varlist))]
            # initialize this chunks variables as keys in the censusdict result
            for c in vlistchunk:
                censusdict[c] = float("NaN")
            # assemble the API request
            req = "https://api.census.gov/data/"+year+"/acs/acs5?get=NAME,"
            req += ",".join(vlistchunk)
            req += "&for=block%20group:"+geo.GEOID[11:12]
            req += "&in=state:"+geo.GEOID[:2]
            req += "&in=county:"+geo.GEOID[2:5]
            req += "&in=tract:"+geo.GEOID[5:11]
            req += "&key=d75043ce01f4feafcc09f2a72ad3c80eb9567598"
            try: 
                r = requests.get(req)
                assert r.status_code == 200
                # The Census response is two lists: a title row and result row
                # The result row prefix is NAME and last 4 cols are state,county,tract,bg etc
                censusdata = json.loads(r.text)[1]
                censusdata = censusdata[1:len(censusdata)-4]
                for v in vlistchunk:
                    censusdict[v] = int(censusdata[vlistchunk.index(v)])
                censusdict["status"] += " Chunk "+str(chunk)+" succeeded."
            except:
                censusdict["status"] += " Chunk "+str(chunk)+" failed."
            chunk += 1
        censuslist.append(censusdict)
    print()
    print()
    return pd.DataFrame(censuslist)
