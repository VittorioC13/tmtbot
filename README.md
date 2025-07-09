# TMT News Collector & Analysis Tool

A comprehensive tool for collecting, analyzing, and generating reports on Technology, Media & Telecommunications (TMT) sector news, with a focus on M&A activities and valuations.

## Features

- **News Collection**: Automated collection of TMT sector news from multiple sources
- **AI-Powered Analysis**: Advanced analysis using OpenAI GPT models
- **PDF Report Generation**: Professional PDF briefs with detailed market analysis
- **Interview Preparation**: Comprehensive interview packages for investment banking roles
- **M&A Focus**: Specialized analysis of mergers, acquisitions, and valuations

## Setup

### Prerequisites

- Python 3.8+
- NewsAPI account
- OpenAI API account

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/tmt-news-collector.git
cd tmt-news-collector
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure API keys:
```bash
cp config_template.py config.py
```
Edit `config.py` and add your API keys:
- `NEWS_API_KEY`: Your NewsAPI key
- `OPENAI_API_KEY`: Your OpenAI API key

### Usage

#### Generate Daily Brief
```bash
python main.py
```

#### Generate Interview Package
```python
from main import IBDMarketAnalyst

analyzer = IBDMarketAnalyst()
package_path = analyzer.generate_interview_package()
print(f"Interview package saved to: {package_path}")
```

## Project Structure

```
tmt-news-collector/
├── main.py                 # Main application
├── config.py              # Configuration (API keys)
├── config_template.py     # Template for configuration
├── interview_generator.py # Interview package generator
├── requirements.txt       # Python dependencies
├── daily_briefs/         # Generated PDF briefs
├── interview_packages/    # Generated interview packages
└── README.md            # This file
```

## Security Notes

- Never commit `config.py` with real API keys
- Use `config_template.py` as a template
- Add `config.py` to your `.gitignore`

## License

Private repository - All rights reserved

## Contributing

This is a private repository for internal use only. 