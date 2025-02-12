import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime

## sheet names
sheetname_usersinfo = "users_info"
sheetname_userdata = "user_data"

## low level func

csv_mode = False

def gsheet_connect():
    ## Connect only if not already connected
    if not csv_mode:
        if "conn" not in st.session_state:
            conn = st.connection("gsheets", type=GSheetsConnection)
            st.session_state.conn = conn

def read_sheet_df(sheet_name):
    gsheet_connect()
    if csv_mode:
        return pd.read_csv(sheet_name + '.csv')
    else:
        return st.session_state.conn.read(ttl=0, worksheet=sheet_name)

def overwrite_sheet_df(df, sheet_name):
    gsheet_connect()
    if csv_mode:
        df.to_csv(sheet_name + '.csv', index=False)
    else:
        st.session_state.conn.update(data=df, worksheet=sheet_name)

def append_sheet_df(df_append, sheet_name):
    gsheet_connect()
    df = read_sheet_df(sheet_name)
    df_new = pd.concat([df, df_append], ignore_index=True)
    overwrite_sheet_df(df_new, sheet_name)

## user functions

def register_new_user(name, email, password):
    if does_email_exist(email):
        return None
        
    df = read_sheet_df(sheetname_usersinfo)
    ## df is pandas dataframe with columns: userid, name, email, password

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

def get_userid_login_password(email, password):
    df = read_sheet_df(sheetname_usersinfo)
    ## df is pandas dataframe with columns: userid, name, email, password

    user_row = df[(df["email"] == email) & (df["password"] == password)]
    if not user_row.empty:
        return user_row.iloc[0]["userid"]
    return None

def does_email_exist(email):
    df = read_sheet_df(sheetname_usersinfo)
    
    ## Check if email already exists in df
    return not df[df["email"] == email].empty

def get_name_for_userid(userid):
    df = read_sheet_df(sheetname_usersinfo)

    row = df[df["userid"] == userid]
    if row.empty:
        st.write("Userid not found" + userid)
    else:
        return row.iloc[0]["name"]
    
    

## user data functions

# columns to use userid, timestamp, state

def store_user_data(userid, state):
    new_userdata_df = pd.DataFrame({
        "userid": [userid],
        "timestamp": [datetime.datetime.now()],
        "state": [state],
    })
    append_sheet_df(new_userdata_df, sheetname_userdata)


def read_latest_user_data(userid):
    df = read_sheet_df(sheetname_userdata)

    if df.empty:
        return None

    user_data = df[df["userid"] == userid]
    
    if user_data.empty:
        return None

    user_data_sorted = user_data.sort_values(by="timestamp", ascending=False)
    
    return user_data_sorted.iloc[0]["state"]    
