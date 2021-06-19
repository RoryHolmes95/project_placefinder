import requests
import json
import matplotlib.pyplot as plt

key = "AujNTOdwhaMihu2M2fT38-KQ_9rg26JFnhn-kE5S20BUTZlJ1uNzoxU-mdt8bi2R"


def get_location(postcode, auth_key=key):
    url = f'http://dev.virtualearth.net/REST/v1/Locations/UK/{postcode}?key={auth_key}'
    response = requests.get(url).content
    response = json.loads(response)
    return response['resourceSets'][0]['resources'][0]['point']['coordinates'][0], response['resourceSets'][0]['resources'][0]['point']['coordinates'][1]

def get_time_and_distance(originLong, originLat, origin2Long, origin2Lat, destinationLong, destinationLat, transport, max_time, auth_key=key):
    url = f'https://dev.virtualearth.net/REST/v1/Routes/DistanceMatrix?origins={originLong},{originLat};{origin2Long},{origin2Lat}&destinations={destinationLong},{destinationLat}&travelMode={transport}&key={auth_key}'
    response = requests.get(url).content
    response = json.loads(response)
    distance = (response['resourceSets'][0]['resources'][0]['results'][0]['travelDistance'])
    duration = (response['resourceSets'][0]['resources'][0]['results'][0]['travelDuration'])
    distance2 = (response['resourceSets'][0]['resources'][0]['results'][1]['travelDistance'])
    duration2 = (response['resourceSets'][0]['resources'][0]['results'][1]['travelDuration'])
    print (f"this journey is approx {distance:.1f}km's and will take around {duration:.0f} minutes")
    print (f"this journey is approx {distance2:.1f}km's and will take around {duration2:.0f} minutes")
    if (float(duration) < float(max_time)) & (float(duration2) < float(max_time)):
        print ("great, you can live here!")
        print ()
    else:
        print ("sorry, one of you will be having a hella commute...")


def main():
    first_origin = input("where does person A work? ")
    second_origin = input("and where does person B work? ")
    first_destination = input("and where do you want to live? ")
    transport = input("and how will you get there? ")
    originLong, originLat = get_location(first_origin)
    origin2Long, origin2Lat = get_location(second_origin)
    destinationLong, destinationLat = get_location(first_destination)
    max_time = input("what's the max amount of time either of you want to travel for? ")
    get_time_and_distance(originLong, originLat, origin2Long, origin2Lat, destinationLong, destinationLat, transport, max_time)

main()

def isochrone(auth_key=key):
    url = f'https://dev.virtualearth.net/REST/v1/Routes/Isochrones?waypoint=51.5072,-0.1353&maxtime=25&timeUnit=minute&travelMode=Walking&key={auth_key}'
    response = requests.get(url).content
    response = json.loads(response)
    coords = response['resourceSets'][0]['resources'][0]['polygons'][0]['coordinates'][0]
    print (coords)
    url2 = f'https://dev.virtualearth.net/REST/v1/Routes/Isochrones?waypoint=51.4896,-0.1362&maxtime=25&timeUnit=minute&travelMode=Walking&key={auth_key}'
    response2 = requests.get(url2).content
    response2 = json.loads(response2)
    coords2 = response2['resourceSets'][0]['resources'][0]['polygons'][0]['coordinates'][0]
    df = pd.DataFrame(coords)
    df.columns = ["latitude", "longitude"]
    df2 = pd.DataFrame(coords2)
    df2.columns = ["latitude", "longitude"]
    BBox = (df.longitude.min(), df.longitude.max(), df.latitude.min(), df.latitude.max())
    #print (BBox)
    #print (df)
    mymap = plt.imread('map11.png')
    fig, ax = plt.subplots(figsize = (8,7))
    ax.plot(df.longitude, df.latitude)
    ax.plot(df2.longitude, df2.latitude)
    ax.set_title('25 minute walk radius from Pimlico and Leicester Square')
    ax.set_xlim(-0.2107,-0.0498)
    ax.set_ylim(51.4768,51.5511)
    lims = (-0.2107, -0.0498, 51.4768, 51.5511,)
    ax.imshow(mymap, extent = lims, aspect= 'equal')
    plt.fill_between(df.longitude, df.latitude, color='blue', alpha = 0.1)
    plt.fill_between(df2.longitude, df2.latitude, color='orange', alpha = 0.1)
    plt.show()

#isochrone()
