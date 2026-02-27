import os
import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS so your homepage browser tab can fetch data from this container
CORS(app)

JELLYFIN_URL = os.environ.get("JELLYFIN_URL", "http://192.168.1.100:8096").rstrip('/')
JELLYFIN_API_KEY = os.environ.get("JELLYFIN_API_KEY", "")
JELLYFIN_USER_ID = os.environ.get("JELLYFIN_USER_ID", "")
LIMIT = os.environ.get("LIMIT", "6") # How many posters to show

@app.route('/recent')
def get_recent():
    if not JELLYFIN_API_KEY or not JELLYFIN_USER_ID:
        return jsonify({"error": "JELLYFIN_API_KEY and JELLYFIN_USER_ID must be set"}), 500
        
    headers = {"Authorization": f'MediaBrowser Token="{JELLYFIN_API_KEY}"'}
    # Fetch latest movies and series
    url = f"{JELLYFIN_URL}/Users/{JELLYFIN_USER_ID}/Items/Latest?Limit={LIMIT}&IncludeItemTypes=Movie,Series"
    
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        data = r.json()
        
        results = []
        for item in data:
            item_id = item.get("Id")
            
            # Fetch high quality, resized posters
            poster_url = f"{JELLYFIN_URL}/Items/{item_id}/Images/Primary?fillWidth=200&quality=90"
            link = f"{JELLYFIN_URL}/web/index.html#!/details?id={item_id}&serverId={item.get('ServerId')}"
            
            results.append({
                "id": item_id,
                "title": item.get("Name"),
                "type": item.get("Type"),
                "year": item.get("ProductionYear", ""),
                "poster": poster_url,
                "link": link
            })
            
        return jsonify(results)
    except Exception as e:
        print(f"Error fetching from Jellyfin: {e}")
        return jsonify({"error": "Failed to fetch data from Jellyfin"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
