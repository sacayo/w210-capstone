"""Basic functionality tests for the municipal research system."""

import unittest
import tempfile
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from municipal_research.agents import ResearchAgent
from municipal_research.data_collection import MunicipalDataCollector
from municipal_research.analysis import LegalCodeAnalyzer
from municipal_research.utils import ConfigManager
from municipal_research.data_collection.base_collector import LegalCode


class TestBasicFunctionality(unittest.TestCase):
    """Test basic functionality of the municipal research system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager()
        
    def test_config_manager_initialization(self):
        """Test configuration manager initialization."""
        config = ConfigManager()
        self.assertIsInstance(config.config, dict)
        self.assertIn('data_collection', config.config)
        self.assertIn('analysis', config.config)
        
    def test_legal_code_creation(self):
        """Test LegalCode dataclass creation."""
        code = LegalCode(
            jurisdiction="San Francisco",
            state="California",
            code_section="zoning_001",
            title="Zoning Ordinance",
            content="This ordinance establishes zoning regulations...",
            url="https://example.com/code/zoning_001"
        )
        
        self.assertEqual(code.jurisdiction, "San Francisco")
        self.assertEqual(code.state, "California")
        self.assertEqual(code.code_section, "zoning_001")
        self.assertIsInstance(code.content, str)
        
    def test_municipal_data_collector_initialization(self):
        """Test data collector initialization."""
        collector = MunicipalDataCollector(data_dir=self.temp_dir)
        self.assertEqual(collector.data_dir, self.temp_dir)
        self.assertIn('California', collector.collectors)
        self.assertIn('Texas', collector.collectors)
        self.assertIn('Georgia', collector.collectors)
        self.assertIn('Florida', collector.collectors)
        
    def test_legal_code_analyzer_initialization(self):
        """Test analyzer initialization.""" 
        analyzer = LegalCodeAnalyzer()
        self.assertIsNotNone(analyzer.text_analyzer)
        self.assertIsNotNone(analyzer.visualizer)
        
    def test_research_agent_initialization(self):
        """Test research agent initialization."""
        config = {'data_dir': self.temp_dir}
        agent = ResearchAgent(config)
        
        self.assertEqual(agent.agent_name, "ResearchAgent")
        self.assertIn("conduct_research", agent.capabilities)
        self.assertIsNotNone(agent.data_agent)
        self.assertIsNotNone(agent.analysis_agent)
        
    def test_sample_analysis_with_mock_data(self):
        """Test analysis with sample mock data."""
        # Create mock legal codes
        mock_codes = {
            'California': [
                LegalCode(
                    jurisdiction="Los Angeles",
                    state="California", 
                    code_section="zoning_001",
                    title="Residential Zoning Requirements",
                    content="All residential buildings must comply with setback requirements. " * 20,
                    url="https://example.com/la/zoning_001",
                    metadata={'word_count': 200, 'character_count': 1000}
                ),
                LegalCode(
                    jurisdiction="San Francisco",
                    state="California",
                    code_section="building_002", 
                    title="Building Safety Standards",
                    content="Building safety standards ensure public welfare and protection. " * 15,
                    url="https://example.com/sf/building_002",
                    metadata={'word_count': 150, 'character_count': 750}
                )
            ],
            'Texas': [
                LegalCode(
                    jurisdiction="Houston",
                    state="Texas",
                    code_section="business_003",
                    title="Business License Requirements", 
                    content="All businesses must obtain proper licensing before operation. " * 25,
                    url="https://example.com/houston/business_003",
                    metadata={'word_count': 250, 'character_count': 1250}
                )
            ]
        }
        
        # Test analysis
        analyzer = LegalCodeAnalyzer()
        results = analyzer.analyze_collection(mock_codes)
        
        # Verify analysis results
        self.assertIn('overview', results)
        self.assertIn('text_statistics', results)
        self.assertIn('content_analysis', results)
        
        # Check overview
        overview = results['overview']
        self.assertEqual(overview['total_codes'], 3)
        self.assertEqual(overview['total_states'], 2)
        
        # Check text statistics
        text_stats = results['text_statistics']['word_count_stats']
        self.assertGreater(text_stats['total'], 0)
        self.assertGreater(text_stats['mean'], 0)
        
    def test_report_generation(self):
        """Test report generation functionality."""
        analyzer = LegalCodeAnalyzer()
        
        # Mock analysis results
        mock_analysis = {
            'overview': {
                'total_codes': 10,
                'total_states': 4,
                'total_jurisdictions': 8
            },
            'text_statistics': {
                'word_count_stats': {
                    'mean': 500,
                    'total': 5000,
                    'max': 1000,
                    'min': 100
                }
            }
        }
        
        report = analyzer.generate_analysis_report(mock_analysis)
        
        self.assertIsInstance(report, str)
        self.assertIn('MUNICIPAL LEGAL CODE ANALYSIS REPORT', report)
        self.assertIn('Total Legal Codes Analyzed: 10', report)
        self.assertIn('States Covered: 4', report)
        
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temporary directory
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


class TestConfigManager(unittest.TestCase):
    """Test configuration manager functionality."""
    
    def test_default_config(self):
        """Test default configuration loading."""
        config = ConfigManager()
        
        self.assertIn('data_collection', config.config)
        self.assertIn('analysis', config.config)
        self.assertIn('output', config.config)
        
        # Test getting values
        rate_limit = config.get('data_collection.rate_limit')
        self.assertIsInstance(rate_limit, (int, float))
        
        # Test setting values
        config.set('data_collection.rate_limit', 2.0)
        self.assertEqual(config.get('data_collection.rate_limit'), 2.0)
        
    def test_config_validation(self):
        """Test configuration validation."""
        config = ConfigManager()
        self.assertTrue(config.validate_config())
        
        # Test invalid configuration
        config.config = {'incomplete': 'config'}
        self.assertFalse(config.validate_config())


if __name__ == '__main__':
    unittest.main()