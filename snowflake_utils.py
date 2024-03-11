import os
import logging
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PWD = os.getenv("SNOWFLAKE_PWD")
SNOWFLAKE_ACC = os.getenv("SNOWFLAKE_ACC")

def connect_to_snowflake():

    try:

        ctx = snowflake.connector.connect(
            user=SNOWFLAKE_USER,
            password=SNOWFLAKE_PWD,
            account=SNOWFLAKE_ACC
        )

        return ctx
  
    except Exception as e:
        logging.exception(f"snowflake error, connection exception {e}")


def read_playlists():

    try:
        ctx = connect_to_snowflake()
        
        cs = ctx.cursor()
        cs.execute(
            f"""SELECT
                "DBT_MODELS"."FOLLOWER_METRICS"."PLAYLIST_ID" AS "PLAYLIST_ID",
                DATE_TRUNC("day", "DBT_MODELS"."FOLLOWER_METRICS"."DATE") AS "DATE",
                SUM("DBT_MODELS"."FOLLOWER_METRICS"."FOLLOWERS") AS "sum"
                FROM
                "AMPLIGO_INTERNAL"."DBT_MODELS"."FOLLOWER_METRICS"
                GROUP BY
                "DBT_MODELS"."FOLLOWER_METRICS"."PLAYLIST_ID",
                DATE_TRUNC("day", "DBT_MODELS"."FOLLOWER_METRICS"."DATE")
                ORDER BY
                "DBT_MODELS"."FOLLOWER_METRICS"."PLAYLIST_ID" ASC,
                DATE_TRUNC("day", "DBT_MODELS"."FOLLOWER_METRICS"."DATE") ASC"""
        )
        data = cs.fetchall()

        return data
    
    except Exception as e:
        logging.exception(f"snowflake error, read playlists exception {e}")
