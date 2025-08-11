# TMT Daily News Analyzer

An automated system that collects, analyzes, and generates daily briefs for Technology, Media, and Telecommunications (TMT) sector news. The system uses AI to provide comprehensive analysis and insights, and generates professional PDF reports.

## Features

- Automated news collection from multiple sources
- AI-powered analysis using GPT-4
- Comprehensive market insights and trends
- Professional PDF report generation
- Web interface for viewing and downloading briefs
- Responsive design for all devices

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- NewsAPI key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/tmt-daily-news-analyzer.git
cd tmt-daily-news-analyzer
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your API keys:
```
OPENAI_API_KEY=your_openai_api_key_here
NEWS_API_KEY=your_newsapi_key_here
```

## Usage

1. Run the news analyzer:
```bash
python tmt_news_analyzer.py
```

2. View the generated briefs:
- Open the web interface by running a local server in the `static-website` directory
- Access the PDFs directly from the `daily_briefs` directory

## Project Structure

```
tmt-daily-news-analyzer/
├── tmt_news_analyzer.py    # Main news analysis script
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not in repo)
├── daily_briefs/          # Generated PDF briefs
└── static-website/        # Web interface
    ├── index.html
    ├── css/
    ├── js/
    └── assets/
```

## Web Interface

The project includes a modern, responsive web interface for viewing and downloading daily briefs. To run the web interface:

1. Navigate to the static-website directory:
```bash
cd static-website
```

2. Start a local server:
```bash
python -m http.server 8000
```

3. Open your browser and visit:
```
http://localhost:8000
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the GPT-4 API
- NewsAPI for news data
- FPDF for PDF generation 