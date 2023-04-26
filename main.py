#!/usr/bin/env python
# coding: utf-8

# In[65]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import streamlit as st
import base64


# In[2]:


def main():
    st.set_page_config(page_title="My Beautiful Page")
    st.title("My Beautiful Page")

#     # Add text inputs and button
#     input1 = st.text_input("Enter your name")
#     input2 = st.text_input("Enter your favorite color")

    df = pd.read_csv('dataset_sentiment.csv', header=0)
    df.dropna(how='any', inplace=True)
    df.drop_duplicates(inplace=True)
    df = df.drop_duplicates(subset = ['track_id'],keep = 'last').reset_index(drop = True)
    df.drop(['Unnamed: 0','Unnamed: 0.1', 'track_id'],axis=1,inplace=True)

    categorical_vars = df.select_dtypes(include=['object','bool']).columns
    categorical_vars = categorical_vars.to_list()
    categorical_vars.remove('track_name')


    le = LabelEncoder()
    df_encode = df.copy()
    df_encode[categorical_vars] = df_encode[categorical_vars].apply(le.fit_transform)


    # rs = np.random.RandomState(0)
    # # df = pd.DataFrame(rs.rand(10, 10))
    # corr = df_encode.corr()
    # corr.style.background_gradient(cmap='coolwarm')

    audio_features = ['artists', 'album_name', 'popularity',
           'explicit', 'danceability', 'energy', 'key','loudness',  'mode',
           'speechiness', 'acousticness', 'instrumentalness', 'liveness',
           'valence', 'tempo','time_signature', 'track_genre','sentiment']

    km_features = ['artists', 'album_name','track_genre','sentiment']

    # Normalize the audio feature data
    scaler = StandardScaler()
    normalized_data = scaler.fit_transform(df_encode[audio_features])

    scaler = StandardScaler()
    km_data = scaler.fit_transform(df_encode[km_features])

    kmeans = KMeans(n_clusters=30, random_state=0, n_init="auto").fit_predict(km_data)

    normalized_data = pd.DataFrame(normalized_data)

    col_map = dict(zip(normalized_data.columns, audio_features))
    encode_df = normalized_data.rename(columns=col_map)
    df1 = pd.concat([pd.DataFrame(encode_df),pd.DataFrame(kmeans)],axis =1)
    df1 = pd.DataFrame(df1)
    df1.rename(columns={0: 'Cluster'}, inplace=True)
    df1 = pd.concat([df1,pd.DataFrame(df.track_name),pd.DataFrame(df.album_name).rename(columns ={'album_name': 'album_title'})],axis =1)
    
    def recommend_songs(name,alb_name,df2, no_of_recommendations):
        idx = df[(df['track_name'].str.lower() == name.lower()) & (df['album_name'].str.lower() == alb_name.lower())].index[0]
        score_series = pd.Series(df2.loc[idx]).sort_values(ascending=False)
        top_indexes = list(score_series.iloc[1:no_of_recommendations+1].index)
        artist_list = list(set(df.iloc[top_indexes]['artists']))
        return df.iloc[top_indexes],artist_list


    def content_based_recommend(songname):
        song = songname
        try:
            if df[df.track_name.str.lower()==song.lower()].shape[0]>1:
                display(df[df.track_name.str.lower()==song.lower()].iloc[:,:4])
                index_song = int(input())
                display(pd.DataFrame(df[df.track_name.str.lower()==song.lower()].iloc[index_song-1,:]).iloc[:3])
                s_name = df[df.track_name.str.lower()==song.lower()].iloc[index_song-1,:]['track_name']
                alb_name = df[df.track_name.str.lower()==song.lower()].iloc[index_song-1,:]['album_name']
            #     recommendations = recommend_songs(s_name,alb_name, no_of_recommendations=5)
            else:
                display(pd.DataFrame(df[df.track_name.str.lower()==song.lower()].iloc[0])[:3])
                s_name = str(df[df.track_name.str.lower()==song.lower()].iloc[0]['track_name'])
                alb_name = str(df[df.track_name.str.lower()==song.lower()].iloc[0]['album_name'])
            cluster_to_use = df1[(df1.track_name == s_name)&(df1.album_title == alb_name)].Cluster.iloc[0]
            all_songs_cluster = df1[df1.Cluster == cluster_to_use]

        except:
            print('The song is not available in our data!')
            return

        similarity_matrix = cosine_similarity(all_songs_cluster.iloc[:,:-3])
        df2 = pd.DataFrame(similarity_matrix)
        df2 = df2.set_index(all_songs_cluster.index).rename_axis('idx',axis=0)
        df2.columns = df2.set_index(df2.index).index
        recommendations,artist_list = recommend_songs(s_name, alb_name ,df2, no_of_recommendations=10)
        return pd.DataFrame(recommendations.iloc[:,:3])

        title = st.text_input('Which song is on your mind')
        if st.button("Similar songs"):
            output = content_based_recommend(title)
            st.write(output)
    
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
    unsafe_allow_html=True
    )
   

if __name__ == "__main__":
    main()


# In[63]:





# In[ ]:








# In[ ]:




