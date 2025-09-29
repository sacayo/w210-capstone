"""Main research agent that coordinates the entire research process."""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from .base_agent import BaseAgent
from .data_agent import DataCollectionAgent
from .analysis_agent import AnalysisAgent
from ..data_collection import MunicipalDataCollector
from ..analysis import LegalCodeAnalyzer

logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    """Main research agent that coordinates the entire research process."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the research agent.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__("ResearchAgent", config)
        
        self.capabilities = [
            "conduct_research",
            "coordinate_analysis", 
            "generate_report",
            "manage_workflow"
        ]
        
        # Initialize sub-agents
        self.data_agent = DataCollectionAgent(config)
        self.analysis_agent = AnalysisAgent(config)
        
        # Initialize core components
        self.data_collector = MunicipalDataCollector(
            data_dir=self.config.get('data_dir', 'data')
        )
        self.analyzer = LegalCodeAnalyzer()
        
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a research task.
        
        Args:
            task: Task specification
            
        Returns:
            Task execution results
        """
        task_type = task.get('type')
        
        try:
            if task_type == "conduct_research":
                result = self._conduct_full_research(task)
            elif task_type == "coordinate_analysis":
                result = self._coordinate_analysis(task)
            elif task_type == "generate_report":
                result = self._generate_report(task)
            elif task_type == "manage_workflow":
                result = self._manage_workflow(task)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            self.log_execution(task, result, "completed")
            return result
            
        except Exception as e:
            error_result = {
                'error': str(e),
                'task_type': task_type,
                'timestamp': datetime.now().isoformat()
            }
            self.log_execution(task, error_result, "failed")
            raise
    
    def _conduct_full_research(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Conduct a complete research workflow.
        
        Args:
            task: Research task specification
            
        Returns:
            Complete research results
        """
        self.logger.info("Starting full research workflow")
        
        # Step 1: Data Collection
        collection_task = {
            'type': 'collect_sample_data',
            'parameters': task.get('collection_parameters', {})
        }
        
        collection_result = self.data_agent.execute_task(collection_task)
        
        if collection_result.get('status') != 'success':
            raise Exception(f"Data collection failed: {collection_result.get('error')}")
        
        # Step 2: Analysis
        analysis_task = {
            'type': 'analyze_legal_codes',
            'data': collection_result['data'],
            'parameters': task.get('analysis_parameters', {})
        }
        
        analysis_result = self.analysis_agent.execute_task(analysis_task)
        
        if analysis_result.get('status') != 'success':
            raise Exception(f"Analysis failed: {analysis_result.get('error')}")
        
        # Step 3: Generate comprehensive report
        report_task = {
            'type': 'generate_comprehensive_report',
            'analysis_results': analysis_result['analysis'],
            'collection_summary': collection_result['summary']
        }
        
        report_result = self._generate_report(report_task)
        
        return {
            'status': 'success',
            'collection_results': collection_result,
            'analysis_results': analysis_result,
            'report': report_result,
            'execution_time': datetime.now().isoformat(),
            'workflow_summary': {
                'codes_collected': collection_result.get('total_codes', 0),
                'states_analyzed': len(collection_result.get('data', {})),
                'analysis_completed': True,
                'report_generated': True
            }
        }
    
    def _coordinate_analysis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate analysis of existing data.
        
        Args:
            task: Analysis coordination task
            
        Returns:
            Analysis coordination results
        """
        return self.analysis_agent.execute_task(task)
    
    def _generate_report(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate research report.
        
        Args:
            task: Report generation task
            
        Returns:
            Report generation results
        """
        self.logger.info("Generating research report")
        
        analysis_results = task.get('analysis_results', {})
        collection_summary = task.get('collection_summary', {})
        
        # Generate text report
        if analysis_results:
            text_report = self.analyzer.generate_analysis_report(analysis_results)
        else:
            text_report = "No analysis results available for report generation."
        
        # Create report structure
        report = {
            'title': 'Municipal Legal Code Research Report',
            'generated_at': datetime.now().isoformat(),
            'executive_summary': self._generate_executive_summary(analysis_results, collection_summary),
            'detailed_analysis': text_report,
            'methodology': self._generate_methodology_section(),
            'findings': self._extract_key_findings(analysis_results),
            'recommendations': self._generate_recommendations(analysis_results)
        }
        
        return {
            'status': 'success',
            'report': report,
            'format': 'structured_text'
        }
    
    def _manage_workflow(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage research workflow execution.
        
        Args:
            task: Workflow management task
            
        Returns:
            Workflow management results
        """
        workflow_type = task.get('workflow_type', 'standard')
        
        if workflow_type == 'standard':
            return self._conduct_full_research(task)
        elif workflow_type == 'analysis_only':
            return self._coordinate_analysis(task)
        else:
            raise ValueError(f"Unknown workflow type: {workflow_type}")
    
    def _generate_executive_summary(self, analysis_results: Dict[str, Any], 
                                  collection_summary: Dict[str, Any]) -> str:
        """Generate executive summary of research."""
        
        if not analysis_results:
            return "Executive summary not available due to insufficient analysis results."
        
        overview = analysis_results.get('overview', {})
        total_codes = overview.get('total_codes', 0)
        total_states = overview.get('total_states', 0)
        
        summary = f"""
        This research analyzed {total_codes} municipal legal code ordinances across {total_states} states 
        (California, Georgia, Florida, and Texas) to conduct exploratory data analysis of municipal 
        legal frameworks.
        
        Key findings include analysis of text complexity, common legal themes, and comparative 
        differences between state approaches to municipal regulation.
        """
        
        return summary.strip()
    
    def _generate_methodology_section(self) -> str:
        """Generate methodology section for the report."""
        
        methodology = """
        METHODOLOGY
        
        This research employed an end-to-end agentic research system to collect and analyze 
        municipal legal code ordinances from four U.S. states:
        
        1. Data Collection: Automated collection of legal codes from municipal websites
           and legal databases for California, Georgia, Florida, and Texas
           
        2. Text Analysis: Natural language processing techniques to extract keywords,
           analyze readability, and identify common themes
           
        3. Comparative Analysis: Cross-state comparison of legal code characteristics
           including length, complexity, and topic distribution
           
        4. Visualization: Generation of charts and graphs to illustrate findings
        
        The system employed web scraping, text mining, and statistical analysis 
        techniques to process and analyze the collected legal documents.
        """
        
        return methodology.strip()
    
    def _extract_key_findings(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Extract key findings from analysis results."""
        
        findings = []
        
        if 'overview' in analysis_results:
            overview = analysis_results['overview']
            findings.append(f"Collected {overview.get('total_codes', 0)} legal codes from {overview.get('total_states', 0)} states")
        
        if 'text_statistics' in analysis_results:
            stats = analysis_results['text_statistics']['word_count_stats']
            findings.append(f"Average legal code length: {stats['mean']:.0f} words")
            findings.append(f"Total corpus size: {stats['total']:,} words")
        
        if 'topic_analysis' in analysis_results:
            topics = analysis_results['topic_analysis']['topic_frequencies']
            if topics:
                top_topic = max(topics.items(), key=lambda x: x[1])
                findings.append(f"Most common topic area: {top_topic[0].replace('_', ' ').title()}")
        
        if 'readability_analysis' in analysis_results:
            readability = analysis_results['readability_analysis']
            if 'average_score' in readability:
                findings.append(f"Average readability score: {readability['average_score']:.1f} ({readability['interpretation']})")
        
        return findings
    
    def _generate_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis results."""
        
        recommendations = [
            "Standardize legal code formatting across jurisdictions for improved accessibility",
            "Consider readability improvements for codes with low readability scores",
            "Develop cross-referencing systems for related ordinances across jurisdictions",
            "Implement regular reviews to ensure code consistency and clarity"
        ]
        
        # Add specific recommendations based on analysis
        if 'readability_analysis' in analysis_results:
            readability = analysis_results['readability_analysis']
            if readability.get('average_score', 0) < 50:
                recommendations.append("Priority focus on improving readability of legal codes for public accessibility")
        
        return recommendations
    
    def get_research_status(self) -> Dict[str, Any]:
        """
        Get current status of research operations.
        
        Returns:
            Status dictionary
        """
        return {
            'research_agent': self.get_execution_summary(),
            'data_agent': self.data_agent.get_execution_summary(),
            'analysis_agent': self.analysis_agent.get_execution_summary(),
            'system_status': 'operational',
            'last_check': datetime.now().isoformat()
        }