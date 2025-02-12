import streamlit as st
import pandas as pd
import database as db_lib
import time
import pickle
import base64

def show_users_login():
    if not is_user_logged_in():

        st.write("")
        st.write("")

        email = st.text_input("Email", key="email")
        password = st.text_input("Password", type="password", key="password")
        if st.button("Login"):
            userid = db_lib.get_userid_login_password(email, password)
            if userid is None:
                st.write("Email or Password incorrect, please try again")
            else:
                do_user_login(userid)
                st.write("You are logged in, " + get_logged_in_user_name())
                restore_session_state()                
                time.sleep(1)
                st.rerun()

        st.divider()
        st.header("New user?")
        new_name = st.text_input("Name", key="new_name")
        new_email = st.text_input("Email", key="new_email")
        new_password = st.text_input("Password", type="password", key="new_password")
        if st.button("Register"):
            if db_lib.does_email_exist(new_email):
                st.write("Sorry, email already exists")
            else:
                new_userid = db_lib.register_new_user(new_name, new_email, new_password)
                if new_userid is None:
                    st.write("Sorry, email already exists")
                else:
                    do_user_login(new_userid)
                    st.write("You are registered, " + get_logged_in_user_name())
                    time.sleep(1)
                    st.rerun()


def is_user_logged_in():
    # st.session_state["logged_in_userid"] = 2
    # st.session_state["logged_in_user_name"] = "Saanvi"
    return ("logged_in_userid" in st.session_state)

def do_user_login(userid):
    st.session_state["logged_in_userid"] = userid
    st.session_state["logged_in_user_name"] = db_lib.get_name_for_userid(userid)

def get_logged_in_userid():
    return st.session_state["logged_in_userid"]


def get_logged_in_user_name():
    return st.session_state["logged_in_user_name"]


def do_user_logout(sidebar=False):
    if sidebar:
        st.sidebar.write("Logging you out, see you soon, " + get_logged_in_user_name())
    else:
        st.write("Logging you out, see you soon, " + get_logged_in_user_name())
    save_session_state()
    del st.session_state["logged_in_userid"]
    del st.session_state["logged_in_user_name"]
    time.sleep(1)

    # clean up session_state
    for key in st.session_state.keys():
        del st.session_state[key]

    st.rerun()

def show_logout_button(sidebar=False):
    if sidebar:
        if st.sidebar.button("Logout"):
            do_user_logout(sidebar)
    else:
        if st.button("Logout"):
            do_user_logout(sidebar)
        
            
def save_session_state():
    state_to_save = dict(st.session_state)
    state_to_save.pop("conn", None)
    binary_data = pickle.dumps(state_to_save)
    encoded_data = base64.b64encode(binary_data).decode('utf-8')
    db_lib.store_user_data(get_logged_in_userid(), encoded_data)


def restore_session_state():
    encoded_data = db_lib.read_latest_user_data(get_logged_in_userid())
    if encoded_data is None:
        return
    
    binary_data = base64.b64decode(encoded_data.encode('utf-8'))
    state_dict = pickle.loads(binary_data)
    #st.write("Read session_state")
    #st.write(state_dict)
    
    # clean up session_state
    for key in st.session_state.keys():
        if key != "conn":
            del st.session_state[key]

    # load session_state
    for key, value in state_dict.items():
        if key != "conn":
            st.session_state[key] = value

