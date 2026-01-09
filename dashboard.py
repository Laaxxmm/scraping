#!/usr/bin/env python3
"""
PDF Scraper Dashboard - Flask Web Application
A beautiful web dashboard to scrape PDFs from any website.
"""

import os
import json
import threading
from flask import Flask, render_template_string, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

app = Flask(__name__)

# Global state for tracking downloads
download_status = {
    'is_running': False,
    'url': '',
    'folder': '',
    'found': 0,
    'downloaded': 0,
    'failed': 0,
    'files': [],
    'errors': [],
    'complete': False
}

def reset_status():
    global download_status
    download_status = {
        'is_running': False,
        'url': '',
        'folder': '',
        'found': 0,
        'downloaded': 0,
        'failed': 0,
        'files': [],
        'errors': [],
        'complete': False
    }

def create_download_folder(folder_path=None):
    """Create the download folder. Uses provided path or defaults to Downloaded_PDFs."""
    if folder_path and folder_path.strip():
        # Expand user path (handles ~)
        download_path = os.path.expanduser(folder_path.strip())
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        download_path = os.path.join(script_dir, "Downloaded_PDFs")
    
    os.makedirs(download_path, exist_ok=True)
    return download_path

def get_pdf_links(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    
    pdf_links = set()
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.lower().endswith('.pdf'):
            absolute_url = urljoin(url, href)
            pdf_links.add(absolute_url)
    
    return list(pdf_links)

def get_filename_from_url(url):
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)
    if not filename:
        filename = "document.pdf"
    if not filename.lower().endswith('.pdf'):
        filename += '.pdf'
    return filename

def download_pdf(url, download_path):
    global download_status
    filename = get_filename_from_url(url)
    filepath = os.path.join(download_path, filename)
    
    counter = 1
    original_filepath = filepath
    while os.path.exists(filepath):
        name, ext = os.path.splitext(original_filepath)
        filepath = f"{name}_{counter}{ext}"
        counter += 1
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=60, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size = os.path.getsize(filepath)
        download_status['downloaded'] += 1
        download_status['files'].append({
            'name': os.path.basename(filepath),
            'size': f"{file_size / 1024:.1f} KB",
            'status': 'success'
        })
        return True
        
    except Exception as e:
        download_status['failed'] += 1
        download_status['errors'].append(f"{filename}: {str(e)}")
        return False

def scrape_worker(url, folder_path):
    global download_status
    try:
        download_path = create_download_folder(folder_path)
        download_status['folder'] = download_path
        
        pdf_links = get_pdf_links(url)
        download_status['found'] = len(pdf_links)
        
        if not pdf_links:
            download_status['errors'].append("No PDF links found on this page")
            download_status['complete'] = True
            download_status['is_running'] = False
            return
        
        for pdf_url in pdf_links:
            download_pdf(pdf_url, download_path)
        
        download_status['complete'] = True
        download_status['is_running'] = False
        
    except Exception as e:
        download_status['errors'].append(str(e))
        download_status['complete'] = True
        download_status['is_running'] = False

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Scraper Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0f0f1a;
            --bg-secondary: #1a1a2e;
            --bg-card: #16213e;
            --accent: #e94560;
            --accent-glow: rgba(233, 69, 96, 0.4);
            --success: #00d26a;
            --text-primary: #ffffff;
            --text-secondary: #a0a0b2;
            --border: rgba(255, 255, 255, 0.1);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            background-image: 
                radial-gradient(ellipse at top, rgba(233, 69, 96, 0.1) 0%, transparent 50%),
                radial-gradient(ellipse at bottom, rgba(0, 210, 106, 0.05) 0%, transparent 50%);
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        
        header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .logo {
            font-size: 3rem;
            margin-bottom: 10px;
            animation: pulse 2s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
        h1 {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent), #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }
        
        .subtitle {
            color: var(--text-secondary);
            font-size: 1.1rem;
        }
        
        .card {
            background: var(--bg-card);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 25px;
            border: 1px solid var(--border);
            backdrop-filter: blur(10px);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        }
        
        .input-row {
            margin-bottom: 15px;
        }
        
        .input-row:last-child {
            margin-bottom: 0;
        }
        
        .input-label {
            display: block;
            color: var(--text-secondary);
            font-size: 0.85rem;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .input-group {
            display: flex;
            gap: 15px;
        }
        
        input[type="text"] {
            flex: 1;
            padding: 18px 25px;
            border: 2px solid var(--border);
            border-radius: 12px;
            background: var(--bg-secondary);
            color: var(--text-primary);
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        input[type="text"]:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 20px var(--accent-glow);
        }
        
        input[type="text"]::placeholder {
            color: var(--text-secondary);
        }
        
        button {
            padding: 18px 35px;
            background: linear-gradient(135deg, var(--accent), #d63447);
            border: none;
            border-radius: 12px;
            color: white;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            white-space: nowrap;
        }
        
        button:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px var(--accent-glow);
        }
        
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .status-bar {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 25px;
        }
        
        .stat {
            text-align: center;
            padding: 25px;
            background: var(--bg-secondary);
            border-radius: 15px;
            border: 1px solid var(--border);
        }
        
        .stat-value {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 5px;
        }
        
        .stat-label {
            color: var(--text-secondary);
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .stat.found .stat-value { color: #6c5ce7; }
        .stat.success .stat-value { color: var(--success); }
        .stat.failed .stat-value { color: var(--accent); }
        
        .folder-path {
            text-align: center;
            padding: 15px;
            background: rgba(0, 210, 106, 0.1);
            border-radius: 10px;
            margin-bottom: 20px;
            font-size: 0.9rem;
            color: var(--success);
            display: none;
        }
        
        .folder-path.show {
            display: block;
        }
        
        .files-list {
            max-height: 350px;
            overflow-y: auto;
        }
        
        .file-item {
            display: flex;
            align-items: center;
            padding: 15px;
            background: var(--bg-secondary);
            border-radius: 10px;
            margin-bottom: 10px;
            animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        .file-icon {
            width: 45px;
            height: 45px;
            background: linear-gradient(135deg, #ff6b6b, var(--accent));
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 15px;
            font-size: 1.2rem;
        }
        
        .file-info {
            flex: 1;
        }
        
        .file-name {
            font-weight: 500;
            margin-bottom: 3px;
            word-break: break-all;
        }
        
        .file-size {
            color: var(--text-secondary);
            font-size: 0.85rem;
        }
        
        .file-status {
            font-size: 1.3rem;
        }
        
        .loader {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid var(--border);
            border-top-color: var(--accent);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 10px;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .progress-text {
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-secondary);
            margin-top: 15px;
        }
        
        .empty-state {
            text-align: center;
            padding: 50px;
            color: var(--text-secondary);
        }
        
        .empty-state .icon {
            font-size: 4rem;
            margin-bottom: 15px;
            opacity: 0.5;
        }
        
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--bg-secondary);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--border);
            border-radius: 4px;
        }
        
        .error-msg {
            background: rgba(233, 69, 96, 0.1);
            border: 1px solid var(--accent);
            padding: 12px 18px;
            border-radius: 10px;
            margin-top: 10px;
            color: var(--accent);
        }
        
        .hint {
            font-size: 0.8rem;
            color: var(--text-secondary);
            margin-top: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">📄</div>
            <h1>PDF Scraper</h1>
            <p class="subtitle">Download all PDFs from any webpage to your chosen folder</p>
        </header>
        
        <div class="card">
            <div class="input-row">
                <label class="input-label">Website URL</label>
                <input type="text" id="urlInput" placeholder="https://example.com/documents">
            </div>
            
            <div class="input-row">
                <label class="input-label">Download Folder (Optional)</label>
                <div class="input-group">
                    <input type="text" id="folderInput" placeholder="~/Downloads/PDFs or /Users/name/Documents/PDFs">
                    <button id="scrapeBtn" onclick="startScrape()">
                        🚀 Scrape PDFs
                    </button>
                </div>
                <p class="hint">💡 Leave empty for default folder. Use ~ for home directory (e.g., ~/Desktop/MyPDFs)</p>
            </div>
            <div id="errorContainer"></div>
        </div>
        
        <div class="status-bar">
            <div class="stat found">
                <div class="stat-value" id="foundCount">0</div>
                <div class="stat-label">Found</div>
            </div>
            <div class="stat success">
                <div class="stat-value" id="downloadedCount">0</div>
                <div class="stat-label">Downloaded</div>
            </div>
            <div class="stat failed">
                <div class="stat-value" id="failedCount">0</div>
                <div class="stat-label">Failed</div>
            </div>
        </div>
        
        <div id="folderDisplay" class="folder-path">
            📁 Files saved to: <span id="folderPath"></span>
        </div>
        
        <div class="card">
            <div id="filesList" class="files-list">
                <div class="empty-state">
                    <div class="icon">📥</div>
                    <p>Enter a URL above to start downloading PDFs</p>
                </div>
            </div>
            <div id="progressText" class="progress-text" style="display: none;">
                <span class="loader"></span>
                Scanning page and downloading PDFs...
            </div>
        </div>
    </div>
    
    <script>
        let isPolling = false;
        
        async function startScrape() {
            const url = document.getElementById('urlInput').value.trim();
            const folder = document.getElementById('folderInput').value.trim();
            
            if (!url) {
                showError('Please enter a URL');
                return;
            }
            
            document.getElementById('scrapeBtn').disabled = true;
            document.getElementById('progressText').style.display = 'flex';
            document.getElementById('filesList').innerHTML = '';
            document.getElementById('errorContainer').innerHTML = '';
            document.getElementById('folderDisplay').classList.remove('show');
            
            try {
                const response = await fetch('/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url, folder })
                });
                
                if (response.ok) {
                    isPolling = true;
                    pollStatus();
                } else {
                    showError('Failed to start scraping');
                    document.getElementById('scrapeBtn').disabled = false;
                }
            } catch (e) {
                showError('Connection error');
                document.getElementById('scrapeBtn').disabled = false;
            }
        }
        
        async function pollStatus() {
            if (!isPolling) return;
            
            try {
                const response = await fetch('/status');
                const data = await response.json();
                
                document.getElementById('foundCount').textContent = data.found;
                document.getElementById('downloadedCount').textContent = data.downloaded;
                document.getElementById('failedCount').textContent = data.failed;
                
                if (data.folder) {
                    document.getElementById('folderPath').textContent = data.folder;
                    document.getElementById('folderDisplay').classList.add('show');
                }
                
                updateFilesList(data.files);
                
                if (data.complete) {
                    isPolling = false;
                    document.getElementById('scrapeBtn').disabled = false;
                    document.getElementById('progressText').style.display = 'none';
                    
                    if (data.errors.length > 0) {
                        data.errors.forEach(err => showError(err));
                    }
                } else {
                    setTimeout(pollStatus, 500);
                }
            } catch (e) {
                setTimeout(pollStatus, 1000);
            }
        }
        
        function updateFilesList(files) {
            if (files.length === 0) return;
            
            const html = files.map(f => `
                <div class="file-item">
                    <div class="file-icon">📄</div>
                    <div class="file-info">
                        <div class="file-name">${f.name}</div>
                        <div class="file-size">${f.size}</div>
                    </div>
                    <div class="file-status">${f.status === 'success' ? '✅' : '❌'}</div>
                </div>
            `).join('');
            
            document.getElementById('filesList').innerHTML = html;
        }
        
        function showError(msg) {
            document.getElementById('errorContainer').innerHTML += 
                `<div class="error-msg">⚠️ ${msg}</div>`;
        }
        
        // Enter key support
        document.getElementById('urlInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') startScrape();
        });
        document.getElementById('folderInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') startScrape();
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/start', methods=['POST'])
def start_scrape():
    global download_status
    data = request.get_json()
    url = data.get('url', '')
    folder = data.get('folder', '')
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    if download_status['is_running']:
        return jsonify({'error': 'Already running'}), 400
    
    # Add https if needed
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    reset_status()
    download_status['is_running'] = True
    download_status['url'] = url
    
    # Start scraping in background thread
    thread = threading.Thread(target=scrape_worker, args=(url, folder))
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'started'})

@app.route('/status')
def get_status():
    return jsonify(download_status)

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 PDF Scraper Dashboard")
    print("=" * 50)
    print("📍 Open http://localhost:5000 in your browser")
    print("💡 You can specify any folder to save PDFs")
    print("=" * 50)
    app.run(debug=False, host='0.0.0.0', port=5000)
