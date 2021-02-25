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
from datetime import datetime, timedelta
from src.db_fns import create_engine2, sql_db_to_df

#%% Funciton for site
def main():
    
    # Get main df
    log_df = load_log_df()
    
    # User has a choice of several pages
    page = st.sidebar.selectbox('Choose a page:', 
                                ['Details by Day', 'Daily View', 'Errors', 'Full Data'])
    
    # User can choose a specific project
    projects = list(set(log_df['Project']))
    projects.insert(0,"All")
    project = st.sidebar.selectbox('Choose a project:', projects)
    # Filter df accordingly
    log_df_filt = log_df.copy()
    if project != 'All':
        log_df_filt = log_df_filt[log_df_filt['Project'] == project]
    
    # User can choose a specific project
    processes = list(set(log_df_filt['Process']))
    processes.insert(0,"All")
    process = st.sidebar.selectbox('Choose a process:', processes)
    # Filter df accordingly
    if process != 'All':
        log_df_filt = log_df_filt[log_df_filt['Process'] == process]
    
    # User can select a date range
    max_date = max(log_df['Event Date'])
    min_date = max_date - timedelta(30)
    date_range = st.sidebar.date_input('Choose a date range:', value=[min_date,max_date])
    
    # If user changes dates, wait until they have selected both a start and end
    if len(date_range) != 2:
        st.stop()
    
    # Filter by date range
    log_df_filt = log_df_filt[log_df_filt['Event Date'] >= date_range[0]]
    log_df_filt = log_df_filt[log_df_filt['Event Date'] <= date_range[1]]
    
    
    # Page chosed changes output
    if page == 'Details by Day':
        
        # Summarise data by date and details and plot
        log_df_sum = log_df_filt.groupby(['Event Date', 'Details'])['Events'].count().reset_index()
        
        fig1 = px.bar(log_df_sum, x='Event Date', y='Events', 
                 color='Details', title='Daily Events')
        st.write(fig1)
        # Also show user df
        st.dataframe(log_df_sum)
        
    elif page == 'Daily View':
        
        # Get list of dates given project/process filter
        date_list = list(set(log_df_filt['Event Date']))
        date_list.sort()
        chosen_date = st.selectbox('Choose a date:', date_list)
        
        # Filter by date
        log_df_filt = log_df_filt.copy()
        log_df_filt = log_df_filt[log_df_filt['Event Date'] == chosen_date]
        
        # Plot day data
        fig2 = px.scatter(log_df_filt, x='Event_Timestamp', y='Details', 
                 color='Details', title='Events in a Day')
        st.write(fig2)
        # Also show user df
        st.dataframe(log_df_filt)
        
    elif page == 'Errors':
        
        # Filter to just errors
        log_errors = log_df_filt.copy()
        log_errors = log_errors[log_errors['Details'] == 'Error']
        
        # Plot day data
        fig3 = px.scatter(log_errors, x='Event_Timestamp', y='Process', 
                 color='Project', title='Events in a Day')
        st.write(fig3)
        # Also show user df
        st.dataframe(log_errors) 
        
    elif page == 'Full Data':
        # Show full data
        st.dataframe(log_df) 
    
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