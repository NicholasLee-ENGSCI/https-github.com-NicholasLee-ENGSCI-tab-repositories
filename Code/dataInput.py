"""
Reads data and outputs data in format specifically compatible to input format of our functions

"""

# from glob import glob
import datetime
import numpy as np
import pandas as pd
import json
import os

from typing import Dict, List, Tuple


def readLocationGroups(fileAddress: str = "./Data/LocationGroups.csv")->Dict[str, List[str]]:
    """
    Returns the stores in their region groups (North, West, Central and South)
    
    Parameters
    ---------
    fileAddress: str
                 Names of supermarkets in each region (North, West, Central and South)
    
    Returns
    ------
    res: dictionary
         Stores in their region groups
    
    """
    fileAddress = fileAddress.replace('/', os.sep)
    # read the input which is the csv file and comma is the delimiter
    locationGroupData = pd.read_csv(fileAddress, sep=',')
    
    # res is a dictionary
    res = {}
    for column in locationGroupData.columns:
        temp = list(locationGroupData[column][:]) + [np.NaN]
        temp = temp[:temp.index(np.NaN)]
        temp = [store.replace('_', ' ') if '_' in store else store for store in temp ]
        res[column] = temp   
    
    # returns the dictionary res
    return res

def readAverageDemands(fileAddress: str = "./Data/AverageDemands.csv", roundUp: bool = True)->Tuple[List[str], Dict[str, Dict[str, int]]]:
    """
    Returns the list of all stores and the demands for all stores from Monday to Saturday
    
    Parameters
    ---------
    fileAddress: str
                 Average demand of pallets for each supermarket
    
    Returns
    -------
    res: dictionary
         Stores and the demands for all store from Monday to Saturday
    
    """
    fileAddress = fileAddress.replace('/', os.sep)
    averageDemands = pd.read_csv(fileAddress, sep=',',index_col=0)
    averageDemands['WeekdayAvg'] = averageDemands[['Monday','Tuesday','Wednesday','Thursday','Friday']].mean(numeric_only=True, axis=1)

    stores = averageDemands.index
    if roundUp:
        res = {day: {store: np.ceil(averageDemands[day][store]) for store in stores} for day in averageDemands.columns}
    else:
        res = {day: {store: averageDemands[day][store] for store in stores} for day in averageDemands.columns}
    
    # return stores, res
    return res
    
def readTravelDurations(fileAddress: str = "./Data/WoolworthsTravelDurations.csv")->pd.DataFrame:
    """
    Returns the adjacency matrix for the stores with the values converted to hours
    
    Parameters
    ----------
    fileAddress: str
                 Travel durations in seconds between each pair of stores and distribution points
    
    Returns
    -------
    Dataframe: Adjacency matrix for the stores with the durations in hours
    
    """
    fileAddress = fileAddress.replace('/', os.sep)
    # Returns a transformed dataframe
    return pd.read_csv(fileAddress,sep=',',index_col=0).applymap(lambda x: x/3600)

def readStoreCoordinates(fileAddress: str = "./Data/WoolworthsLocations.csv")->pd.DataFrame:
    """
    Read the longitude and latitude values from the WoolworthsLocations csv
    
    Parameters
    ----------
    fileAddress: str
                 Latitude and longitude of Woolworths supermarkets
                 
    Returns
    ------
    Dataframe: Latitude and longtitude of each Woolworth supermarket
    """
    fileAddress = fileAddress.replace('/', os.sep)
    return pd.read_csv(fileAddress, sep=",",usecols=['Store','Lat','Long']).set_index('Store')
    
def storeRoutes(partitions, fileAddress='Data/newRoutes.json'):
    """
    Converts routes to a JSON file

    Parameters:
    ----------
     partitions: Dict[str, List[List[Tuple(List[str],float)]]]
                 The partitions for each region
        
     fileAddress: str
                  name of the file to store the data in, should be a json
    """
    fileAddress = fileAddress.replace('/', os.sep)
    fp = open(fileAddress, mode='w')

    json.dump(partitions,fp)
    fp.close()
    return

def readRoutes(fileAddress='Data/newRoutes.json'):
    """
    Reads in a dict of routes stored as a JSON using storeRoute()

    Parameters:
    ----------
    fileAddress: str
    
    Returns
    -------
    temp: JSON
          Contains routes
    
    """
    fileAddress = fileAddress.replace('/', os.sep)
    fp = open(fileAddress, mode='r')

    temp = json.load(fp)
    fp.close()
    return temp

def readDataWithStats(fileAddress: str = 'Data/WoolworthsDemands.csv', roundUp: bool = False):
    '''
    
    Parameters
    ----------
    fileAddress: str
                Pallet demands for each supermarket for a four-week period
    
    Returns
    -------
    newDf: DataFrame
    
    '''
    fileAddress = fileAddress.replace('/', os.sep)

    df = pd.read_csv(fileAddress).set_index('Store')
    df.columns = pd.to_datetime(df.columns)
    
    # geting weekdays 
    validDays = [d for d in df.columns if d.weekday() < 5] # weekday columns
    # print(df[:5])
    demands = df.loc[:,validDays].mean(axis=1)
    # mins    = df.loc[:,validDays].min(axis=1)
    stds   = df.loc[:,validDays].std(axis=1)
    # maxs    = df.loc[:,validDays].max(axis=1)
    # print(maxs[:5])
    
    # newDf = pd.DataFrame(columns=["Store", "Demand", "min", "max", "std"])
    newDf = pd.DataFrame(columns=["Store", "Demand", "std"])
    newDf["Store"] = df.index
    newDf.set_index("Store", inplace=True)

    newDf["Demand"] = demands.values
    # newDf["min"] = mins.values
    # newDf["max"] = maxs.values
    newDf["std"] = stds.values

    if roundUp:
        for column in newDf.columns:
            newDf[column] = newDf[column].apply(np.ceil)
    
    return newDf


def readSaturdayWithStats(fileAddress: str = "Data/WoolworthsDemands.csv", roundUp: bool = False):
    '''
    
    Parameters
    ----------
    fileAddress: str
                 Pallet demands for each supermarket for a four-week period
    
    Returns
    -------
    newDf: DataFrame
    
    '''
    fileAddress = fileAddress.replace('/', os.sep)

    df = pd.read_csv(fileAddress).set_index('Store')
    df.columns = pd.to_datetime(df.columns)
    
    # geting weekdays 
    validDays = [d for d in df.columns if d.weekday() == 5] # saturday column
    # print(df[:5])
    demands = df.loc[:,validDays].mean(axis=1)
    mins    = df.loc[:,validDays].min(axis=1)
    maxs    = df.loc[:,validDays].max(axis=1)

    # print(maxs[:5])
    newDf = pd.DataFrame(columns=["Store", "Demand", "min", "max"])
    newDf["Store"] = df.index
    newDf["Demand"] = demands.values
    newDf["min"] = mins.values
    newDf["max"] = maxs.values

    newDf = newDf[newDf["Demand"] > 0]
    newDf.set_index("Store", inplace=True)

    if roundUp:
        for column in newDf.columns:
            newDf[column] = newDf[column].apply(np.ceil)

    return newDf

# --------------------------------------------------------------
# NEW FUNCTION, DONT DELETE
def readLocationGroupsWithStoreClosure(toClose: List[List[str]])->Dict[str, List[str]]:
    
    stores = readLocationGroups()  

    for store in toClose:
        for region in stores:
            if store[0] in stores[region]:
                stores[region].remove(store[0])
        
    return stores
    

def readDemandsWithStoreClosure(toClose: List[List[str]], transferRatio = 0.5, roundUp: bool = False):
    demandDict = readAverageDemands()

    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
        del demandDict[day]

    
    for storeGroups in toClose:    
        demandDict["WeekdayAvg"][storeGroups[1]] += demandDict["WeekdayAvg"][storeGroups[0]]*transferRatio
        demandDict["Saturday"][storeGroups[1]] += demandDict["Saturday"][storeGroups[0]]*transferRatio
        del demandDict["WeekdayAvg"][storeGroups[0]]
        del demandDict["Saturday"][storeGroups[0]]

    if roundUp:
        for day in demandDict:
            for store in demandDict[day]:
                demandDict[day][store] = np.ceil(demandDict[day][store])
        
    return demandDict


if __name__=="__main__":
    # groups = readLocationGroups()
    # stores, demands = readAverageDemands(roundUp=True)
    # durationAdjacencyMatrix = readTravelDurations()
    # locations = readStoreCoordinates()
    # print(locations.head())
    # print(locations.columns)
    # print(demands)
    # print(readSaturdayWithStats()[:5])
    # print(readDemandsWithStoreClosure())
    # print(readLocationGroupsWithStoreClosure())
    # dems = readDemandsWithStoreClosure()    
    # temp = readLocationGroupsWithStoreClosure()
    # allStores = []
    # for region in temp:
    #     allStores.extend(temp[region])

    # print(set(allStores) ^ set(dems["Saturday"].keys()))
    
    data = readRoutes("simulationResults.json")
    routes = data["Saturday"]["evening"]["routes"]["upper"]
    print(routes)
