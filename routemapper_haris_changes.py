from hashlib import new
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
import polygon_functions
import other_functions
import itertools as it
import time

key = "AujNTOdwhaMihu2M2fT38-KQ_9rg26JFnhn-kE5S20BUTZlJ1uNzoxU-mdt8bi2R"

class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y

def get_df_combo(coords1,coords2):
    coords1 = coords1.values.tolist()
    coords2 = coords2.values.tolist()
    intersects1 = []
    intersects2 = []
    for i in range(len(coords1)-1):
        y1,x1 = coords1[i]
        y2,x2 = coords1[i+1]
        for j in range(len(coords2)-1):
            y3,x3 = coords2[j] 
            y4,x4 = coords2[j+1]
            p1 = Point(x1, y1)
            q1 = Point(x2, y2)
            p2 = Point(x3, y3)
            q2 = Point(x4, y4)
            if polygon_functions.doIntersect(p1, q1, p2, q2):
                intersects1.append(i)
                intersects2.append(j)
    df_coords1 = pd.DataFrame(coords1,columns = ["latitude", "longitude"])
    df_coords2 = pd.DataFrame(coords2,columns = ["latitude", "longitude"])
    df_combo = pd.DataFrame(columns=df_coords1.columns)
    for i in range(len(intersects1)-1):
        if i%2==0:
            rows_between = df_coords1.iloc[intersects1[i]:intersects1[i+1]]
        else:
            rows_between = df_coords2.iloc[intersects2[i]:intersects2[i+1]]
        df_combo = df_combo.append(rows_between)
    return df_combo

def get_union(postcodes, transportType, travelTime, auth_key=key):
    #obtain all coord info for all provided points
    locs = [str(other_functions.get_location(x.replace(" ",""))).replace(" ","").replace("(","").replace(")","") for x in postcodes]
    urls = ['https://dev.virtualearth.net/REST/v1/Routes/Isochrones?waypoint={loc}&maxtime={time}&timeUnit=minute&travelMode={transport}&key={auth_key}'.format(
        loc=x,
        time=travelTime,
        transport=transportType,
        auth_key=auth_key) for x in locs]
    responses = [requests.get(url) for url in urls]
    print(responses)
    contents = [json.loads(response.content) for response in responses]
    polygonses = [content['resourceSets'][0]['resources'][0]['polygons'] for content in contents]
    coordses0 = [[pd.DataFrame(polygon['coordinates'][0],columns=["latitude", "longitude"]) for polygon in polygons] for polygons in polygonses]
    #coordses0 = [pd.DataFrame(content['resourceSets'][0]['resources'][0]['polygons'][0]['coordinates'][0],columns=["latitude", "longitude"]) for content in contents]

    #generate meshgrid that contains all the areas
    t0 = time.time()
    xx,yy = polygon_functions.generate_meshgrid(coordses0)
    #plot each area on the combined meshgrid 
    areases = [[polygon_functions.generate_area(coords,xx,yy) for coords in coordses] for coordses in coordses0]
    #combine the values - number at each gridpoint show how many areas cover that point
    combined_areas = sum([sum(areas) for areas in areases])
    t1 = time.time()
    print("Time:"+str(t1-t0))
    #plotting
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.imshow(combined_areas, aspect='auto', cmap=plt.cm.gray, interpolation='nearest')
    plt.show()
    exit(-1)

    #start loop through areas to get mutual intersection
    #sum to n-1 different intersects
    N_postcodes = len(coordses0)
    N_combos = int(((N_postcodes-1)*N_postcodes)/2)
    #loop variables
    df_combo_list = [None]*N_combos
    k = 0
    coordses = coordses0
    origs = coordses
    print (N_postcodes)
    while len(df_combo_list) == N_combos and k<N_postcodes:
        coordses_out = coordses
        df_combo_list = []
        for coords1,coords2 in it.combinations(coordses,2):
            df_combo_list.append(get_df_combo(coords1,coords2))
        coordses = df_combo_list
        k = k+1
    
    #output is N_postcodes coordinate dataframes
    #if all areas intersect, then output should be N dataframes that are roughly equivalent.
    #otherwise will output the best combination (eg if there's 3 postcodes, but there's no triple intersect, will return the double intersect areas in three dataframes)
    #print(coordses_out)
    #exit(-1)
    
    # if len(intersects1) > 0:   
    #     df_combo = df_combo.append(df_coords2.iloc[intersects2[-1]:intersects2[0]])
    #     latitude = (df_combo['latitude'].to_list())
    #     longitude = (df_combo['longitude'].to_list())
    #     centroid = Polygon(zip(latitude, longitude)).centroid
    #     locality = other_functions.get_postcode(f"{centroid.x},{centroid.y}")
    #     print (f"Based on your inputs, we suggest you look for housing in {locality}")
    #     print (locality)
    mymap = plt.imread('map11.png')
    fig, ax = plt.subplots(figsize = (8,7))
    # for each in origs:
    #     ax.plot(each.longitude, each.latitude)
    for each in df_combo_list:
        print (each)
        ax.plot(each.longitude, each.latitude)
    # print (df_combo_list[0])
    # ax.plot(df_combo_list[0].latitude, df_combo_list[0].longitude)
    #ax.plot(df_coords2.longitude, df_coords2.latitude)
    # if len(intersects1) > 0:   
    #     ax.plot(df_combo.longitude, df_combo.latitude, color = 'green')
    #     ax.set_title(f'{travelTime} minute {transportType} radius from {postcode1} and {postcode2}. \n We suggest you look for housing in {locality}')
    # else:
    #     ax.set_title(f'{travelTime} minute {transportType} radius from {postcode1} and {postcode2}. \n There is no area that allow you both to get to work on time, try changing the above parameters')
    #ax.set_xlim(-0.2107,-0.0498)
    #ax.set_ylim(51.4768,51.5511)
    lims = (-0.2107, -0.0498, 51.4768, 51.5511,)
    ax.imshow(mymap, extent = lims, aspect= 'equal')
    #plt.fill(df_coords1.longitude, df_coords1.latitude, color='blue', alpha = 0.2)
    #plt.fill(df_coords2.longitude, df_coords2.latitude, color='orange', alpha = 0.2)
    #if len(intersects1) > 0:   
    #    plt.fill(df_combo.longitude, df_combo.latitude, color='green', alpha = 0.4)
    #else:
    #    print ("There is no area that allow you both to get to work on time, please get a new job")
    plt.show()
        

get_union(["SE14QB", "SE1 0BE","E14 4AD"],"Transit", 30)