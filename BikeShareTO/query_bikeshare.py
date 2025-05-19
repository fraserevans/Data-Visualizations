import requests
import os
import time
import pandas as pd

# URL for real-time station status
url = "https://tor.publicbikesystem.net/ube/gbfs/v1/en/station_status"
response = requests.get(url)
data = response.json()
stations = data["data"]["stations"]

# Add timestamp to each station
current_time = int(time.time())
#for station in stations:
#    station["last_queried"] = current_time

# Define file paths
os.makedirs("BikeShareTO/station_status", exist_ok=True)
log_file = "BikeShareTO/station_status/station_status_log.csv"
recent_file = "BikeShareTO/station_status/station_status_recent.csv"

# Convert to DataFrame
df = pd.DataFrame(stations)

# Drop unwanted columns
drop_cols = ["is_charging_station", "is_installed", "status", 'is_returning', 'traffic', 'is_renting']
df = df.drop(columns=[col for col in drop_cols if col in df.columns])

# Load existing log if it exists
if os.path.exists(log_file):
    old_df = pd.read_csv(log_file)
    df = pd.concat([old_df, df], ignore_index=True)

# Remove duplicates based on station_id and last_reported
df = df.drop_duplicates(subset=["station_id", "last_reported"])

# Remove rows older than 1 month (30 days)
one_month_ago = current_time - 14 * 24 * 3600
df = df[df["last_reported"] >= one_month_ago]

# Save full cleaned log
df.to_csv(log_file, index=False)

# Save recent (last 24 hours) data
one_day_ago = current_time - 24 * 3600
recent_df = df[df["last_reported"] >= one_day_ago]
recent_df.to_csv(recent_file, index=False)
