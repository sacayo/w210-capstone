# Municipal Legal Code Research System

An end-to-end agentic research system for conducting exploratory data analysis of municipal legal code ordinances across California, Georgia, Florida, and Texas.

## Overview

This system implements an intelligent, automated approach to collecting and analyzing municipal legal codes using agentic AI. It demonstrates how autonomous agents can collaborate to conduct comprehensive legal research, making large-scale municipal law analysis more accessible and efficient.

## Features

### 🤖 Agentic AI System
- **Research Agent**: Coordinates the entire research workflow
- **Data Collection Agent**: Specialized in gathering legal codes from multiple sources
- **Analysis Agent**: Performs comprehensive text and statistical analysis

### 📊 Data Collection
- Automated collection from California, Georgia, Florida, and Texas
- Support for multiple jurisdictions per state
- Configurable collection parameters
- Data validation and quality checks

### 🔍 Analysis Capabilities
- **Text Analysis**: Word counts, readability scores, keyword extraction
- **Topic Analysis**: Identification of common legal themes and subjects
- **Comparative Analysis**: Cross-state comparison of legal code characteristics
- **Readability Assessment**: Public accessibility evaluation using standard metrics

### 📈 Visualizations
- State-by-state comparison charts
- Topic distribution analysis
- Readability score comparisons
- Common terms and keyword clouds
- Comprehensive dashboard generation

### 📄 Reporting
- Automated report generation
- Executive summaries
- Key findings extraction
- Methodology documentation
- Actionable recommendations

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/sacayo/w210-capstone.git
cd w210-capstone
```

2. **Install dependencies:**
```bash
pip install -e .
```

3. **Optional dependencies for enhanced functionality:**
```bash
# For advanced text analysis
python -m nltk.downloader punkt stopwords

# For readability analysis
pip install textstat

# For word clouds
pip install wordcloud
```

## Quick Start

### Command Line Interface

Run the complete research workflow:

```bash
python src/municipal_research/main.py
```

With custom parameters:
```bash
python src/municipal_research/main.py \
  --max-jurisdictions 3 \
  --max-codes 5 \
  --data-dir ./research_data \
  --log-level DEBUG
```

### Jupyter Notebook

Explore the interactive demo:

```bash
jupyter notebook notebooks/exploratory_analysis_demo.ipynb
```

### Python API

```python
from municipal_research.agents import ResearchAgent

# Initialize research agent
agent = ResearchAgent({
    'data_dir': 'data',
    'visualization_dir': 'visualizations'
})

# Define research task
task = {
    'type': 'conduct_research',
    'collection_parameters': {
        'max_jurisdictions_per_state': 2,
        'max_codes_per_jurisdiction': 3
    }
}

# Execute research
results = agent.execute_task(task)
```

## Configuration

The system uses JSON configuration files for customization:

```json
{
  "data_collection": {
    "rate_limit": 1.0,
    "max_jurisdictions_per_state": 3,
    "max_codes_per_jurisdiction": 5
  },
  "analysis": {
    "generate_visualizations": true,
    "calculate_readability": true
  },
  "output": {
    "data_dir": "data",
    "visualization_dir": "visualizations"
  }
}
```

## Architecture

### Agentic Framework
```
ResearchAgent (Coordinator)
├── DataCollectionAgent
│   ├── CaliforniaCollector
│   ├── TexasCollector
│   ├── GeorgiaCollector
│   └── FloridaCollector
└── AnalysisAgent
    ├── LegalCodeAnalyzer
    ├── TextAnalyzer
    └── LegalCodeVisualizer
```

### Data Flow
1. **Collection**: Automated scraping of municipal legal codes
2. **Processing**: Text cleaning, validation, and structuring
3. **Analysis**: Statistical analysis, topic modeling, readability assessment
4. **Visualization**: Chart and graph generation
5. **Reporting**: Comprehensive report compilation

## Example Output

### Data Collection Summary
```
Total Legal Codes Analyzed: 48
States Covered: 4
Total Jurisdictions: 8

Codes by State:
  California: 12 codes
  Texas: 12 codes
  Georgia: 12 codes
  Florida: 12 codes
```

### Analysis Results
```
Text Statistics:
  Average words per code: 847
  Total words: 40,656
  Longest code: 2,341 words

Most Common Topics:
  1. Zoning: 156 mentions
  2. Building: 134 mentions
  3. Business: 98 mentions
  4. Public Safety: 87 mentions

Readability Analysis:
  Average score: 42.3 (College level)
  Range: 28.1 - 67.9
```

## Research Applications

### Academic Research
- Comparative municipal law studies
- Legal accessibility research
- Urban planning policy analysis
- Public administration studies

### Policy Analysis
- Cross-jurisdictional policy comparison
- Legal complexity assessment
- Public engagement evaluation
- Regulatory harmonization studies

### Legal Practice
- Municipal law research
- Compliance analysis
- Policy development support
- Legal accessibility improvement

## File Structure

```
w210-capstone/
├── src/municipal_research/          # Main package
│   ├── agents/                      # Agentic AI components
│   ├── data_collection/             # Data collection modules
│   ├── analysis/                    # Analysis and visualization
│   ├── utils/                       # Utilities and configuration
│   └── main.py                      # Command line interface
├── config/                          # Configuration files
├── notebooks/                       # Jupyter notebooks
├── tests/                          # Test suite
├── data/                           # Collected data
├── visualizations/                 # Generated charts
├── reports/                        # Research reports
└── logs/                          # System logs
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Future Enhancements

- [ ] Natural language processing for semantic analysis
- [ ] Machine learning models for classification
- [ ] Real-time data collection and monitoring
- [ ] Web-based dashboard interface
- [ ] API endpoints for external integration
- [ ] Advanced visualization with D3.js
- [ ] Multi-language support
- [ ] Integration with legal databases

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- UC Berkeley W210 Capstone Program
- Municipal legal code databases and APIs
- Open source natural language processing libraries
- Data visualization community

## Contact

For questions, suggestions, or collaboration opportunities, please open an issue or contact the development team.

---

**Note**: This system is designed for research and educational purposes. Always verify legal code information with official sources for any practical or legal applications.
