import json
import requests
import datetime


class InsightAPIClient:
    def __init__(self, access_token):
        self.base_url = "https://graph.facebook.com/v19.0"
        self.access_token = access_token

    def get_campaign_insights(self, campaign_id, start_date, end_date):

        try:

            # Format dates
            start_date_formatted = start_date.strftime("%Y-%m-%d")
            end_date_formatted = end_date.strftime("%Y-%m-%d")

            # Define the fields to retrieve
            fields = [
                "conversions",
                "cost_per_conversion",
                "cpm",
                "impressions",
                "created_time",
                "spend",
                "reach",
                "updated_time",
            ]

            # Construct the URL
            url = f"{self.base_url}/{campaign_id}/insights"
            params = {
                "access_token": self.access_token,
                "time_range": json.dumps(
                    {"since": start_date_formatted, "until": end_date_formatted}
                ),
                "fields": ",".join(fields),
            }

            # Make the request
            response = requests.get(url, params=params)

            # Check if the request was successful
            if response.status_code == 200:
                if response.json()["data"]:
                    return response.json()["data"][0]
                else:
                    return None
            else:
                raise Exception(f"Failed to retrieve insights: {response.text}")

        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def getCampaignStartDate(self, campaign_id):
        try:
            # Define the fields to retrieve
            fields = [
                "created_time",
            ]

            # Construct the URL
            url = f"{self.base_url}/{campaign_id}/insights"
            params = {
                "access_token": self.access_token,
                "fields": ",".join(fields),
            }
            # Make the request
            response = requests.get(url, params=params)

            # Check if the request was successful
            if response.status_code == 200:

                if (
                    response.json().get("data")
                    and len(response.json()["data"]) > 0
                    and "created_time" in response.json()["data"][0]
                ):
                    return response.json()["data"][0]
                else:
                    print(f"No data found for campaign: {campaign_id}")
                    return None
            else:
                raise Exception(f"Failed to retrieve insights: {response.text}")

        except Exception as e:
            print(f"An error occurred: {str(e)}")


def getInsight(client: InsightAPIClient, campaign_id, start_date, end_date):
    return client.get_campaign_insights(
        campaign_id, start_date, end_date - datetime.timedelta(days=1)
    )
