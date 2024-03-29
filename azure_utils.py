import csv
import os
import json
import logging
from io import StringIO
from helpers.exceptions import CSVtoListDictConvertionException
import psycopg2
import streamlit as st


DB_NAME = st.secrets["db_name"]
DB_HOST = st.secrets["db_host"]
DB_USER = st.secrets["db_user"]
DB_PASSWORD = st.secrets["db_password"]


def get_assets() -> dict:

    # Define the connection parameters
    db_params = {
        "host": DB_HOST,
        "database": DB_NAME,
        "user": DB_USER,
        "password": DB_PASSWORD,
    }

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(**db_params)

    try:
        # Create a cursor
        cursor = conn.cursor()

        playlist_ids = []

        for this_playlist_id in row[1]:

            # Query the sentinel_tracks table
            cursor.execute(
                f"SELECT URL FROM placement.playlists WHERE playlist_id='{this_playlist_id}'"
            )

            # Fetch all rows from the result
            this_playlist_url = cursor.fetchone()

            # Extract the playlist ID from the URL (assuming the URL format is consistent)
            playlist_id = this_playlist_url[0].split("/")[-1].split("?")[0]

            # Create the data structure for the JSON
            playlist_ids.append(playlist_id)

        cursor.close()
        conn.close()

        return result
    except Exception as e:
        print("Error: ", e)
        return None
