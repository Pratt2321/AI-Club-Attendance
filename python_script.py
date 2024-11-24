import pandas as pd
import requests
from bs4 import BeautifulSoup
import plotly.express as px
from datetime import datetime
import schedule
import time

def load_csv_data(csv_path):
    # Load the attendance data
    data = pd.read_csv(csv_path)
    data['Timestamp'] = pd.to_datetime(data['Timestamp'])
    
    # Aggregate attendance by workshop (group by date or inferred workshop number)
    data['Date'] = data['Timestamp'].dt.date
    workshop_attendance = data.groupby('Date').size().reset_index(name='Attendance')
    return workshop_attendance