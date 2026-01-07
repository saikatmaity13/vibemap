from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import osmnx as ox
import pandas as pd
import os
import random
import certifi
import dns.resolver
from dotenv import load_dotenv
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from bson.objectid import ObjectId
import spacy
import math
import re
from concurrent.futures import ThreadPoolExecutor

# --- 1. INTELLIGENCE SETUP ---
print("🧠 Loading Map Brain...")
try:
    nlp = spacy.load("en_core_web_md")
    print("✅ spaCy Loaded.")
except:
    print("⚠️ spaCy model missing. Run: python -m spacy download en_core_web_md")
    nlp = None

# --- 2. DB & FLASK SETUP ---
dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['8.8.8.8']

load_dotenv()
app = Flask(__name__)
app.secret_key = "super_secret_key"
MONGO_URI = os.getenv("MONGO_URI")

try:
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), tlsAllowInvalidCertificates=True, serverSelectionTimeoutMS=5000)
    db = client.vibemap_db
    collection = db.places
    users_collection = db.users
    bookmarks_collection = db.bookmarks
    
    collection.create_index("Type")
    collection.create_index("PlaceID", unique=True)
    print("✅ Connected to MongoDB Atlas.")
except Exception as e:
    print(f"❌ DB Error: {e}")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']

@login_manager.user_loader
def load_user(user_id):
    try:
        user_data = users_collection.find_one({"_id": ObjectId(user_id)})
        if user_data: return User(user_data)
    except: return None

# --- 3. VIBE MAP ---
VIBE_MAP = {
    'quiet': ['library', 'bookstore', 'place_of_worship', 'temple', 'museum', 'art_centre', 'gallery', 'yoga', 'garden'],
    'nature': ['park', 'garden', 'nature_reserve', 'lake', 'viewpoint', 'forest'],
    'active': ['gym', 'fitness_centre', 'stadium', 'playground', 'dance', 'climbing'],
    'foodie': ['restaurant', 'cafe', 'fast_food', 'ice_cream', 'bakery', 'pub', 'bar'],
    'nightlife': ['bar', 'pub', 'nightclub', 'cinema', 'theatre']
}

# --- REMOVED WORKOUT KEYS HERE ---
PRESET_INTENTS = {
    "🍔 Find Food": "foodie", 
    "I am hungry 🍔": "foodie",
    "☕ Need Coffee": "tired",
    "I need coffee ☕": "tired",
    "Quiet place 🤫": "quiet",
    "🤫 Quiet Spot": "quiet",
    "Nature vibes 🍃": "nature",
    "Party time 🎉": "nightlife",
    "🎉 Party": "nightlife",
    "😢 Cheer me up": "sad",
    "I am sad 😢": "sad"
}

def get_realistic_rating():
    return round(random.uniform(3.8, 4.9), 1)

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371 
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def search_osm_and_cache(query, lat, lon, dist=5000):
    print(f"🌍 DOWNLOADING: Fetching new data for {query}...")
    tags = {'amenity': query, 'leisure': query, 'building': query, 'tourism': query}
    if query in VIBE_MAP:
        mapped = VIBE_MAP[query]
        tags = {'amenity': mapped, 'leisure': mapped, 'building': mapped, 'tourism': mapped, 'landuse': mapped}
    
    try:
        gdf = ox.features_from_point((lat, lon), tags=tags, dist=dist)
        if gdf.empty: return []

        new_places = []
        for index, row in gdf.head(40).iterrows():
            if 'name' in row and pd.notna(row['name']):
                if row.geometry.geom_type == 'Point': p_lat, p_lon = row.geometry.y, row.geometry.x
                else: p_lat, p_lon = row.geometry.centroid.y, row.geometry.centroid.x
                
                place_type = "Place"
                for col in ['amenity', 'leisure', 'tourism', 'building']:
                    if col in row and pd.notna(row[col]):
                        place_type = row[col]; break
                
                item = {
                    'PlaceID': str(index), 'Name': row['name'], 
                    'Type': str(place_type).replace('_', ' ').capitalize(),
                    'Lat': p_lat, 'Lon': p_lon, 'City': "Bangalore",
                    'Rating': get_realistic_rating(), 'Address': f"Near {query}, Bangalore"
                }
                collection.update_one({'PlaceID': item['PlaceID']}, {'$setOnInsert': item}, upsert=True)
                new_places.append(item)
        return new_places
    except Exception as e:
        print(f"OSM Error: {e}")
        return []

def get_places_fast(search_term, lat=12.9716, lon=77.5946, dist=5000):
    regex_pattern = search_term
    if search_term in VIBE_MAP:
        regex_pattern = "|".join(VIBE_MAP[search_term])

    print(f"🔍 Searching DB for pattern: {regex_pattern}")
    db_results = list(collection.find({"Type": {"$regex": regex_pattern, "$options": "i"}}).limit(50))
    for p in db_results:
        if 'Rating' not in p: p['Rating'] = get_realistic_rating()

    if len(db_results) >= 5: return db_results, True
    return search_osm_and_cache(search_term, lat, lon, dist), False

# --- 4. ROUTES ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username')
        user_data = users_collection.find_one({"username": username})
        if not user_data:
            user_id = users_collection.insert_one({"username": username}).inserted_id
            user_data = {"_id": user_id, "username": username}
        login_user(User(user_data), remember=True)
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home(): 
    return render_template('index.html', name=current_user.username)

@app.route('/api/search')
@login_required
def search_places():
    query = request.args.get('q', 'cafe').lower()
    lat = float(request.args.get('lat', 12.9716))
    lon = float(request.args.get('lon', 77.5946))
    places, from_db = get_places_fast(query, lat, lon)
    for item in places: item.pop('_id', None)
    return jsonify({'places': places})

@app.route('/api/all_places')
@login_required
def get_all_places():
    print("📂 Fetching ALL data from DB...")
    places = list(collection.find().limit(2000))
    for item in places:
        item.pop('_id', None)
        if 'Rating' not in item: item['Rating'] = get_realistic_rating()
    return jsonify({'places': places})

# --- CRAWL & FEATURES ---
@app.route('/api/crawl', methods=['POST'])
@login_required
def generate_crawl():
    data = request.json
    crawl_type = data.get('type', 'date_night')
    sequences = {'date_night': ['restaurant', 'park', 'ice_cream']}
    steps = sequences.get(crawl_type, sequences['date_night'])

    candidates = []
    for step_query in steps:
        places, _ = get_places_fast(step_query, dist=5000)
        for p in places: 
            if 'Rating' not in p: p['Rating'] = get_realistic_rating()
        top_places = sorted(places, key=lambda x: x.get('Rating', 4.0), reverse=True)[:10]
        if not top_places: return jsonify({'error': f"Could not find places"}), 404
        candidates.append(top_places)

    best_path = [candidates[0][0], candidates[1][0], candidates[2][0]]
    for item in best_path: item.pop('_id', None)
    return jsonify({'path': best_path})

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    user_input = request.json.get('message', '').strip()
    
    # Check if we have a match
    if user_input in PRESET_INTENTS:
        best_match = PRESET_INTENTS[user_input]
        
        search_map = {
            'active': ('gym', "Get moving! Here are some gyms 💪"),
            'foodie': ('restaurant', "Here's some food nearby 🍔"),
            'nature': ('park', "Here is some fresh air 🍃"),
            'quiet': ('library', "Shh... quiet zones found 🤫"),
            'nightlife': ('bar', "Party time! 🎉"),
            'sad': ('ice_cream', "Sending virtual hugs & ice cream ❤️"),
            'tired': ('cafe', "Emergency caffeine detected ☕")
        }
        
        search_term, bot_reply = search_map.get(best_match, (None, ""))
        
        if search_term:
            places, _ = get_places_fast(search_term)
            for item in places: item.pop('_id', None)
            return jsonify({'reply': bot_reply, 'places': places})

    # NLP Fallback
    if nlp:
        doc = nlp(user_input.lower())
        best_match = None
        highest_score = 0
        NLP_ANCHORS = {
            'active': nlp("workout gym fitness"),
            'foodie': nlp("hungry food eat"),
            'nature': nlp("nature park trees"),
            'nightlife': nlp("party drink club")
        }
        for key, anchor in NLP_ANCHORS.items():
            score = doc.similarity(anchor)
            if score > 0.55 and score > highest_score:
                highest_score = score
                best_match = key
        
        if best_match:
            search_term = VIBE_MAP[best_match][0]
            places, _ = get_places_fast(search_term)
            for item in places: item.pop('_id', None)
            return jsonify({'reply': f"Found some {best_match} spots!", 'places': places})

    return jsonify({'reply': "I'm mostly a map bot! Try clicking the buttons.", 'places': []})

@app.route('/api/bookmark', methods=['POST'])
@login_required
def toggle_bookmark():
    data = request.json
    place_id = data.get('PlaceID')
    existing = bookmarks_collection.find_one({'user_id': current_user.id, 'PlaceID': place_id})
    if existing:
        bookmarks_collection.delete_one({'_id': existing['_id']})
        return jsonify({'status': 'removed'})
    else:
        bookmarks_collection.insert_one({**data, 'user_id': current_user.id})
        return jsonify({'status': 'added'})

@app.route('/api/user/bookmarks')
@login_required
def get_bookmarks():
    try:
        bookmarks = list(bookmarks_collection.find({'user_id': current_user.id}))
        for b in bookmarks:
            b.pop('_id', None); b.pop('user_id', None)
        return jsonify(bookmarks)
    except: return jsonify([])

@app.route('/api/heatmap', methods=['GET'])
@login_required
def get_heatmap_data():
    vibe = request.args.get('vibe', 'active') 
    regex_pattern = vibe
    if vibe in VIBE_MAP: regex_pattern = "|".join(VIBE_MAP[vibe])
    places = list(collection.find({"Type": {"$regex": regex_pattern, "$options": "i"}}, {"Lat": 1, "Lon": 1, "_id": 0}).limit(1000))
    return jsonify([[p['Lat'], p['Lon'], 1.0] for p in places if 'Lat' in p])

@app.route('/api/recommend', methods=['GET'])
@login_required
def get_recommendations():
    bookmarks = list(bookmarks_collection.find({'user_id': current_user.id}))
    if not bookmarks: return jsonify([])
    
    type_counts = {}
    for b in bookmarks:
        p_type = b.get('Type', 'Unknown')
        type_counts[p_type] = type_counts.get(p_type, 0) + 1
    
    favorite_type = max(type_counts, key=type_counts.get)
    saved_ids = [b['PlaceID'] for b in bookmarks]
    
    recommendations = list(collection.find({"Type": favorite_type, "PlaceID": {"$nin": saved_ids}}).limit(5))
    for item in recommendations: 
        item.pop('_id', None)
        if 'Rating' not in item: item['Rating'] = get_realistic_rating()
    return jsonify(recommendations)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)