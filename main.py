#!/usr/bin/env python3
"""
🚀 Samsung FOTA Hacker Terminal - COMPLETE SINGLE FILE
Matrix theme + Flask web UI + Multi-region scraper + GitHub auto-save
Deploy: Render.com FREE | No extra files needed!
"""

import os
import sys
import json
import time
import random
import threading
import subprocess
from flask import Flask, render_template, request, jsonify
import requests
from xml.etree import ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from github import Github

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG - Render Environment Variables
# ═══════════════════════════════════════════════════════════════════════════════
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = os.getenv('GITHUB_REPO', 'AdnanHossen123/Sumsung_DataBase')
GITHUB_FILE_PATH = 'DataBase.json'

app = Flask(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# FOTA SCRAPER CLASS
# ═══════════════════════════════════════════════════════════════════════════════
class SamsungFOTAScraper:
    def __init__(self, model: str, max_workers: int = 25):
        self.model = model.upper()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.max_workers = max_workers
        self.regions = [
            "XAC","XAR","XAS","XAT","XAU","XEU","XFE","XFM","XFV","XID","XIN","XIT","XME",
            "XNZ","XPR","XSG","XSP","XTB","XTC","XTM","XUK","XXV","AFG","ALB","ARE","ARG",
            "ARM","AUS","AUT","AZE","BDU","BEL","BGD","BGL","BLA","BNC","BOL","BRA","BWA",
            "CAN","CHE","CHL","CHN","CHT","CIE","CIG","COL","CRI","CYP","CZE","DEU","DNK",
            "DOM","DOR","ECU","EGY","ESP","EST","ETH","FIN","FRA","GBR","GEO","GHN","GRC",
            "GTM","HKG","HRV","HUN","IDN","IND","IRN","IRQ","ISR","ITA","JED","JOR","JPN",
            "KAZ","KEN","KOR","KSA","KWT","LAV","LTU","LUX","LVA","MAR","MEX","MGL","MKD",
            "MM1","MNE","MOZ","MWI","MYM","NEE","NLD","NOR","NZC","PAK","PAN","PER","PHN",
            "PLA","POL","PRT","QAT","ROM","RUS","SAU","SER","SGP","SVK","SVN","SWE","THL",
            "TPE","TUR","TWN","UKR","URY","USA","VEN","VIE","XAA","XAM","XEU","XFA","XID2",
            "XIN","XME","XMY","XSG","XSA","XTB","XNZ","ZAF","ZAM","ZSA","ZTM","ZTO","ZVV"
        ]

    def scrape_region(self, region: str) -> str | None:
        url = f"https://fota-cloud-dn.ospserver.net/firmware/{region}/{self.model}/version.xml"
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                latest = root.find(".//latest")
                return latest.text.strip() if latest is not None and latest.text else None
        except:
            pass
        return None

    def scrape_all(self) -> dict:
        build_ids = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.scrape_region, region): region for region in self.regions}
            for future in as_completed(futures):
                result = future.result()
                if result and result not in build_ids:
                    build_ids.append(result)
        
        unique_builds = sorted(list(dict.fromkeys(build_ids)))
        return {"model": self.model, "build_id": unique_builds}

# ═══════════════════════════════════════════════════════════════════════════════
# GITHUB SAVER
# ═══════════════════════════════════════════════════════════════════════════════
def save_to_github(new_data: list):
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)
        
        try:
            file_content = repo.get_contents(GITHUB_FILE_PATH)
            existing_data = json.loads(file_content.decoded_content.decode('utf-8'))
        except:
            existing_data = []
        
        model_builds = {}
        for item in existing_data + new_data:
            model = item["model"].strip().upper()
            if model not in model_builds:
                model_builds[model] = set()
            model_builds[model].update(item["build_id"])
        
        final_data = [{"model": model, "build_id": sorted(list(builds))} 
                     for model, builds in model_builds.items()]
        
        content = json.dumps(final_data, ensure_ascii=False, indent=2).encode('utf-8')
        message = f"FOTA Update: {len(new_data)} models → {len(final_data)} total"
        
        if file_content:
            repo.update_file(GITHUB_FILE_PATH, message, content, file_content.sha)
        else:
            repo.create_file(GITHUB_FILE_PATH, message, content)
        
        print(f"✅ SAVED: {len(final_data)} models → {GITHUB_REPO}/{GITHUB_FILE_PATH}")
        return True
    except Exception as e:
        print(f"❌ GITHUB ERROR: {e}")
        return False

# ═══════════════════════════════════════════════════════════════════════════════
# FLASK ROUTES - HACKER TERMINAL UI
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Samsung FOTA Hacker Terminal</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { 
            background: #000; 
            color: #00ff41; 
            font-family: 'Courier New', monospace; 
            overflow: hidden; 
            height: 100vh;
        }
        canvas { 
            position: fixed; top:0; left:0; z-index:1; 
            filter: contrast(150%) brightness(1.2);
        }
        .terminal { 
            position: relative; z-index:10; 
            padding: 40px; height:100vh; 
            backdrop-filter: blur(10px);
        }
        .input-group { 
            display: flex; gap:20px; align-items:center; 
            margin-bottom: 30px; 
        }
        input[type="text"] { 
            flex:1; padding:15px 20px; 
            background: rgba(0,255,65,0.1); 
            border: 2px solid #00ff41; 
            color: #00ff41; font-size:18px; 
            border-radius: 8px; 
            outline: none; 
            box-shadow: 0 0 20px rgba(0,255,65,0.3);
        }
        input[type="text"]:focus { 
            box-shadow: 0 0 40px rgba(0,255,65,0.6); 
            border-color: #00cc33;
        }
        .btn { 
            padding:15px 30px; background:#00ff41; 
            color:#000; border:none; 
            font-size:18px; font-weight:bold; 
            border-radius:8px; cursor:pointer; 
            box-shadow: 0 0 20px rgba(0,255,65,0.5);
            transition: all 0.3s;
        }
        .btn:hover { box-shadow: 0 0 40px rgba(0,255,65,0.8); transform: scale(1.05); }
        .btn:disabled { opacity:0.5; cursor:not-allowed; transform:none; }
        .status { 
            padding:20px; margin:20px 0; 
            border-radius:8px; font-size:16px; 
            border-left:4px solid #00ff41;
        }
        .success { background: rgba(0,255,65,0.1); }
        .processing { background: rgba(0,255,65,0.2); animation: pulse 1.5s infinite; }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }
        .models-list { 
            background: rgba(0,0,0,0.7); 
            padding:15px; border-radius:8px; 
            margin:10px 0; font-family:monospace;
        }
        .progress { 
            width:100%; height:8px; background:rgba(0,255,65,0.2); 
            border-radius:4px; overflow:hidden; margin:10px 0;
        }
        .progress-bar { 
            height:100%; background:#00ff41; 
            width:0%; transition: width 0.3s; 
            box-shadow: 0 0 20px #00ff41;
        }
        .scanline { position:fixed; top:0; left:0; width:100%; height:2px; background:linear-gradient(90deg,transparent,#00ff4180,transparent); z-index:20; animation: scan 3s linear infinite; }
        @keyframes scan { 0%{ transform:translateY(0%); } 100%{ transform:translateY(100vh); } }
    </style>
</head>
<body>
    <canvas id="matrix"></canvas>
    <div class="scanline"></div>
    
    <div class="terminal">
        <h1 style="font-size:28px; margin-bottom:20px; text-shadow:0 0 20px #00ff41;">🔥 SAMSUNG FOTA HACKER TERMINAL</h1>
        <p style="color:#00cc66; margin-bottom:20px;">Enter models (comma separated): <span id="example" style="font-family:monospace;">SM-A055F,SM-G998B,SM-S918B</span></p>
        
        <div class="input-group" id="inputGroup">
            <input type="text" id="modelsInput" placeholder="SM-A055F,SM-G998B..." />
            <button class="btn" onclick="deployFota()">DEPLOY FOTA</button>
        </div>
        
        <div id="status" style="display:none;"></div>
        <div id="progress" style="display:none;">
            <div class="progress"><div class="progress-bar" id="progressBar"></div></div>
        </div>
    </div>

    <script>
        // Matrix Rain Effect
        const canvas = document.getElementById('matrix');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        
        const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
        const fontSize = 14;
        const columns = canvas.width / fontSize;
        const drops = Array(Math.floor(columns)).fill(1);
        
        function drawMatrix() {
            ctx.fillStyle = 'rgba(0,0,0,0.05)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#00ff41';
            ctx.font = fontSize + 'px monospace';
            
            for(let i=0; i<drops.length; i++) {
                const text = chars[Math.floor(Math.random()*chars.length)];
                ctx.fillText(text, i*fontSize, drops[i]*fontSize);
                if(drops[i]*fontSize > canvas.height && Math.random() > 0.975)
                    drops[i] = 0;
                drops[i]++;
            }
        }
        setInterval(drawMatrix, 50);
        
        // Deploy FOTA
        async function deployFota() {
            const input = document.getElementById('modelsInput');
            const models = input.value.split(',').map(m=>m.trim()).filter(m=>m);
            
            if(!models.length) return alert('Enter models!');
            
            // UI States
            document.getElementById('inputGroup').style.display = 'none';
            const status = document.getElementById('status');
            status.innerHTML = `
                <div class="status processing">
                    <strong>🚀 DEPLOYING FOTA TARGETS...</strong><br>
                    <div class="models-list">${models.join(' ')}</div>
                    <small>Scanning 130+ regions... GitHub sync in progress</small>
                </div>
            `;
            status.style.display = 'block';
            document.getElementById('progress').style.display = 'block';
            
            try {
                const response = await fetch('/scrape', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({models})
                });
                const result = await response.json();
                
                if(response.ok) {
                    status.innerHTML = `
                        <div class="status success">
                            ✅ <strong>${result.message}</strong><br>
                            🔗 <a href="https://github.com/${result.repo}/blob/main/${result.file}" target="_blank" style="color:#00ff41;">View DataBase.json</a>
                        </div>
                    `;
                    document.getElementById('progressBar').style.width = '100%';
                } else {
                    throw new Error(result.error || 'Deploy failed');
                }
            } catch(e) {
                status.innerHTML = `<div class="status" style="background:rgba(255,0,0,0.2);border-left-color:#ff4444;">❌ ${e.message}</div>`;
            }
        }
        
        // Enter key
        document.getElementById('modelsInput').addEventListener('keypress', e=>{
            if(e.key==='Enter') deployFota();
        });
        
        window.addEventListener('resize', ()=> {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        });
    </script>
</body>
</html>
    '''

# ═══════════════════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    models = [m.strip().upper() for m in data.get('models', []) if m.strip()]
    
    if not models:
        return jsonify({'error': 'NO TARGETS'}), 400
    
    def run_scraper():
        all_data = []
        for model in models:
            print(f"🔍 [{models.index(model)+1}/{len(models)}] {model}")
            scraper = SamsungFOTAScraper(model)
            data = scraper.scrape_all()
            if data['build_id']:
                all_data.append(data)
                print(f"✅ {len(data['build_id'])} builds")
        
        if all_data:
            save_to_github(all_data)
    
    thread = threading.Thread(target=run_scraper)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'message': f'Deployed {len(models)} FOTA targets',
        'models': models,
        'repo': GITHUB_REPO,
        'file': GITHUB_FILE_PATH,
        'status': 'EXECUTING'
    })

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN - Render Compatible
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Samsung FOTA Hacker Terminal LIVE!")
    print(f"📱 GitHub: {GITHUB_REPO}/{GITHUB_FILE_PATH}")
    app.run(debug=False, host='0.0.0.0', port=port)
