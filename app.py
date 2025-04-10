import os
import tempfile
import zipfile
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import networkx as nx
import ast
from flask_socketio import SocketIO
from flask_caching import Cache
from flask_cors import CORS
from radon.complexity import cc_visit
from radon.metrics import mi_visit
from code_analyzer.analyzer import CodeAnalyzer
from utils.file_handler import process_uploaded_file
from utils.metrics import calculate_code_metrics

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300

cache = Cache(app)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

ALLOWED_EXTENSIONS = {'py', 'zip'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Process the uploaded file
            code_files = process_uploaded_file(filepath)
            
            # Analyze the code
            analyzer = CodeAnalyzer()
            graph_data = analyzer.analyze_code(code_files)
            
            # Calculate code metrics
            metrics = calculate_code_metrics(code_files)
            
            # Convert NetworkX graph to D3.js format
            d3_data = convert_to_d3_format(graph_data)
            
            # Emit progress update
            socketio.emit('analysis_complete', {
                'status': 'success',
                'metrics': metrics
            })
            
            return jsonify({
                'success': True,
                'graph_data': d3_data,
                'metrics': metrics
            })
            
        except Exception as e:
            socketio.emit('analysis_error', {'error': str(e)})
            return jsonify({'error': str(e)}), 500
        finally:
            # Clean up uploaded file
            os.remove(filepath)
    
    return jsonify({'error': 'Invalid file type'}), 400

def convert_to_d3_format(graph):
    """Convert NetworkX graph to D3.js format with enhanced node data"""
    nodes = []
    for node, data in graph.nodes(data=True):
        nodes.append({
            'id': str(node),
            'type': data.get('type', 'unknown'),
            'name': data.get('name', str(node)),
            'complexity': data.get('complexity', 0),
            'maintainability': data.get('maintainability', 0),
            'documentation': data.get('documentation', ''),
            'code_snippet': data.get('code_snippet', '')
        })
    
    links = []
    for source, target, data in graph.edges(data=True):
        links.append({
            'source': str(source),
            'target': str(target),
            'type': data.get('type', 'unknown'),
            'weight': data.get('weight', 1)
        })
    
    return {
        'nodes': nodes,
        'links': links
    }

if __name__ == '__main__':
    socketio.run(app, debug=True) 