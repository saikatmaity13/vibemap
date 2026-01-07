from pymongo import MongoClient
import osmnx as ox
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to Atlas
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.vibemap_db
collection = db.places

CITY = "Bangalore, India"
TAGS = {
    'amenity': ['cafe', 'restaurant', 'library', 'place_of_worship'],
    'leisure': ['park', 'garden']
}

print(f"🚀 Seeding database for {CITY}...")

# 1. Get Data from OSM
gdf = ox.features_from_place(CITY, tags=TAGS)

count = 0
for index, row in gdf.iterrows():
    if 'name' in row and pd.notna(row['name']):
        # Get location
        if row.geometry.geom_type == 'Point':
            lat, lon = row.geometry.y, row.geometry.x
        else:
            lat, lon = row.geometry.centroid.y, row.geometry.centroid.x
            
        # Determine type
        place_type = "Unknown"
        if 'amenity' in row and pd.notna(row['amenity']): place_type = row['amenity']
        elif 'leisure' in row and pd.notna(row['leisure']): place_type = row['leisure']

        # Save to DB
        place_data = {
            'PlaceID': str(index),
            'Name': row['name'],
            'Type': place_type.capitalize(),
            'Lat': lat,
            'Lon': lon,
            'Budget': "Unknown",
            'VibeTags': ["New"],
            'Source': 'Seeded'
        }
        
        try:
            collection.update_one(
                {'PlaceID': str(index)}, 
                {'$setOnInsert': place_data}, 
                upsert=True
            )
            count += 1
        except:
            pass

print(f"✅ Success! Added {count} places to MongoDB Atlas.")