"""Analysis agent for the agentic research system."""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from .base_agent import BaseAgent
from ..analysis import LegalCodeAnalyzer, LegalCodeVisualizer

logger = logging.getLogger(__name__)


class AnalysisAgent(BaseAgent):
    """Agent specialized in data analysis tasks."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the analysis agent.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__("AnalysisAgent", config)
        
        self.capabilities = [
            "analyze_legal_codes",
            "generate_visualizations",
            "compare_jurisdictions",
            "analyze_topics",
            "analyze_readability"
        ]
        
        self.analyzer = LegalCodeAnalyzer()
        self.visualizer = LegalCodeVisualizer()
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an analysis task.
        
        Args:
            task: Task specification
            
        Returns:
            Task execution results
        """
        task_type = task.get('type')
        
        try:
            if task_type == "analyze_legal_codes":
                result = self._analyze_legal_codes(task)
            elif task_type == "generate_visualizations":
                result = self._generate_visualizations(task)
            elif task_type == "compare_jurisdictions":
                result = self._compare_jurisdictions(task)
            elif task_type == "analyze_topics":
                result = self._analyze_topics(task)
            elif task_type == "analyze_readability":
                result = self._analyze_readability(task)
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
    
    def _analyze_legal_codes(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of legal codes.
        
        Args:
            task: Analysis task specification
            
        Returns:
            Analysis results
        """
        self.logger.info("Starting comprehensive legal code analysis")
        
        data = task.get('data')
        parameters = task.get('parameters', {})
        
        if not data:
            raise ValueError("No data provided for analysis")
        
        try:
            # Perform comprehensive analysis
            analysis_results = self.analyzer.analyze_collection(data)
            
            # Generate visualizations if requested
            generate_viz = parameters.get('generate_visualizations', True)
            visualization_paths = {}
            
            if generate_viz:
                viz_dir = parameters.get('visualization_dir', 'visualizations')
                try:
                    visualization_paths = self.visualizer.create_dashboard(
                        analysis_results, viz_dir
                    )
                except Exception as e:
                    self.logger.warning(f"Visualization generation failed: {e}")
            
            # Generate text report
            text_report = self.analyzer.generate_analysis_report(analysis_results)
            
            return {
                'status': 'success',
                'analysis': analysis_results,
                'text_report': text_report,
                'visualizations': visualization_paths,
                'analysis_time': datetime.now().isoformat(),
                'parameters_used': parameters
            }
            
        except Exception as e:
            self.logger.error(f"Legal code analysis failed: {e}")
            raise
    
    def _generate_visualizations(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate visualizations for analysis results.
        
        Args:
            task: Visualization task specification
            
        Returns:
            Visualization results
        """
        self.logger.info("Generating visualizations")
        
        analysis_results = task.get('analysis_results')
        save_dir = task.get('save_dir', 'visualizations')
        
        if not analysis_results:
            raise ValueError("No analysis results provided for visualization")
        
        try:
            visualization_paths = self.visualizer.create_dashboard(
                analysis_results, save_dir
            )
            
            return {
                'status': 'success',
                'visualization_paths': visualization_paths,
                'save_directory': save_dir,
                'generation_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Visualization generation failed: {e}")
            raise
    
    def _compare_jurisdictions(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare legal codes between jurisdictions.
        
        Args:
            task: Comparison task specification
            
        Returns:
            Comparison results
        """
        self.logger.info("Comparing jurisdictions")
        
        data = task.get('data')
        jurisdictions = task.get('jurisdictions', [])
        
        if not data or not jurisdictions:
            raise ValueError("Data and jurisdictions list required for comparison")
        
        try:
            # Filter data for specified jurisdictions
            filtered_data = {}
            for state, codes in data.items():
                state_codes = [
                    code for code in codes 
                    if code.jurisdiction in jurisdictions
                ]
                if state_codes:
                    filtered_data[state] = state_codes
            
            if not filtered_data:
                raise ValueError("No codes found for specified jurisdictions")
            
            # Analyze filtered data
            comparison_results = self.analyzer.analyze_collection(filtered_data)
            
            # Add specific comparison metrics
            comparison_metrics = self._calculate_comparison_metrics(filtered_data, jurisdictions)
            comparison_results['jurisdiction_comparison'] = comparison_metrics
            
            return {
                'status': 'success',
                'comparison_results': comparison_results,
                'jurisdictions_compared': jurisdictions,
                'comparison_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Jurisdiction comparison failed: {e}")
            raise
    
    def _analyze_topics(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform topic analysis on legal codes.
        
        Args:
            task: Topic analysis task specification
            
        Returns:
            Topic analysis results
        """
        self.logger.info("Performing topic analysis")
        
        data = task.get('data')
        custom_topics = task.get('custom_topics', {})
        
        if not data:
            raise ValueError("No data provided for topic analysis")
        
        try:
            # Flatten codes for analysis
            all_codes = []
            for state_codes in data.values():
                all_codes.extend(state_codes)
            
            # Perform topic analysis
            topic_results = self.analyzer._analyze_topics(all_codes)
            
            # Add custom topic analysis if provided
            if custom_topics:
                custom_results = self._analyze_custom_topics(all_codes, custom_topics)
                topic_results['custom_topics'] = custom_results
            
            return {
                'status': 'success',
                'topic_analysis': topic_results,
                'total_codes_analyzed': len(all_codes),
                'analysis_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Topic analysis failed: {e}")
            raise
    
    def _analyze_readability(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform readability analysis on legal codes.
        
        Args:
            task: Readability analysis task specification
            
        Returns:
            Readability analysis results
        """
        self.logger.info("Performing readability analysis")
        
        data = task.get('data')
        
        if not data:
            raise ValueError("No data provided for readability analysis")
        
        try:
            # Flatten codes for analysis
            all_codes = []
            for state_codes in data.values():
                all_codes.extend(state_codes)
            
            # Perform readability analysis
            readability_results = self.analyzer._analyze_readability(all_codes)
            
            # Add state-by-state breakdown
            state_readability = {}
            for state, codes in data.items():
                if codes:
                    state_avg = self.analyzer._calculate_avg_readability(codes)
                    state_readability[state] = {
                        'average_score': state_avg,
                        'code_count': len(codes),
                        'interpretation': self.analyzer._interpret_readability_score(state_avg)
                    }
            
            readability_results['by_state'] = state_readability
            
            return {
                'status': 'success',
                'readability_analysis': readability_results,
                'total_codes_analyzed': len(all_codes),
                'analysis_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Readability analysis failed: {e}")
            raise
    
    def _calculate_comparison_metrics(self, data: Dict[str, List], 
                                    jurisdictions: List[str]) -> Dict[str, Any]:
        """
        Calculate specific comparison metrics between jurisdictions.
        
        Args:
            data: Legal codes data organized by state
            jurisdictions: List of jurisdictions to compare
            
        Returns:
            Comparison metrics
        """
        jurisdiction_metrics = {}
        
        for jurisdiction in jurisdictions:
            # Find codes for this jurisdiction
            jurisdiction_codes = []
            for state_codes in data.values():
                jurisdiction_codes.extend([
                    code for code in state_codes 
                    if code.jurisdiction == jurisdiction
                ])
            
            if jurisdiction_codes:
                # Calculate metrics
                word_counts = [
                    code.metadata.get('word_count', len(code.content.split()))
                    for code in jurisdiction_codes
                ]
                
                jurisdiction_metrics[jurisdiction] = {
                    'code_count': len(jurisdiction_codes),
                    'avg_word_count': sum(word_counts) / len(word_counts),
                    'total_word_count': sum(word_counts),
                    'avg_readability': self.analyzer._calculate_avg_readability(jurisdiction_codes)
                }
        
        return jurisdiction_metrics
    
    def _analyze_custom_topics(self, codes: List, custom_topics: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Analyze custom topics defined by user.
        
        Args:
            codes: List of legal codes
            custom_topics: Dictionary mapping topic names to keyword lists
            
        Returns:
            Custom topic analysis results
        """
        topic_counts = {}
        codes_by_topic = {}
        
        for topic, keywords in custom_topics.items():
            topic_counts[topic] = 0
            codes_by_topic[topic] = []
            
            for code in codes:
                content_lower = code.content.lower()
                title_lower = code.title.lower()
                
                # Count keyword matches
                matches = sum(
                    content_lower.count(keyword.lower()) + title_lower.count(keyword.lower()) * 2
                    for keyword in keywords
                )
                
                if matches > 0:
                    topic_counts[topic] += matches
                    codes_by_topic[topic].append({
                        'jurisdiction': code.jurisdiction,
                        'state': code.state,
                        'title': code.title,
                        'matches': matches
                    })
        
        return {
            'topic_frequencies': topic_counts,
            'codes_by_topic': codes_by_topic,
            'topic_distribution': {
                topic: len(codes_list) for topic, codes_list in codes_by_topic.items()
            }
        }