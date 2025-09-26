#!/usr/bin/env python
# coding: utf-8

# In[13]:


import numpy as np
import pandas as pd
from pandas import json_normalize
from os import path
import requests
import pandas as pd
from io import BytesIO
import streamlit as st
DATA_DIR = '/users/harrisonkreiling/desktop/python/college-football-info'
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


# In[14]:


week = 5


# In[15]:


df = pd.read_csv(path.join(DATA_DIR, f'full_dataframe_asof_week_{week}.csv'))


# In[17]:
st.title("College Football")
week = st.sidebar.selectbox("Select Week", sorted(df["week"].unique()))
week_view = df.loc[
    (df["week"] == week) & (df['homeAway'] == 'home'),
    [
        "opponent", "team", "impliedSpreadPregame", "impliedOverUnderPregame"
    ]
].copy()
week_view = week_view.rename(columns={'team': 'Home', 'opponent': 'Away'})
week_view['impliedSpreadPregame'] = ((week_view['impliedSpreadPregame'] * 2).round(0) / 2)
def format_spread(row):
    spread = row["impliedSpreadPregame"]
    if abs(spread) < 1:
        return "PK"
    if spread < 0:
        # Home team is favored, keep the spread as-is
        return f"{row['Home']} {spread:+}"
    else:
        # Away team is favored, flip sign
        return f"{row['Away']} {-spread:+}"

week_view["Spread"] = week_view.apply(format_spread, axis=1)
week_view['O/U'] = (week_view['impliedOverUnderPregame'] * 2).round(0) / 2
week_view.drop(columns=['impliedSpreadPregame', 'impliedOverUnderPregame'], inplace=True)
st.subheader(f"Week {week} Matchups")
st.dataframe(week_view[["Away", "Home", "Spread", "O/U"]].reset_index(drop=True))

# === Resume Table Function ===
def build_resume_table(df):
    df = df[df["teamClass"] == "fbs"].copy()
    agg_dict = {
        "conference": "last", "currTeamRating": "last", "currOffRating": "last", "currDefRating": "last", "seasonTeamRating": "last",
        "W": "sum", "L": "sum", "xW": "sum", "xL": "sum", "confW": "sum", "confL": "sum", "SOS": "sum", 
        "rateSOR": "last", "teamRatingSeasonDelta": "last"}
    resume_table = df.groupby("team").agg(agg_dict).rename(columns={"currTeamRating": "teamRating",
              "currOffRating": "offRating", "currDefRating": "defRating", "rateSOR": "SOR"}).reset_index() 
    resume_table["teamRatingRank"] = resume_table["teamRating"].rank(ascending=False, method="min").astype(int)
    resume_table["offRatingRank"] = resume_table["offRating"].rank(ascending=False, method="min").astype(int)
    resume_table["defRatingRank"] = resume_table["defRating"].rank(ascending=False, method="min").astype(int)
    resume_table["seasonRatingRank"] = resume_table["seasonTeamRating"].rank(ascending=False, method="min").astype(int)
    resume_table["SOSRank"] = resume_table["SOS"].rank(ascending=False, method="min").astype(int)
    resume_table["SORRank"] = resume_table["SOR"].rank(ascending=False, method="min").astype(int)
    resume_table = resume_table[["team", "conference","W", "L", "xW", "xL",
            "confW", "confL", "teamRating", "teamRatingRank",
            "offRating", "offRatingRank", "defRating", "defRatingRank", "seasonTeamRating", "seasonRatingRank", "SOS", "SOSRank", "SOR", "SORRank",
            "teamRatingSeasonDelta"]]
    resume_table = resume_table.sort_values(by=["teamRatingRank"], ascending=True).reset_index(drop=True)
    return resume_table

# === Add Resume Table Section ===
st.subheader("Team Power Ratings")

resume_table = build_resume_table(df)

# Add a conference filter
conference_filter = st.selectbox("Filter by Conference", ["All"] + sorted(resume_table["conference"].unique()))
if conference_filter != "All":
    st.dataframe(resume_table[resume_table["conference"] == conference_filter].reset_index(drop=True))
else:
    st.dataframe(resume_table.reset_index(drop=True))

