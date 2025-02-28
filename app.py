import time
import pandas as pd
import streamlit as st
import requests
import subprocess
from telegram_utils import send_telegram_message

st.set_page_config(
    page_title="Server Monitoring",
    layout="wide",
)

# Previous telegram message to avoid spamming
previous_telegram_message = ""


def get_data_from_api():
    url = st.secrets["API_URL"]
    response = requests.get(url)
    data = response.json()
    return data


def get_server_status(IP):
    # Check whether the server is up or down
    status = 0
    try:
        subprocess.run(
            ["ping", "-n", "2", IP],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        status = 1
    except subprocess.CalledProcessError:
        status = 0

    return status


# Dashboard title
st.title("Server Monitoring Dashboard")

# Creating a single-element container
placeholder = st.empty()

# Near real-time / live feed simulation
while True:
    # Get the data from the API
    data = get_data_from_api()

    # Ping each server to check if it is online or offline
    for IP in data.keys():
        data[IP]["status"] = "Online" if get_server_status(IP) else "Offline"
        if data[IP]["status"] == "Offline":
            message = f"⚠️ Server {data[IP]['name']} (`{IP}`) is offline!"
            if message != previous_telegram_message:
                send_telegram_message(message)
                previous_telegram_message = message

    # Create a DataFrame from the data
    df = pd.DataFrame(data).T.reset_index()

    # Remove the IP column
    df.drop("ip", axis=1, inplace=True)

    # Rename index to IP
    df.rename(columns={"index": "IP"}, inplace=True)
    df.rename(columns={"name": "Name"}, inplace=True)
    df.rename(columns={"cpu_usage": "Cpu Usage"}, inplace=True)
    df.rename(columns={"ram_available": "RAM Available"}, inplace=True)
    df.rename(columns={"disk_free": "Disk Free"}, inplace=True)
    df.rename(columns={"status": "Status"}, inplace=True)

    # Restructure the DataFrame
    df = df[["IP", "Name", "Cpu Usage", "RAM Available", "Disk Free", "Status"]]

    df_offline = df[df["Status"] == "Offline"]

    # Reset the index
    df_offline.reset_index(drop=True, inplace=True)

    # Only display IP, Name, and Status columns
    df_offline = df_offline[["IP", "Name", "Status"]]

    df_online = df[df["Status"] == "Online"]
    # Reset the index
    df_online.reset_index(drop=True, inplace=True)

    with placeholder.container():
        # Display the offline servers
        st.markdown("### ⚠️ Offline Servers")
        # Create 2 columns for offline servers
        col1, col2 = st.columns([1, 3])
        with col1:
            st.table(df_offline)

        st.write("---")

        # Display the online servers
        st.markdown("### ✅ Online Servers")
        st.table(df_online)

        time.sleep(3)
