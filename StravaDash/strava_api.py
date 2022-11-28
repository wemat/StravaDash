import requests
import pandas as pd

def get_data():
    api_dict = {}

    with open('api_params.txt','r') as api_params:
        for line in api_params.readlines():
            key,value = line.partition(':')[::2]
            api_dict[key]= value.strip()

    activities_url = 'https://www.strava.com/api/v3/athlete/activities'

    auth_url = 'https://www.strava.com/oauth/token'
    payload = {
        'client_id': api_dict['client_id'],
        'client_secret': api_dict['client_secret'],
        'refresh_token': api_dict['refresh_token'],
        'grant_type': 'refresh_token',
        'f': 'json'
    }

    res = requests.post(auth_url, data=payload, verify=False)

    access_token = res.json()['access_token']

    header = {'Authorization': 'Bearer ' + access_token}

    page= 1
    requested_data = []
    while True:
        param = {'per_page':200, 'page':page}
        response = requests.get(activities_url,headers=header,params=param).json()
        if len(response)==0:
            break
        requested_data.append(response)
        page+=1

    df =pd.DataFrame(*requested_data)
    return df

def preprocess(df):
    df['kilometres'] = df['distance'] / 1000
    df['start_date'] = pd.to_datetime(df['start_date'])
    df['year'] = df['start_date'].dt.year
    df['month'] = df['start_date'].dt.month
    df['quarter'] = df['start_date'].dt.quarter
    df['weekday'] = df['start_date'].dt.weekday
    df['year_quarter'] = df['year'].astype(str) + "_" + df['quarter'].astype(str)
    df['training_hours'] = df['moving_time'] / 3600
    df.index = df['start_date']
    df = df.sort_index()

    df['average_speed_strava'] = df['average_speed']
    df['average_speed'] = df['kilometres'] / df['training_hours']
    df['avg_speed_elevation_gain'] = df['total_elevation_gain'] / df['training_hours']
    df.loc[:, 'dist_cat'] = df[['type', 'kilometres']].apply(
        lambda x: get_cats(x['kilometres'], x['type'], all_cats), axis=1)
    return df

def get_cats(x,activity,all_cats):
    """find the closest category based on smallest absolute distance"""
    cats = all_cats[activity]
    for key,val in cats.items():
        upper,lower=val
        if upper< x < lower:
            return key

ride_cats = {'short':[0,30],'medium':[30,40],'long':[40,999]}
run_cats = {'short':[0,7],'medium':[7,12],'long':[12,999]}
all_cats = {'Ride':ride_cats,'Run':run_cats}

