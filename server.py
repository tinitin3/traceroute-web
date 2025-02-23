from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import re
import requests
import os


app = Flask(__name__)
CORS(app) 

def run_traceroute(domain):
    result = subprocess.run(["traceroute", "-n", domain], capture_output=True, text=True)
    ips = re.findall(r'\d+\.\d+\.\d+\.\d+', result.stdout)
    return ips

@app.route("/traceroute", methods=["GET"])
def traceroute():
    domain = request.args.get("domain")
    if not domain:
        return jsonify({"error": "Missing domain"}), 400

    ips = run_traceroute(domain)
    geo_data = []
    
    for ip in ips:
        try:
            response = requests.get(f"http://ip-api.com/json/{ip}").json()
            if response["status"] == "success":
                geo_data.append({
                    "ip": ip,
                    "lat": response["lat"],
                    "lon": response["lon"],
                    "city": response.get("city", ""),
                    "country": response.get("country", "")
                })
        except Exception as e:
            print(f"Erreur avec {ip}: {e}")

    return jsonify(geo_data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
