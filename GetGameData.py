import numpy as np
import pandas as pd
import requests
import json
import time
from pandas.io.json import json_normalize

API_KEY = ""

def extract_values(obj, key):
    """Pull all values of specified key from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    results = extract(obj, arr, key)
    return results

def test_run():
    #fake header from Chrome, because GiantBomb doesn't like the default python request header
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}  # This is chrome,

    # get all games for a platform - name, id, guid
    url = "https://www.giantbomb.com/api/games"
    api_info = "/?api_key=" + API_KEY
    field_list = "&format=json&filter=platforms:145&field_list=name,id,guid"

    response = requests.get(url + api_info+field_list, headers=headers)
    jsonResponse = response.json()

    ps4 = json_normalize(jsonResponse, record_path='results')

    game_count = jsonResponse['number_of_total_results']

    # we are requesting 100 records at a time
    game_count += game_count % 100

    url = "https://www.giantbomb.com/api/games/"
    api_info = "?api_key=" + API_KEY
    filter = "&format=json&filter=platforms:145" #145 - Xbox One, 146 - PS4, 157 - Switch
    field_list = "&field_list=name,id,guid"
    print("game count = " + str(game_count))

    #create a dataframe with all  games - game name, guid, and id
    # giantbomb limits us to 100 games per api call
    for x in range(100, game_count, 100):
        url_page = url + api_info + filter + '&offset=' + str(x) + field_list
        time.sleep(2)  # limit request to every 2 seconds to avoid rate limit
        response = requests.get(url_page, headers=headers)
        jsonResponse = response.json()
        ps4 = pd.concat([ps4,json_normalize(jsonResponse, record_path='results')], sort=False, ignore_index= True)

    ps4['Platform'] = 'XBoxOne' #update this to match the platform you are querying for
    ps4['Rating'] = ''

    #get genre for each game
    url = "https://www.giantbomb.com/api/game/"
    api_info = "/?api_key=" + API_KEY

    #get the genre and ESRB rating for each game in the dataframe
    for index, row in ps4.iterrows():
        url_game = url +  row['guid'] + api_info + "&format=json" + "&field_list=genres"
        time.sleep(2)  # limit requests to every 2 seconds for rate limit
        response = requests.get(url_game, headers=headers)
        jsonResponse = response.json()
        genres = extract_values(jsonResponse, 'name')

        for genre in genres:
            ps4.at[index,genre] = 'Yes'

        url_game = url + row['guid'] + api_info + "&format=json" + "&field_list=original_game_rating"
        time.sleep(2)  # limit requests to every 2 seconds
        response = requests.get(url_game, headers=headers)
        jsonResponse = response.json()

        # ratings field may include ratings from multiple countries
        # we just want the ESRB one
        ratings = extract_values(jsonResponse, 'name')
        for rating in ratings:
            if ('ESRB' in rating):
                ps4.at[index,'Rating'] = rating[6:] #strip out the 'ESRB: ' from the rating

    ps4.to_csv("xboxone.csv", index=False)

if __name__ == "__main__":
    test_run()