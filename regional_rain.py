def out_max(txt):
    return [int(s) for s in txt.split() if s.isdigit()][-1]

def convert_df(df):
   return df.to_csv().encode('utf-8')

def region_rain():
    import time
    import sys
    from selenium import webdriver
    from selenium.webdriver import FirefoxOptions
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    driver = webdriver.Firefox(options=opts)
    from datetime import time as tm
    import pandas as pd
    import numpy as np
    import time
    from bs4 import BeautifulSoup
    from selenium.webdriver.support.ui import Select
    from selenium.webdriver.common.by import By
    from datetime import datetime
    from datetime import timedelta
    import plotly.express as px
    import streamlit as st
    default_time1 = tm(0,0)
    default_time2 = tm(23,59)
    
    with st.sidebar:
        st.markdown("---")
        st.title("Regional Rainfall Record")
        st.markdown("---")
        with st.form("form1"):
            a1, a2 = st.columns(2)
            with a1:
                Start_Date = st.date_input("Start Date")
                Start_Time = st.time_input('Start Time', default_time1)
            with a2:
                End_Date = st.date_input("End Date")
                End_Time = st.time_input('End Time', default_time1)
            st.form_submit_button("Submit")
        p_bar = st.sidebar.progress(0)
        status=st.empty()

    ds=datetime.combine(Start_Date,Start_Time)
    de=datetime.combine(End_Date,End_Time)

    if ds.minute > 45:
        ds=ds.replace(minute=45)
    elif ds.minute<45:
        ds=ds.replace(minute=45)
        ds = ds - timedelta(hours=1)
    
    if de.minute > 45:
        de=de.replace(minute=0)
        de = de + timedelta(hours=1)
    elif de.minute<=45:
        de=de.replace(minute=0)    

    date1=ds
    date2=de

    domain = pd.date_range(start=ds, end=de, freq='H')
    #domain=domain[:-2]
    #st.write(domain)


    district=["Central & Western District","Eastern District","Islands District","Kowloon City","Kwai Tsing","Kwun Tong","North District","Sai Kung","Sha Tin","Sham Shui Po","Southern District","Tai Po","Tsuen Wan","Tuen Mun","Wan Chai","Wong Tai Sin","Yau Tsim Mong","Yuen Long"]
    from_web=pd.DataFrame()

    out_plot=st.empty()
    out_table=st.empty()
        
    i=0
    for run in domain:
        d = f'{run.day:02d}'
        h = f'{run.hour:02d}'
        m = f'{run.month:02d}'
        y = f'{run.year:02d}'
        status.success("Currently reading: "+run.strftime("%Y%m%d-%H"))


        hourly_url = "https://www.hko.gov.hk/en/wxinfo/rainfall/rf_record.shtml"
        # initiating the webdriver. Parameter includes the path of the webdriver.
        #driver = webdriver.Chrome(r'C:\\chromedriver\\chromedriver.exe')
        driver.get(hourly_url)
        time.sleep(1)

        ddelement= Select(driver.find_element(By.ID, value='Selday'))
        ddelement.select_by_value(d)
        ddelement= Select(driver.find_element(By.ID, value='Selmonth'))
        ddelement.select_by_value(m)
        ddelement= Select(driver.find_element(By.ID, value='Selhour'))
        ddelement.select_by_value(h)
        driver.find_element(By.XPATH, "//input[@type='submit']").click()

        time.sleep(1)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        mainc = soup.find(id='rainfalldata')
        rows = mainc.find_all('tr')
        
        hourly=[]
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            hourly.append([ele for ele in cols if ele]) # Get rid of empty values
        

        hourly_df=pd.DataFrame(hourly[2:], columns=['Region', 'Rainfall'])
        hourly_df["Time from"]= run # - timedelta(minutes=15)
        hourly_df = hourly_df.set_index("Time from")
        from_web=pd.concat([from_web, hourly_df])
        if len(rows)<=1:
            status.success("(No recorded rainfall for "+run.strftime("%Y%m%d-%H"))

        district_max_h=pd.DataFrame(index=from_web.index.unique(), columns=district)
        i+=1
        progress=i/len(domain)
        p_bar.progress(progress)
    driver.close()

    for i in district:
        district_max_h[i]=from_web.loc[from_web["Region"]==i].loc[:, "Rainfall"]  

    status.success("All download completed")
    district_max_h=district_max_h.applymap(out_max, na_action='ignore')
    filename = "max hr regional rain "+date1.strftime("%m%d-%H")+" to "+date2.strftime("%m%d-%H")+".csv"

    new_date_range = pd.date_range(start=date1, end=date2, freq='H')
    district_max_h = pd.DataFrame(district_max_h.copy(), index=new_date_range)
    district_max_h.insert(0, 'Time to', district_max_h.index+timedelta(minutes=60))
    district_max_h.index.name = 'Time from'
    district_max_h=district_max_h.fillna(0)
    district_max_h.iloc[:, 1:]=district_max_h.iloc[:, 1:].astype('int')
    district_max_h.insert(1, 'Max District', district_max_h.iloc[:,2:].replace(0, np.nan).idxmax(axis=1))
    district_max_h.insert(1, 'Max Rainfall', district_max_h.iloc[:,3:].max(axis=1))
    
    chartdata=district_max_h 
    fig = px.line(chartdata.iloc[:,3:], labels={
                     "variable": "District",
                     "index": "Time",
                     "value": "Recorded Hourly Rainfall (mm)",
                 })
    fig.update_layout(autotypenumbers='convert types', width=1200, height=600)
    out_plot.plotly_chart(fig)
    out_table.write(district_max_h)
    csv = convert_df(district_max_h)
    st.download_button("Download CSV", csv, filename, "text/csv", key='download-csv')