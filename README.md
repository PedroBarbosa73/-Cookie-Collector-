# Cookie Collector 🍪

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python application with a graphical user interface for collecting and managing cookies from websites. The application uses Selenium WebDriver to automate browser interactions and SQLite to store the collected cookies.

## ✨ Features

- 🖥️ User-friendly graphical interface
- 🌐 Multiple browser support (Chrome, Firefox*, Edge*)
- 📑 Single and multiple site collection modes
- 🔒 Headless mode support (no visible browser window)
- 💾 Cookie storage in SQLite database
- 📊 Database viewer and manager
- 📈 Progress tracking with status updates
- ⚙️ Settings persistence
- 📤 Cookie export functionality

*Coming soon

## 🖼️ Screenshots

[Add screenshots of the application here]

## 📋 Requirements

- Python 3.7+
- Google Chrome browser
- Required Python packages (see requirements.txt)

## 🚀 Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/cookie-collector.git
cd cookie-collector
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Unix or MacOS:
source venv/bin/activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## 💻 Usage

1. Start the application:
```bash
python -m src.gui.CookieCollector
```

2. Using the application:
   - Select your browser (currently Chrome is fully supported)
   - Choose collection mode (Single Site or Multiple Sites)
   - Enter the URL(s) you want to collect cookies from
   - Adjust settings:
     - Page Load Wait Time: How long to wait for each page to load
     - Save to Database: Whether to store cookies in the database
     - Headless Mode: Run without visible browser window
   - Click "Start Collection" to begin
   - Monitor progress in the progress bar
   - View results in the detailed results window

3. Database Management:
   - Click "View Database" to open the database viewer
   - Browse collected cookies by website
   - Delete unwanted entries
   - Export cookies to JSON files

## 🗄️ Database Structure

The application uses SQLite to store cookies with the following schema:

### Websites Table
- id (Primary Key)
- url (Unique)
- created_at
- updated_at

### Cookies Table
- id (Primary Key)
- website_id (Foreign Key)
- name
- value
- domain
- path
- expires
- secure
- httpOnly
- sameSite

## 🔧 Development

The project structure is organized as follows:

```
cookie-collector/
├── src/
│   ├── __init__.py
│   ├── core.py
│   ├── database.py
│   ├── browser_base.py
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── CookieCollector.py
│   │   └── controller.py
│   └── browsers/
│       └── chrome/
│           └── chrome_browser.py
├── tests/
├── data/
│   └── settings.json
├── requirements.txt
└── README.md
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

MIT License

## ⚠️ Known Issues

- Firefox and Edge support is under development
- Some websites may block automated access
- USB device errors may appear in headless mode (these can be safely ignored)

## 🔜 Future Enhancements

- Complete Firefox and Edge browser support
- Cookie consent popup handling
- Cookie filtering options
- Import/Export in multiple formats
- Proxy support
- Custom browser profiles 