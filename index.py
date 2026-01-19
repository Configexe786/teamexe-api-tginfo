from flask import Flask, jsonify, request
import pandas as pd
import os

app = Flask(__name__)

# Config
DB_DIR = 'database'
API_KEY_FILE = 'apikey.txt'

def get_api_key():
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE, 'r') as f:
            return f.read().strip()
    return "YDAIoYzubTQCsxlG" # Default backup key

@app.route('/')
def home():
    return jsonify({
        "status": "Online",
        "api": "TeamEXE TG Info API",
        "search_type": "Telegram User ID",
        "dev": "@istgrehu"
    })

@app.route('/fetch', methods=['GET'])
def fetch_data():
    # 1. Auth Check
    user_key = request.args.get('key')
    if user_key != get_api_key():
        return jsonify({"error": "Invalid API Key"}), 403

    # 2. Query Check (Now expecting User ID)
    user_id = request.args.get('num')
    if not user_id:
        return jsonify({"error": "Please provide Telegram User ID (?num=)"}), 400

    search_val = str(user_id).strip()

    try:
        # Loop through your 13 split parts
        for i in range(1, 14):
            file_name = f"Telegram_27_{i:03d}.csv"
            path = os.path.join(DB_DIR, file_name)
            
            if not os.path.exists(path):
                continue
            
            # Fast reading in chunks to avoid Vercel RAM crash
            for chunk in pd.read_csv(path, encoding='latin-1', chunksize=15000, low_memory=False):
                # Search for the User ID in all columns
                # Isse phone number ya ID dono mil jayenge
                match = chunk[chunk.apply(lambda r: r.astype(str).str.contains(search_val).any(), axis=1)]
                
                if not match.empty:
                    # Convert found row to dictionary
                    result_data = match.iloc[0].to_dict()
                    
                    return jsonify({
                        "status": "success",
                        "dev": "@istgrehu",
                        "source_file": file_name,
                        "data": result_data
                    })

        return jsonify({"status": "not_found", "message": "User ID not found in database"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
