from daily_weather import daily_weather
import streamlit as st
import os, sys
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
opts = FirefoxOptions()
opts.add_argument("--headless")
import matplotlib.pyplot as plt
import pandas as pd
from bs4 import BeautifulSoup
import time
import matplotlib.dates as mdates
from streamlit import caching
st.set_page_config(layout="wide")

def home_page():
  st.markdown("""# Welcome to this App
  This is a web app under alpha testing regarding Hong Kong weather.
  """)

@st.cache
def installff():
  os.system('sbase install geckodriver')
  os.system('ln -s /home/appuser/venv/lib/python3.7/site-packages/seleniumbase/drivers/geckodriver /home/appuser/venv/bin/geckodriver')

_ = installff()
to_func = {
  "Home": home_page,
  "Daily Weather": daily_weather,
  
}

st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 500px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 500px;
        margin-left: -500px;
    }
    </style>
    """,
    unsafe_allow_html=True,)


_ = installff()
with st.sidebar:
  demo_name = st.selectbox("Applications", to_func.keys())
to_func[demo_name]()
