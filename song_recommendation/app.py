import streamlit as st
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import plotly.express as px
import streamlit.components.v1 as components

st.set_page_config(
            page_title="Song Recommendation", 
            layout="wide",
            initial_sidebar_state="auto"
            )



@st.cache(allow_output_mutation=True)
def load_data():
    df = pd.read_csv("data/SpotifyFeatures.csv")
    return df


exploded_track_df = load_data()
Song_names = exploded_track_df.track_name.unique()
genre_names = exploded_track_df.genre.unique()
audio_feats = ["acousticness", "danceability", "energy", "instrumentalness","liveness","loudness","speechiness", "valence", "tempo"]

def n_neighbors_uri_audio(genre, test_feat):
    # genre = genre.lower()
    genre_data = exploded_track_df[(exploded_track_df["genre"]==genre)]
    # & (exploded_track_df["release_year"]>=start_year) & (exploded_track_df["release_year"]<=end_year)]
    genre_data = genre_data.sort_values(by='popularity', ascending=False)[:500]

    neigh = NearestNeighbors()
    neigh.fit(genre_data[audio_feats].to_numpy())

    n_neighbors = neigh.kneighbors([test_feat], n_neighbors=len(genre_data), return_distance=False)[0]

    uris = genre_data.iloc[n_neighbors]["track_id"].tolist()
    audios = genre_data.iloc[n_neighbors][audio_feats].to_numpy()
    return uris, audios

def main():
        st.sidebar.title('Interactive Visualizer')
        st.sidebar.markdown("Select filters for customization.")

if __name__ == '__main__':
    main()


def page():
    title = "Song Recommendation Engine"
    st.title(title)

    st.write("First of all, welcome! This is the place where you can customize what you want to listen to based on songs, genre and several key audio features. Try playing around with different settings and listen to the songs recommended by our system!")
    st.markdown("##")

    st.sidebar.markdown("***Choose your genre:***")
    genre = st.sidebar.selectbox(
                "A", 
                genre_names,label_visibility= 'hidden', index=0)
        # st.markdown("***Choose Songs you like:***")
        # Song_select = st.multiselect(
        #     "",
        #     Song_names,Song_names[3] 
        # )
    st.sidebar.markdown("***Choose features to customize:***")
    # start_year, end_year = st.slider(
    #             'Select the year range',
    #             1990, 2019, (2015, 2019)
    #         )
    acousticness = st.sidebar.slider(
                'Acousticness',
                0.0, max(exploded_track_df.acousticness), max(exploded_track_df.acousticness)/2)
    danceability = st.sidebar.slider(
                'Danceability',
                0.0, max(exploded_track_df.danceability), max(exploded_track_df.danceability)/2)
    energy = st.sidebar.slider(
                'Energy',
                0.0, max(exploded_track_df.energy), max(exploded_track_df.energy)/2)
    instrumentalness = st.sidebar.slider(
                'Instrumentalness',
                0.0, max(exploded_track_df.instrumentalness), max(exploded_track_df.instrumentalness)/2)
    valence = st.sidebar.slider(
                'Valence',
                0.0, max(exploded_track_df.valence), max(exploded_track_df.valence)/2)
    tempo = st.sidebar.slider(
                'Tempo',
                0.0, max(exploded_track_df.tempo), max(exploded_track_df.tempo)/2)
    liveness = st.sidebar.slider(
                'Liveness',
                0.0, max(exploded_track_df.liveness), max(exploded_track_df.liveness)/2)
    loudness = st.sidebar.slider(
                'Loudness',
                0.0, max(exploded_track_df.loudness), max(exploded_track_df.loudness)/2)
    speechiness = st.sidebar.slider(
                'Speechiness',
                0.0, max(exploded_track_df.speechiness), max(exploded_track_df.speechiness)/2)

    tracks_per_page = 6
    test_feat = [acousticness, danceability, energy, instrumentalness, liveness, loudness, speechiness,valence, tempo]
    uris, audios = n_neighbors_uri_audio(genre, test_feat)

    tracks = []
    for uri in uris:
        track = """<iframe src="https://open.spotify.com/embed/track/{}" width="260" height="380" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>""".format(uri)
        tracks.append(track)

    if 'previous_inputs' not in st.session_state:
        st.session_state['previous_inputs'] = [genre] + test_feat
    
    current_inputs = [genre] + test_feat
    if current_inputs != st.session_state['previous_inputs']:
        if 'start_track_i' in st.session_state:
            st.session_state['start_track_i'] = 0
        st.session_state['previous_inputs'] = current_inputs

    if 'start_track_i' not in st.session_state:
        st.session_state['start_track_i'] = 0
    
    with st.container():
        col1, col3 = st.columns([2,2])
        if st.button("Recommend More Songs"):
            if st.session_state['start_track_i'] < len(tracks):
                st.session_state['start_track_i'] += tracks_per_page

        current_tracks = tracks[st.session_state['start_track_i']: st.session_state['start_track_i'] + tracks_per_page]
        current_audios = audios[st.session_state['start_track_i']: st.session_state['start_track_i'] + tracks_per_page]
        if st.session_state['start_track_i'] < len(tracks):
            for i, (track, audio) in enumerate(zip(current_tracks, current_audios)):
                if i%2==0:
                    with col1:
                        components.html(
                            track,
                            height=400,
                        )
                        with st.expander("See more details"):
                            df = pd.DataFrame(dict(
                            r=audio[:5],
                            theta=audio_feats[:5]))
                            fig = px.line_polar(df, r='r', theta='theta', line_close=True)
                            fig.update_layout(height=400, width=340)
                            st.plotly_chart(fig)
            
                else:
                    with col3:
                        components.html(
                            track,
                            height=400,
                        )
                        with st.expander("See more details"):
                            df = pd.DataFrame(dict(
                                r=audio[:5],
                                theta=audio_feats[:5]))
                            fig = px.line_polar(df, r='r', theta='theta', line_close=True)
                            fig.update_layout(height=400, width=340)
                            st.plotly_chart(fig)

        else:
            st.write("No songs left to recommend")

page()

