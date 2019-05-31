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

def radarchart(df_saved_tracks):
    cluster_features = ['acousticness', 'danceability', 'instrumentalness', 'energy', 'speechiness']
    df_recent = df_saved_tracks.loc[df_saved_tracks['added_at_year'] == 2019]

    df_cluster = df_recent[cluster_features]
    X = np.array(df_cluster)
    scaler = StandardScaler()
    scaler.fit(X)
    X = scaler.transform(X)

    num_clusters = 5
    kmeanModel = KMeans(n_clusters=num_clusters, max_iter=10000, init='k-means++', random_state=123).fit(X)
    df_recent.loc[:, 'cluster'] = kmeanModel.labels_
    radar_col = cluster_features + ['cluster']

    # feature average for each cluster as a radar chart
    df_radar = df_recent[radar_col]
    df_radar = df_radar.groupby('cluster').mean().reset_index()

    return df_radar


def make_radar(row, title, color, dframe, num_clusters):
    # number of variable
    categories = list(dframe)[1:]
    N = len(categories)

    # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
    angles = [n / float(N) * 2 * math.pi for n in range(N)]
    angles += angles[:1]

    # Initialise the radar plot
    ax = plt.subplot(2, math.ceil(num_clusters / 2), row + 1, polar=True, )

    # If you want the first axis to be on top:
    ax.set_theta_offset(math.pi / 2)
    ax.set_theta_direction(-1)

    # Draw one axe per variable + add labels labels yet
    plt.xticks(angles[:-1], categories, color='grey', size=14)

    # Draw ylabels
    ax.set_rlabel_position(0)
    plt.yticks([0.2, 0.4, 0.6, 0.8], ["0.2", "0.4", "0.6", "0.8"], color="grey", size=8)
    plt.ylim(0, 1)

    # Ind1
    values = dframe.loc[row].drop('cluster').values.flatten().tolist()
    values += values[:1]
    ax.plot(angles, values, color=color, linewidth=2, linestyle='solid')
    ax.fill(angles, values, color=color, alpha=0.4)

    # Add a title
    plt.title(title, size=16, color=color, y=1.06)