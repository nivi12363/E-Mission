import streamlit as st
import pandas as pd
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import datetime

# Google Sheet URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1dRsURQhNhHzSDVS-280ef8YJDwQXA8-hR79GZfNGgwY"

# Sheet names
sheetname_usersinfo = "users_info"
sheetname_userdata = "user_data"

# Low-level functions

def gsheet_connect():
    """Connect to a public Google Sheet without authentication."""
    gc = gspread.service_account()  # Skip if not using authentication
    sh = gc.open_by_url(SHEET_URL)
    return sh

def read_sheet_df(sheet_name):
    """Read data from Google Sheets."""
    sh = gsheet_connect()
    worksheet = sh.worksheet(sheet_name)
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

def overwrite_sheet_df(df, sheet_name):
    """Overwrite data in Google Sheets."""
    sh = gsheet_connect()
    worksheet = sh.worksheet(sheet_name)
    worksheet.clear()
    set_with_dataframe(worksheet, df)

def append_sheet_df(df_append, sheet_name):
    """Append data to Google Sheets."""
    df = read_sheet_df(sheet_name)
    df_new = pd.concat([df, df_append], ignore_index=True)
    overwrite_sheet_df(df_new, sheet_name)

# User functions

def register_new_user(name, email, password):
    """Register a new user."""
    if does_email_exist(email):
        return None
        
    df = read_sheet_df(sheetname_usersinfo)
    max_userID = df["userid"].max() if not df.empty else 0
    new_userID = max_userID + 1
    new_user_df = pd.DataFrame({
        "userid": [new_userID],
        "name": [name],
        "email": [email],
        "password": [password]
    })
    
    append_sheet_df(new_user_df, sheetname_usersinfo)
    return new_userID

def does_email_exist(email):
    """Check if email already exists."""
    df = read_sheet_df(sheetname_usersinfo)
    return not df[df["email"] == email].empty

# User data functions

def store_user_data(userid, state):
    """Store user data."""
    new_userdata_df = pd.DataFrame({
        "userid": [userid],
        "timestamp": [datetime.datetime.now()],
        "state": [state],
    })
    append_sheet_df(new_userdata_df, sheetname_userdata)

def read_latest_user_data(userid):
    """Read latest user data."""
    df = read_sheet_df(sheetname_userdata)
    if df.empty:
        return None
    user_data = df[df["userid"] == userid]
    if user_data.empty:
        return None
    user_data_sorted = user_data.sort_values(by="timestamp", ascending=False)
    return user_data_sorted.iloc[0]["state"]
