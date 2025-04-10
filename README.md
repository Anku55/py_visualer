# Python Code Structure Visualizer 🔍

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0%2B-green.svg)](https://flask.palletsprojects.com/)
[![D3.js](https://img.shields.io/badge/D3.js-7.0-orange.svg)](https://d3js.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![venv](https://img.shields.io/badge/venv-recommended-brightgreen.svg)](https://docs.python.org/3/library/venv.html)

An interactive visualization tool for Python codebases that creates beautiful, force-directed graphs showing the relationships between files, classes, functions, and imports.

## 🎥 Demo

<div align="center">
  <img src="docs/assets/demo.gif" alt="Python Code Visualizer Demo" width="800px">
  
  *Interactive visualization of a Python codebase showing files, classes, and their relationships*
</div>

## ✨ Features

### 📊 Visualization
- **Interactive Graph** - Drag, zoom, and explore your code structure
- **Color-Coded Nodes** 🎨
  - 🔷 Files (Blue)
  - 🟢 Classes (Green)
  - 🟡 Functions (Yellow)
  - 🟠 Methods (Orange)
  - ⚪ Imports (Gray)

### 🔄 Dynamic Updates
- **Real-time Cache Status** - Visual feedback in the navigation bar
- **Auto-clearing Visualizations** - Previous graphs are automatically removed
- **Manual Cache Clear** - Press `Ctrl + F5` to force clear the cache and refresh

### 🛠️ Analysis Features
- **Code Complexity** - Analyzes and displays code complexity metrics
- **Maintainability Index** - Shows code maintainability scores
- **Documentation Analysis** - Extracts and displays documentation info

### 🎯 Interactive Elements
- **Smart Tooltips** - Hover over nodes to see detailed information
- **Connection Highlighting** - See related nodes and connections on hover
- **Collapsible Sidebar** - Easy access to controls and legend
- **Zoom Controls** - Scroll to zoom, drag to pan

## 🚀 Getting Started

### Prerequisites
```bash
Python 3.8 or higher
pip (Python package manager)
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Anku55/py_visualer.git
cd py_visualer
```

2. Set up a virtual environment:
```bash
# On Windows
python -m venv venv
.\venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open in browser:
```
http://localhost:5000
```

### 🔒 Virtual Environment Tips

- **Creating New Environment**:
  ```bash
  python -m venv venv  # Creates a new virtual environment named 'venv'
  ```

- **Activation Commands**:
  - Windows (PowerShell): `.\venv\Scripts\activate`
  - Windows (Command Prompt): `venv\Scripts\activate.bat`
  - macOS/Linux: `source venv/bin/activate`

- **Deactivation**:
  ```bash
  deactivate  # Use this command when you're done
  ```

- **Requirements**:
  ```bash
  # After installing new packages, update requirements.txt:
  pip freeze > requirements.txt
  ```

## 💡 Usage Tips

### 📁 File Upload
1. Click "Choose File" to select a Python file or ZIP containing Python files
2. Click "Analyze Code" to generate the visualization

### 🔍 Navigation
- **Zoom**: Use mouse wheel or trackpad
- **Pan**: Click and drag on empty space
- **Move Nodes**: Click and drag nodes
- **View Details**: Hover over nodes for tooltips
- **Clear Cache**: Press `Ctrl + F5` for a fresh start

### 🎨 Visualization Controls
- **Sidebar**: Hover on the left edge to access controls
- **Legend**: View node and connection types
- **Status Updates**: Watch the cache status in the navigation bar

## 🔧 Troubleshooting

### Common Issues
- **Visualization Not Updating**: 
  - Press `Ctrl + F5` to clear cache
  - Check the cache status message in the navigation bar
- **Large Files**: 
  - Allow time for processing
  - Watch the status indicators for progress

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- D3.js for the visualization framework
- Flask for the backend server
- Bootstrap for the UI components 
