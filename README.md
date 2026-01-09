# 📄 PDF Scraper

A Python tool to download all PDF files from any webpage. Features both a sleek web dashboard and a command-line interface.

![Dashboard Screenshot](https://raw.githubusercontent.com/Laaxxmm/pdf-scraper/main/screenshot.png)

## ✨ Features

- 🌐 **Web Dashboard** - Beautiful dark UI with real-time progress
- 📁 **Custom Download Folder** - Save PDFs anywhere on your computer
- 🔗 **Smart URL Handling** - Works with both absolute and relative links
- 💻 **Cross-Platform** - Works on Windows, macOS, and Linux
- 📊 **Live Progress** - See downloads happening in real-time

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/pdf-scraper.git
cd pdf-scraper
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Dashboard

```bash
python dashboard.py
```

Open http://localhost:5000 in your browser.

## 📖 Usage

### Web Dashboard (Recommended)

1. Start the dashboard: `python dashboard.py`
2. Open http://localhost:5000
3. Enter the website URL with PDF links
4. Optionally specify a download folder (e.g., `~/Downloads/PDFs`)
5. Click **"Scrape PDFs"**

### Command Line

```bash
python pdf_scraper.py "https://example.com/documents"
```

## 📂 Download Folder Options

| Format | Example | Description |
|--------|---------|-------------|
| Default | *(leave empty)* | Saves to `Downloaded_PDFs` in project folder |
| Home directory | `~/Documents/PDFs` | Uses your home folder |
| Absolute path | `/Users/name/Desktop/PDFs` | Full path to folder |

## 🛠️ Requirements

- Python 3.7+
- requests
- beautifulsoup4
- flask (for dashboard)

## 📝 License

MIT License - feel free to use and modify!

---

Made with ❤️ for easy PDF downloading
