from numpy import dsplit
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
from datetime import datetime
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
opts = FirefoxOptions()
opts.add_argument("--headless")
driver = webdriver.Firefox(options=opts)
from datetime import time as tm
from st_aggrid import AgGrid
import plotly.express as px


@st.experimental_singleton
def hko_daily_table(url):
    driver.get(url)
    time.sleep(2)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    mainc = soup.find(id='mainContent')
    rows = mainc.find_all('tr')
    data=[]
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele]) # Get rid of empty values
    
    return data

year = datetime.now().year
month = datetime.now().month

def daily_weather():
  with st.sidebar:
    st.markdown("---")
    st.title("Daily Weather Summary")
    st.markdown("---")
  
    a1, a2, a3 = st.columns(3)
    with a1:
      ds = st.date_input("Start Date")
    with a2:
      de = st.date_input("End Date")
      st.markdown("---")
    st.write("Loading Progress:")
    p_bar = st.sidebar.progress(0)

  all_col = ["Day", "Mean Pressure (hPa)", "Absolute Daily Max (deg. C)", "Mean (deg. C)", "Absolute Daily Min (deg. C)", "Mean Dew Point (deg. C)", "Mean Relative Humidity (%)", "Mean Amount", "Total Rainfall (mm)", "Total Bright Sunshine (hours)", "Prevailing Wind Direction (degrees)", "Mean Wind Speed (km/h)"] 
  dfc=pd.DataFrame(columns=all_col)
  ind=pd.date_range(ds, de+ pd.DateOffset(months=1), freq='1M', closed="right") #replace closed by (inclusive="both") when using pandas 1.4.0 or later


  
  #st.write(ind)
  j=0

  for i in ind:
    year = i.year
    month = i.month
    out = hko_daily_table("https://www.hko.gov.hk/en/cis/dailyExtract.htm?y=%04d&m=%02d"%(year, month))
    df=pd.DataFrame(out[3:])
    df.columns=all_col[0:df.shape[1]]

    df['year']=year
    df['month']=month
    
    df=df.loc[pd.to_numeric(df['Day'], errors='coerce').notnull()]
    df['Date']=pd.to_datetime(df[['year', 'month', 'Day']])
    df=df.set_index("Date")
    df=df.drop(columns=['year', 'month', 'Day'])
    dfc = pd.concat([dfc, df])
    st.sidebar.success("%04d-%02d data retrieved."%(year, month))
    j+=1
    progress=j/ind.shape[0]
    p_bar.progress(progress)

  dfc["Day"]=dfc.index.strftime('%Y-%m-%d')
  dfc=dfc[ds:de]
  dfc = dfc.rename({"Day": "Record Date"}, axis='columns')
  #chartdata=df[df.applymap(isnumber)]
  chartdata=dfc 
  fig = px.line(chartdata.iloc[:,1:])
  fig.update_layout(autotypenumbers='convert types', width=1200, height=600)
  st.plotly_chart(fig)

  st.write("Data")
  AgGrid(chartdata, height=300,fit_columns_on_grid_load=True)
  st.write("Data Source: https://www.hko.gov.hk/en/cis/dailyExtract.htm")

def isnumber(x):
    try:
        float(x)
        return True
    except:
        return False

