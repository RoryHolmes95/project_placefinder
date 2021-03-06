from hashlib import new
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
import polygon_functions
import other_functions

key = "AujNTOdwhaMihu2M2fT38-KQ_9rg26JFnhn-kE5S20BUTZlJ1uNzoxU-mdt8bi2R"

class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y

def get_union(postcode1, postcode2, transportType, travelTime, auth_key=key):
    loc1 = str(other_functions.get_location(postcode1.replace(" ",""))).replace(" ","").replace("(","").replace(")","")
    loc2 = str(other_functions.get_location(postcode2.replace(" ",""))).replace(" ","").replace("(","").replace(")","")
    url = f'https://dev.virtualearth.net/REST/v1/Routes/Isochrones?waypoint={loc1}&maxtime={travelTime}&timeUnit=minute&travelMode={transportType}&key={auth_key}'
    response = requests.get(url).content
    response = json.loads(response)
    coords = response['resourceSets'][0]['resources'][0]['polygons'][0]['coordinates'][0]
    url2 = f'https://dev.virtualearth.net/REST/v1/Routes/Isochrones?waypoint={loc2}&maxtime={travelTime}&timeUnit=minute&travelMode={transportType}&key={auth_key}'
    response2 = requests.get(url2).content
    response2 = json.loads(response2)
    coords2 = response2['resourceSets'][0]['resources'][0]['polygons'][0]['coordinates'][0]
    intersects = []
    intersects2 = []
    for i in range(len(coords)-1):
        y1 = coords[i][0]
        x1 = coords[i][1]   
        y2 = coords[i+1][0]
        x2 = coords[i+1][1]
        for x in range(len(coords2)-1):
            y3 = coords2[x][0]
            x3 = coords2[x][1]  
            y4 = coords2[x+1][0]
            x4 = coords2[x+1][1]
            p1 = Point(x1, y1)
            q1 = Point(x2, y2)
            p2 = Point(x3, y3)
            q2 = Point(x4, y4)
            if polygon_functions.doIntersect(p1, q1, p2, q2):
                intersects.append(i)
                intersects2.append(x)
    coords = pd.DataFrame(coords)
    coords.columns = ["latitude", "longitude"]
    coords2 = pd.DataFrame(coords2)
    coords2.columns = ["latitude", "longitude"]
    df3 = pd.DataFrame(columns=coords.columns)
    for i in range(len(intersects)-1):
        if i%2==0:
            rows_between = coords.iloc[intersects[i]:intersects[i+1]]
        else:
            rows_between = coords2.iloc[intersects2[i]:intersects2[i+1]]
        df3 = df3.append(rows_between)
    if len(intersects) > 0:   
        df3 = df3.append(coords2.iloc[intersects2[-1]:intersects2[0]])
        latitude = (df3['latitude'].to_list())
        longitude = (df3['longitude'].to_list())
        poly = zip(latitude, longitude)
        polygon = Polygon(poly)
        centroid = (polygon.centroid)
        locality = other_functions.get_postcode(f"{centroid.x},{centroid.y}")
        print (f"Based on your inputs, we suggest you look for housing in {locality}")
        print (locality)
    mymap = plt.imread('map11.png')
    fig, ax = plt.subplots(figsize = (8,7))
    ax.plot(coords.longitude, coords.latitude)
    ax.plot(coords2.longitude, coords2.latitude)
    if len(intersects) > 0:   
        ax.plot(df3.longitude, df3.latitude, color = 'green')
        ax.set_title(f'{travelTime} minute {transportType} radius from {postcode1} and {postcode2}. \n We suggest you look for housing in {locality}')
    else:
        ax.set_title(f'{travelTime} minute {transportType} radius from {postcode1} and {postcode2}. \n There is no area that allow you both to get to work on time, try changing the above parameters')
    ax.set_xlim(-0.2107,-0.0498)
    ax.set_ylim(51.4768,51.5511)
    lims = (-0.2107, -0.0498, 51.4768, 51.5511,)
    ax.imshow(mymap, extent = lims, aspect= 'equal')
    plt.fill(coords.longitude, coords.latitude, color='blue', alpha = 0.2)
    plt.fill(coords2.longitude, coords2.latitude, color='orange', alpha = 0.2)
    if len(intersects) > 0:   
        plt.fill(df3.longitude, df3.latitude, color='green', alpha = 0.4)
    else:
        print ("There is no area that allow you both to get to work on time, please get a new job")
    plt.show()
        

get_union("W8 6UG", "EC1V 7HP", "Walking", 30)