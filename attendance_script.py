import pandas as pd
import requests
from bs4 import BeautifulSoup
import plotly.express as px
from datetime import datetime
import schedule
import time

# --- Step 1: Load CSV Data ---
def load_csv_data(csv_path):
    # Load the attendance data
    data = pd.read_csv(csv_path)
    data['Timestamp'] = pd.to_datetime(data['Timestamp'])
    
    # Aggregate attendance by workshop (group by date or inferred workshop number)
    data['Date'] = data['Timestamp'].dt.date
    workshop_attendance = data.groupby('Date').size().reset_index(name='Attendance')
    return workshop_attendance

# --- Step 2: Scrape Website Data ---
def scrape_workshop_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    workshops = []
    
    # Extract events
    events = soup.find_all('div', class_='event-card')
    for event in events:
        title = event.find('h3', class_='event-title').text.strip()
        date = event.find('p', class_='event-date').text.strip()
        attendance = event.find('span', class_='event-attendance').text.strip()  # Assuming this exists
        
        # Filter workshops
        if "Advanced Workshop" not in title:
            if "Fall Kickoff" in title or "Workshop" in title:
                workshops.append({
                    'Title': title,
                    'Date': datetime.strptime(date, '%B %d, %Y').date(),
                    'Attendance': int(attendance) if attendance.isdigit() else None
                })
    
    return pd.DataFrame(workshops)

# --- Step 3: Merge Data ---
def merge_data(csv_data, web_data):
    # Combine CSV and web-scraped data
    combined_data = pd.concat([csv_data, web_data[['Date', 'Attendance']]], ignore_index=True)
    combined_data.sort_values(by='Date', inplace=True)
    return combined_data

# --- Step 4: Create Interactive Graph ---
def create_graph(data, title="Workshop Attendance Over Time"):
    fig = px.line(
        data, x='Date', y='Attendance', color='Source',
        title=title, markers=True,
        labels={'Date': 'Workshop Date', 'Attendance': 'Attendance Count'}
    )
    fig.show()

# --- Step 5: Automate Updates ---
def update_data_and_visualize(csv_path, url):
    csv_data = load_csv_data(csv_path)
    csv_data['Source'] = 'CSV'
    
    web_data = scrape_workshop_data(url)
    web_data['Source'] = 'Website'
    
    combined_data = merge_data(csv_data, web_data)
    create_graph(combined_data)

# Schedule the script to run every day at 8:00 AM
def schedule_updates():
    schedule.every().day.at("08:00").do(update_data_and_visualize, 
                                        csv_path="AI Club Attendance SS24.csv", 
                                        url="https://www.msuaiclub.com/events")

    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute for scheduled tasks

# --- Run the Script ---
if __name__ == "__main__":
    csv_path = "AI Club Attendance SS24.csv"
    url = "https://www.msuaiclub.com/events"
    
    # Initial Run
    update_data_and_visualize(csv_path, url)
    
    # Schedule Future Updates
    schedule_updates()