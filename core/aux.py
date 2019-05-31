import spotipy
import spotipy.util as util
from datetime import datetime
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import matplotlib.pyplot as plt
import calendar
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import numpy as np
import math

def table(sp):
    df_saved_tracks = pd.DataFrame()
    track_list = ''
    added_ts_list = []
    artist_list = []
    title_list = []
    added_ts_list_year = []
    added_ts_list_month = []
    added_ts_list_month_index = []

    more_songs = True
    offset_index = 0

    while more_songs:
        songs = sp.current_user_saved_tracks(offset=offset_index)

        for song in songs['items']:
            # join track ids to a string for audio_features function
            track_list += song['track']['id'] + ','

            # get the time when the song was added
            added_ts_list.append(datetime.strptime(song['added_at'], '%Y-%m-%dT%H:%M:%SZ'))
            added_ts_list_year.append(datetime.strptime(song['added_at'], '%Y-%m-%dT%H:%M:%SZ').year)
            month_abbr = calendar.month_abbr[
                             (datetime.strptime(song['added_at'], '%Y-%m-%dT%H:%M:%SZ').month)] + "," + str(
                datetime.strptime(song['added_at'], '%Y-%m-%dT%H:%M:%SZ').year)
            added_ts_list_month.append(month_abbr)
            added_ts_list_month_index.append(datetime.strptime(song['added_at'], '%Y-%m-%dT%H:%M:%SZ').month)
            # get the title of the song
            title_list.append(song['track']['name'])

            # get all the artists in the song
            artists = song['track']['artists']
            artists_name = ''
            for artist in artists:
                artists_name += artist['name'] + ','
            artist_list.append(artists_name[:-1])
        # print(type(month_abbr))
        # get the track features and append into a dataframe
        track_features = sp.audio_features(track_list[:-1])
        df_temp = pd.DataFrame(track_features)
        df_saved_tracks = df_saved_tracks.append(df_temp)
        track_list = ''

        if songs['next'] == None:
            # no more songs in playlist
            more_songs = False
        else:
            # get the next n songsss 'st
            offset_index += songs['limit']

    # include timestamp added, title and artists of a song
    df_saved_tracks['added_at'] = added_ts_list
    df_saved_tracks['song_title'] = title_list
    df_saved_tracks['artists'] = artist_list
    df_saved_tracks['added_at_year'] = added_ts_list_year
    df_saved_tracks['added_at_month'] = added_ts_list_month
    df_saved_tracks["added_at_month_index"] = added_ts_list_month_index

    return df_saved_tracks