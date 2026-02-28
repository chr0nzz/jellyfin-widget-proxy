import os
import requests
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jellyfin_proxy")

app = Flask("jellyfin_proxy")
CORS(app)

JELLYFIN_URL = os.environ.get("JELLYFIN_URL", "http://192.168.1.100:8096").rstrip('/')
JELLYFIN_API_KEY = os.environ.get("JELLYFIN_API_KEY", "")
JELLYFIN_USER_ID = os.environ.get("JELLYFIN_USER_ID", "")
LIMIT = int(os.environ.get("LIMIT", "6"))

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

logger.info("jellyfin-proxy-widget starting...")
logger.info(f"JELLYFIN_URL={JELLYFIN_URL}")
logger.info(f"API_KEY_SET={'Yes' if JELLYFIN_API_KEY else 'No'}")
logger.info(f"USER_ID_SET={'Yes' if JELLYFIN_USER_ID else 'No'}")
logger.info(f"LIMIT={LIMIT}")

def fetch_latest(item_type):
    """Helper to fetch latest items by type"""
    headers = {"Authorization": f'MediaBrowser Token="{JELLYFIN_API_KEY}"'}
    url = f"{JELLYFIN_URL}/Users/{JELLYFIN_USER_ID}/Items/Latest"
    params = {
        "Limit": LIMIT,
        "IncludeItemTypes": item_type,
        "Fields": "PrimaryImageAspectRatio,ProductionYear,ServerId,DateCreated,SeriesId,SeriesName"
    }
    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.error(f"Error fetching {item_type}: {e}")
        return []

@app.route('/recent')
def get_recent():
    if not JELLYFIN_API_KEY or not JELLYFIN_USER_ID:
        logger.error("Missing configuration: API Key or User ID not set")
        return jsonify({"error": "JELLYFIN_API_KEY and JELLYFIN_USER_ID must be set"}), 500
        
    try:
        logger.info(f"Fetching latest Movies and Episodes separately...")
        
        movies = fetch_latest("Movie")
        episodes = fetch_latest("Episode")
        
        combined_data = movies + episodes
        
        combined_data.sort(key=lambda x: x.get("DateCreated", ""), reverse=True)
        
        final_items = combined_data[:LIMIT]
        
        results = []
        for item in final_items:
            item_id = item.get("Id")
            item_type = item.get("Type")
            
            is_episode = item_type == "Episode"
            display_title = item.get("SeriesName") if is_episode else item.get("Name")
            
            poster_id = item.get("SeriesId") if is_episode else item_id
            
            poster_url = f"{JELLYFIN_URL}/Items/{poster_id}/Images/Primary?fillWidth=200&quality=90"
            link = f"{JELLYFIN_URL}/web/index.html#!/details?id={item_id}&serverId={item.get('ServerId')}"
            
            results.append({
                "id": item_id,
                "title": display_title,
                "type": "TV" if is_episode else "Movie",
                "year": item.get("ProductionYear", ""),
                "poster": poster_url,
                "link": link,
                "date": item.get("DateCreated")
            })
            
        logger.info(f"Successfully returned {len(results)} merged items")
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error merging data: {e}")
        return jsonify({"error": "Failed to fetch data from Jellyfin"}), 500

if __name__ == '__main__':
    logger.info("🚀 Jellyfin Proxy: Development server starting...")
    app.run(host='0.0.0.0', port=5000)
else:
    logger.info("✅ Jellyfin Proxy: Server is UP and Ready (Gunicorn)")
