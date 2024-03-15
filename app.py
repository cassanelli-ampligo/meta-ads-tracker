from snowflake_utils import read_playlists
import streamlit as st
import datetime
from collections import defaultdict
import json
from spotify_utils import get_playlist_details
from datetime import datetime, timedelta

from meta_api import InsightAPIClient, getInsight
import requests

from colorize import colorize

today = datetime.now()
yesterday = today - timedelta(days=1)

start_date = yesterday
end_date = today


st.set_page_config(layout="wide")
ACCESS_TOKEN = st.secrets["meta_access_token"]

st.title("Meta Ads Tracker")
st.divider()


client = InsightAPIClient(ACCESS_TOKEN)

data = read_playlists()

data = [item for item in data if item[1] is not None]

filters1, filters2 = st.columns([2, 1])

with filters1:

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("Yesterday"):
            start_date = yesterday
            end_date = today
    with col2:
        if st.button("2 days ago"):
            two_days_ago = datetime.now() - timedelta(days=2)
            start_date = two_days_ago
            end_date = yesterday
    with col3:
        if st.button("last week"):
            last_week = datetime.now() - timedelta(days=7)
            start_date = last_week
            end_date = today


response = requests.get(
    "https://ampligostoragenoprod.blob.core.windows.net/meta-ads-tracker/assets.json"
)
assets = response.json()

with filters2:
    col1, col2 = st.columns([3, 1])

    with col1:
        # Create a filter using a multidropdown
        selected_assets = st.multiselect(
            "Filter Assets", options=assets, format_func=lambda x: x["name"]
        )

    with col2:
        # Reset button
        if st.button("Reset"):
            selected_assets = []

if len(selected_assets) > 0:
    playlist_ids = [item["playlist_id"] for item in selected_assets]
else:
    playlist_ids = [item["playlist_id"] for item in assets]


data_required = [d for d in data if d[0] in playlist_ids]

playlist_data = defaultdict(list)
for playlist_id, date, followers in data_required:
    playlist_data[playlist_id].append((date, followers))

all_dates = [date for _, date, _ in data]
min_date = (
    min(all_dates) if all_dates else datetime.date.today() - datetime.timedelta(days=1)
)
max_date = max(all_dates) if all_dates else datetime.date.today()


col1, col2, col3 = st.columns(3)

with col1:
    start_date_picker = st.date_input(
        "Start date", max_value=yesterday, value=start_date
    )

with col2:
    end_date_picker = st.date_input("End date", max_value=today, value=end_date)


def calculate_diff(playlist_records, start_date, end_date):
    start_followers = None
    end_followers = None
    for record_date, followers in playlist_records:
        if record_date and start_date and record_date == start_date:
            start_followers = followers
        if record_date and end_date and record_date == end_date:
            end_followers = followers
    if start_followers is not None and end_followers is not None:
        return end_followers - start_followers
    return "N/A"  # Return "N/A" if no data found for either start or end date


tracked_playlists = []

for playlist_id, records in playlist_data.items():

    records = [record for record in records if record[0] is not None]
    this_record_dates = [record[0] for record in records]

    if (
        start_date_picker not in this_record_dates
        or end_date_picker not in this_record_dates
    ):
        continue

    additional_playlist_info = next(
        (item for item in assets if item["playlist_id"] == playlist_id), None
    )

    if additional_playlist_info.get("meta_id") is None:
        continue

    diff = calculate_diff(records, start_date_picker, end_date_picker)

    daily_spend = (
        int(int(additional_playlist_info["price"]) / 30)
        if additional_playlist_info.get("price") is not None
        else None
    )

    length_campaign = end_date_picker - start_date_picker
    cost_per_followers = round(daily_spend * length_campaign.days / diff, 3)

    insights = getInsight(
        client,
        additional_playlist_info["meta_id"],
        start_date_picker,
        end_date_picker,
    )
    if insights is None:
        continue

    date_start_campaign = datetime.strptime(insights["created_time"], "%Y-%m-%d").date()

    if date_start_campaign > start_date_picker:
        continue

    tracked_playlists.append({"Name": get_playlist_details(playlist_id)[0]})

    cost_per_spotify_contain = float(insights["cost_per_conversion"][0]["value"])
    spotify_contains = int(insights["conversions"][0]["value"])

    tracked_playlists[-1]["Daily Budget"] = f"€{daily_spend}"
    tracked_playlists[-1]["Amount Spent"] = f"€{round(float(insights['spend']), 3)}"

    tracked_playlists[-1]["Spotify Contain"] = spotify_contains
    tracked_playlists[-1]["Followers"] = diff

    tracked_playlists[-1][
        "Cost per Spotify Contain"
    ] = f"€{round(cost_per_spotify_contain, 3)}"
    tracked_playlists[-1]["CPF"] = f"€{cost_per_followers}"

    if diff != "N/A" and isinstance(diff, str):
        diff = int(diff)
    if isinstance(diff, int) and diff > 0:
        tracked_playlists[-1]["CPF - Real"] = round(float(insights["spend"]), 3) / diff
    else:
        tracked_playlists[-1]["CPF - Real"] = "N/A"

    tracked_playlists[-1]["Ratio"] = f"{int(diff/spotify_contains*100)}%"
    tracked_playlists[-1]["cpm"] = f"€{round(float(insights.get('cpm', 0)), 3)}"
    tracked_playlists[-1]["impressions"] = format(
        int(insights.get("impressions", 0)), ","
    )
    tracked_playlists[-1]["reach"] = format(int(insights.get("reach", 0)), ",")
    tracked_playlists[-1]["Date Start"] = insights.get("created_time", "N/A")
    tracked_playlists[-1]["Last Update"] = insights.get("updated_time", "N/A")

    tracked_playlists.sort(key=lambda x: x["Name"])


not_campaign_playlists = []

for playlist_id, records in playlist_data.items():

    if (
        start_date_picker not in this_record_dates
        or end_date_picker not in this_record_dates
    ):
        continue

    records = [record for record in records if record[0] is not None]
    this_record_dates = [record[0] for record in records]

    additional_playlist_info = next(
        (item for item in assets if item["playlist_id"] == playlist_id), None
    )

    if additional_playlist_info.get("meta_id") is not None:

        date_start_campaign = datetime.strptime(
            client.getCampaignStartDate(additional_playlist_info["meta_id"])[
                "created_time"
            ],
            "%Y-%m-%d",
        ).date()

        if date_start_campaign <= start_date_picker:
            continue

        insights = getInsight(
            client,
            additional_playlist_info["meta_id"],
            start_date_picker,
            end_date_picker,
        )

    diff = calculate_diff(records, start_date_picker, end_date_picker)

    daily_spend = (
        int(int(additional_playlist_info["price"]) / 30)
        if additional_playlist_info.get("price") is not None
        else None
    )

    length_campaign = end_date_picker - start_date_picker

    if isinstance(diff, int) and diff > 0:
        cost_per_followers = round(daily_spend * length_campaign.days / diff, 3)
    else:
        cost_per_followers = round(daily_spend * length_campaign.days, 3)

    not_campaign_playlists.append(
        {
            "Name": get_playlist_details(playlist_id)[0],
            "Start Date": start_date,
            "End Date": end_date,
            "Followers Difference": diff,
            "Daily Budget": f"€{daily_spend}",
            "CPF": f"€{cost_per_followers}",
        }
    )

    if additional_playlist_info.get("meta_id") is not None:
        not_campaign_playlists[-1]["Campaign Start"] = date_start_campaign
        not_campaign_playlists.sort(key=lambda x: x["Name"])


untracked_playlists = []

for playlist_id, records in playlist_data.items():

    records = [record for record in records if record[0] is not None]
    this_record_dates = [record[0] for record in records]
    # if playlist_id == "6v6DEX9zlblL3P58zpQJgP":
    #     print(records)

    if records:
        records.sort(key=lambda x: x[0])

        if (
            start_date_picker not in this_record_dates
            or end_date_picker not in this_record_dates
        ):
            untracked_playlists.append(
                {
                    "Name": get_playlist_details(playlist_id)[0],
                    "Start Date": start_date,
                    "End Date": end_date,
                }
            )
            untracked_playlists.sort(key=lambda x: x["Name"])


st.subheader("Tracked Playlists")
st.dataframe(colorize(tracked_playlists))

st.subheader("Not in Campaign Playlists")
st.table(not_campaign_playlists)

st.subheader("Un-Tracked Playlists")
st.table(untracked_playlists)
