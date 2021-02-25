'''
    File name: app.py
    Author: Henry Letton
    Date created: 2021-02-25
    Python Version: 3.8.3
    Desciption: Central script for dashboard
'''

#%% Import required modules and functions
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from src.db_fns import create_engine2, sql_db_to_df

#%% Funciton for site
def main():
    
    # Get main df
    log_df = load_log_df()
    # Basic groupby of data
    log_df_sum = log_df.groupby(['Event Date', 'Details'])['Events'].count().reset_index()
    
    # Show both dfs
    st.dataframe(log_df)
    st.dataframe(log_df_sum)
    
    # Output summary as interactive df
    fig = px.bar(log_df_sum, x="Event Date", y="Events", color="Details", title="Daily")
    st.write(fig)
    
    return


#%% Load full event log from database
@st.cache(allow_output_mutation=True)
def load_log_df():
    engine = create_engine2()
    df = sql_db_to_df(engine, 'Event_Log')
    # Fix and feature engineer
    df['Details'][df['Details'] == 'end']= 'End'
    df['Event Date'] = df['Event_Timestamp'].dt.date
    df['Events'] = 1
    return df

#%% Run main function
if __name__ == '__main__':
    main()