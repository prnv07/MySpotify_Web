import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from io import BytesIO
import base64



from django.shortcuts import render, redirect
import requests_oauthlib
from requests_oauthlib import OAuth2Session
from django.http import HttpResponseRedirect
import spotipy
import spotipy.util as util
import requests
from django.http import HttpResponseRedirect
from datetime import datetime
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

import calendar
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import numpy as np
from math import *
from . import aux
# Create your views here.

def UserNameView(request):
    return render(request, 'core/UserName.html')

def ExecuteScript(request):
    # username = request.POST['username']
    # scope = "user-library-read"
    # export SPOTIPY_CLIENT_ID ='3aa12f8e691c4df69ea5cf90a8d14b83'
    # export SPOTIPY_CLIENT_SECRET ='380a5fc6c96e4fdcaf568425b919a00e'
    # export SPOTIPY_REDIRECT_URI ='http://localhost:8888'
    # client_credentials_manager = SpotifyClientCredentials(client_id='3aa12f8e691c4df69ea5cf90a8d14b83', client_secret='380a5fc6c96e4fdcaf568425b919a00e')
    # token = util.prompt_for_user_token(username, scope, client_id='35018e55ab1d418f85142ed667b3f069',
    #                                    client_secret='5150cff246404d1795f3d4c2c559e902',
    #                                    redirect_uri='http://localhost:8888/callback/')
    #
    # # playlists = sp.user_playlists('rckprnv')
    # if token:
    #     sp = spotipy.Spotify(auth=token)
    #     results = sp.current_user_saved_tracks()
    #     for item in results['items']:
    #         track = item['track']
    #         print(track['name'] + ' - ' + track['artists'][0]['name'])
    # else:
    #     print("Can't get token for"), username
    # URL = "https://accounts.spotify.com/authorize/"
    #
    # # location given here
    # # location = "delhi technological university"
    #
    # # defining a params dict for the parameters to be sent to the API
    # PARAMS = {'client_id': '35018e55ab1d418f85142ed667b3f069', 'scope': 'user-library-read',
    #           'redirect_uri': 'http://127.0.0.1:8000/show_stats/', 'response_type': 'code'}
    #
    # # sending get request and saving the response as response object
    # r = requests.get(url=URL, params=PARAMS)
    # return redirect(str(r.url))
    scope = ['user-library-read']
    client_id = '35018e55ab1d418f85142ed667b3f069'
    redirect_uri = 'http://127.0.0.1:8000/show_stats/'
    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri,
                               scope=scope)
    authorization_url, state = oauth.authorization_url(
        "https://accounts.spotify.com/authorize/",
        # access_type and prompt are Google specific extra
        # parameters.
        )

    return redirect(str(authorization_url))


    #authorization_response = raw_input('Enter the full callback URL')


def ShowStats(request):
    # export OAUTHLIB_INSECURE_TRANSPORT=1
    # scope = ['user-library-read']
    client_id = '35018e55ab1d418f85142ed667b3f069'
    redirect_uri = 'http://127.0.0.1:8000/show_stats/'
    # oauth = OAuth2Session(client_id, redirect_uri=redirect_uri,
    #                       scope=scope)
    client_secret = '5150cff246404d1795f3d4c2c559e902'
    #
    # token = oauth.fetch_token(
    #     'https://accounts.spotify.com/api/token',
    #     authorization_response=request.build_absolute_uri(),
    #     # Google specific extra parameter used for client
    #     # authentication
    #     client_secret=client_secret,
    #     client_id = client_id,
    #     grant_type = 'authorization_code',
    #     redirect_uri = redirect_uri,
    #
    #     )\
    API_ENDPOINT = 'https://accounts.spotify.com/api/token'
    data = {'grant_type':"authorization_code",
        'code':request.GET.get('code'),
        'redirect_uri':redirect_uri,
        'client_id':client_id,
        'client_secret': client_secret
        }
    r = requests.post(url=API_ENDPOINT, data=data)
    data = r.json()
    sp = spotipy.Spotify(auth=data["access_token"])
    results = sp.current_user_saved_tracks()

    df_saved_tracks = aux.table(sp)

    df_mean = df_saved_tracks.loc[df_saved_tracks['added_at_year'] == 2019]

    df_mean = df_mean.groupby(['added_at_month']).mean().sort_values('added_at_month_index')

    df_mean.plot(kind='line', y='acousticness', figsize=(10, 10))
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300)
    image_acousticness = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
    buf.close()

    df_mean.plot(kind='line', y='danceability', figsize=(10, 10))
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300)
    image_danceability = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
    buf.close()

    df_mean.plot(kind='line', y='instrumentalness', figsize=(10, 10))
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300)
    image_instrumentalness = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
    buf.close()

    df_mean.plot(kind='line', y='speechiness', figsize=(10, 10))
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300)
    image_speechiness = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
    buf.close()

    df_radar = aux.radarchart(df_saved_tracks)

    plt.figure(figsize=(24, 15))

    # Create a color palette:
    my_palette = plt.cm.get_cmap("Set1", len(df_radar.index))

    # Create cluster name
    title_list = ['Group 1', 'Group 2', 'Group 3', 'Group 4', 'Group 5']

    # Loop to plot
    for row in range(0, len(df_radar.index)):
        aux.make_radar(row=row, title=str(df_radar['cluster'][row]) + ' : ' + title_list[row],
                   color=my_palette(row), dframe=df_radar, num_clusters=len(df_radar.index))

    # # Show plot
    # plt.show()

    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300)
    image_radars = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
    buf.close()

    context = {
           # 'results' : results["items"],
            'image_acousticness'     : image_acousticness,
            'image_danceability'     : image_danceability,
            'image_instrumentalness' : image_instrumentalness,
            'image_speechiness'      : image_speechiness,
            'image_radars'           : image_radars,
    }

    return render(request, 'core/Album.html', context)
