from flask import Flask, render_template, request, jsonify, send_file
import os
from datetime import datetime
import sys

# Add the parent directory to the Python path to import the analyzer
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
news_collector_dir = os.path.join(parent_dir, 'IBD TMT - News Collector')
sys.path.append(news_collector_dir)
from main import IBDMarketAnalyst

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'daily_briefs'

# Initialize the analyzer
analyzer = IBDMarketAnalyst()

@app.route('/')
def index():
    """Render the main page"""
    print("Received request for index page")  # Debug print
    return render_template('index.html')

@app.route('/generate_brief', methods=['POST'])
def generate_brief():
    """Generate a new brief"""
    try:
        # Generate the brief
        brief_path = analyzer.generate_daily_brief()
        if not brief_path:
            raise Exception("Failed to generate brief")
        
        # Get the filename from the path
        filename = os.path.basename(brief_path)
        
        return jsonify({
            'success': True,
            'message': 'Brief generated successfully',
            'filename': filename
        })
    except Exception as e:
        print(f"Error in generate_brief: {str(e)}")  # Debug print
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/generate_interview_package', methods=['POST'])
def generate_interview_package():
    """Generate a new interview preparation package"""
    try:
        # Generate the interview package
        package_path = analyzer.generate_interview_package()
        if not package_path:
            raise Exception("Failed to generate interview package")
        
        # Get the filename from the path
        filename = os.path.basename(package_path)
        
        return jsonify({
            'success': True,
            'message': 'Interview package generated successfully',
            'filename': filename
        })
    except Exception as e:
        print(f"Error in generate_interview_package: {str(e)}")  # Debug print
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/download_brief/<filename>')
def download_brief(filename):
    """Download a specific brief"""
    try:
        brief_path = os.path.join(analyzer.briefs_dir, filename)
        if not os.path.exists(brief_path):
            raise Exception(f"Brief not found: {filename}")
            
        return send_file(
            brief_path,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        print(f"Error in download_brief: {str(e)}")  # Debug print
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404

@app.route('/download_interview_package/<filename>')
def download_interview_package(filename):
    """Download a specific interview package"""
    try:
        package_path = os.path.join(analyzer.interview_dir, filename)
        if not os.path.exists(package_path):
            raise Exception(f"Interview package not found: {filename}")
            
        return send_file(
            package_path,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        print(f"Error in download_interview_package: {str(e)}")  # Debug print
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404

@app.route('/list_briefs')
def list_briefs():
    """List all available briefs"""
    try:
        briefs = analyzer.list_past_briefs()
        return jsonify({
            'success': True,
            'briefs': briefs
        })
    except Exception as e:
        print(f"Error in list_briefs: {str(e)}")  # Debug print
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/list_interview_packages')
def list_interview_packages():
    """List all available interview packages"""
    try:
        packages = analyzer.list_interview_packages()
        return jsonify({
            'success': True,
            'packages': packages
        })
    except Exception as e:
        print(f"Error in list_interview_packages: {str(e)}")  # Debug print
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("\nStarting TMT Analysis Server...")
    print("Try accessing the website at: http://localhost:5000")
    print("Press CTRL+C to quit\n")
    
    # Run on localhost port 5000 (Flask's default port)
    app.run(host='localhost', port=5000, debug=True) 