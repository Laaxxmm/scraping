#!/usr/bin/env python3
"""
PDF Scraper - Vercel Serverless Version
Finds all PDF links on a webpage for direct download.
"""

from flask import Flask, render_template_string, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os

app = Flask(__name__)

def get_pdf_links(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    
    pdf_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.lower().endswith('.pdf'):
            absolute_url = urljoin(url, href)
            filename = os.path.basename(urlparse(absolute_url).path) or "document.pdf"
            pdf_links.append({'url': absolute_url, 'name': filename})
    return pdf_links

HTML = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PDF Scraper</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Inter,sans-serif;background:#0f0f1a;color:#fff;min-height:100vh}
.container{max-width:900px;margin:0 auto;padding:40px 20px}
header{text-align:center;margin-bottom:40px}
.logo{font-size:3rem;margin-bottom:10px}
h1{font-size:2.5rem;background:linear-gradient(135deg,#e94560,#ff6b6b);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.subtitle{color:#a0a0b2;margin-top:8px}
.card{background:#16213e;border-radius:20px;padding:30px;margin-bottom:25px;border:1px solid rgba(255,255,255,0.1)}
.input-group{display:flex;gap:15px}
input{flex:1;padding:18px;border:2px solid rgba(255,255,255,0.1);border-radius:12px;background:#1a1a2e;color:#fff;font-size:1rem}
input:focus{outline:none;border-color:#e94560}
button{padding:18px 35px;background:linear-gradient(135deg,#e94560,#d63447);border:none;border-radius:12px;color:#fff;font-weight:600;cursor:pointer}
button:hover{transform:translateY(-2px)}
button:disabled{opacity:0.6}
.stat{text-align:center;padding:25px;background:#1a1a2e;border-radius:15px;margin-bottom:20px}
.stat-value{font-size:2.5rem;font-weight:700;color:#6c5ce7}
.stat-label{color:#a0a0b2;text-transform:uppercase}
.info{background:rgba(108,92,231,0.1);border:1px solid #6c5ce7;padding:15px;border-radius:10px;margin-bottom:20px;color:#a29bfe;text-align:center}
.files-list{max-height:400px;overflow-y:auto}
.file-item{display:flex;align-items:center;padding:15px;background:#1a1a2e;border-radius:10px;margin-bottom:10px;text-decoration:none}
.file-item:hover{transform:translateX(5px)}
.file-icon{width:45px;height:45px;background:linear-gradient(135deg,#ff6b6b,#e94560);border-radius:10px;display:flex;align-items:center;justify-content:center;margin-right:15px;font-size:1.2rem}
.file-name{flex:1;color:#fff;word-break:break-all}
.download-icon{font-size:1.5rem;color:#00d26a}
.loader{display:none;text-align:center;padding:30px;color:#a0a0b2}
.loader.show{display:block}
.spinner{display:inline-block;width:30px;height:30px;border:3px solid rgba(255,255,255,0.1);border-top-color:#e94560;border-radius:50%;animation:spin 1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.empty{text-align:center;padding:50px;color:#a0a0b2}
.empty .icon{font-size:4rem;opacity:0.5}
.error{background:rgba(233,69,96,0.1);border:1px solid #e94560;padding:12px;border-radius:10px;margin-top:10px;color:#e94560}
</style></head>
<body><div class="container">
<header><div class="logo">📄</div><h1>PDF Scraper</h1><p class="subtitle">Find all PDF links on any webpage</p></header>
<div class="card">
<div class="input-group"><input type="text" id="url" placeholder="https://example.com/documents">
<button id="btn" onclick="scan()">🔍 Find PDFs</button></div>
<div id="err"></div></div>
<div class="stat"><div class="stat-value" id="count">0</div><div class="stat-label">PDFs Found</div></div>
<div class="info">💡 Click any PDF to download it directly</div>
<div class="card">
<div id="loader" class="loader"><div class="spinner"></div><p style="margin-top:15px">Scanning...</p></div>
<div id="files" class="files-list"><div class="empty"><div class="icon">📥</div><p>Enter a URL to find PDFs</p></div></div>
</div></div>
<script>
async function scan(){const url=document.getElementById('url').value.trim();if(!url){showErr('Enter a URL');return}
document.getElementById('btn').disabled=true;document.getElementById('loader').classList.add('show');
document.getElementById('files').innerHTML='';document.getElementById('err').innerHTML='';document.getElementById('count').textContent='0';
try{const r=await fetch('/scan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url})});
const d=await r.json();document.getElementById('loader').classList.remove('show');document.getElementById('btn').disabled=false;
if(d.error){showErr(d.error);return}document.getElementById('count').textContent=d.pdfs.length;
if(d.pdfs.length===0){document.getElementById('files').innerHTML='<div class="empty"><div class="icon">🔍</div><p>No PDFs found</p></div>';return}
document.getElementById('files').innerHTML=d.pdfs.map(p=>\`<a href="\${p.url}" target="_blank" class="file-item"><div class="file-icon">📄</div><div class="file-name">\${p.name}</div><div class="download-icon">⬇️</div></a>\`).join('')}
catch(e){document.getElementById('loader').classList.remove('show');document.getElementById('btn').disabled=false;showErr('Error: '+e.message)}}
function showErr(m){document.getElementById('err').innerHTML=\`<div class="error">⚠️ \${m}</div>\`}
document.getElementById('url').addEventListener('keypress',e=>{if(e.key==='Enter')scan()})
</script></body></html>"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/scan', methods=['POST'])
def scan():
    try:
        data = request.get_json()
        url = data.get('url', '')
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        pdfs = get_pdf_links(url)
        return jsonify({'pdfs': pdfs, 'count': len(pdfs)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
