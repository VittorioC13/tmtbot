from flask import Flask, render_template, send_file
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    # Get list of briefs from daily_briefs directory
    briefs_dir = 'daily_briefs'
    briefs = []
    for filename in os.listdir(briefs_dir):
        if filename.endswith('.pdf'):
            # Extract date from filename (brief_YYYY-MM-DD.pdf)
            date_str = filename[6:-4]  # Remove 'brief_' prefix and '.pdf' suffix
            date = datetime.strptime(date_str, '%Y-%m-%d')
            briefs.append({
                'filename': filename,
                'date': date,
                'url': f'/brief/{filename}'
            })
    
    # Sort briefs by date (newest first)
    briefs.sort(key=lambda x: x['date'], reverse=True)
    return render_template('index.html', briefs=briefs)

@app.route('/brief/<filename>')
def get_brief(filename):
    return send_file(f'daily_briefs/{filename}', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True) 