"""Data collection agent for the agentic research system."""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from .base_agent import BaseAgent
from ..data_collection import MunicipalDataCollector

logger = logging.getLogger(__name__)


class DataCollectionAgent(BaseAgent):
    """Agent specialized in data collection tasks."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the data collection agent.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__("DataCollectionAgent", config)
        
        self.capabilities = [
            "collect_sample_data",
            "collect_jurisdiction_data", 
            "collect_state_data",
            "validate_data",
            "save_data"
        ]
        
        self.collector = MunicipalDataCollector(
            data_dir=self.config.get('data_dir', 'data')
        )
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a data collection task.
        
        Args:
            task: Task specification
            
        Returns:
            Task execution results
        """
        task_type = task.get('type')
        
        try:
            if task_type == "collect_sample_data":
                result = self._collect_sample_data(task)
            elif task_type == "collect_jurisdiction_data":
                result = self._collect_jurisdiction_data(task)
            elif task_type == "collect_state_data":
                result = self._collect_state_data(task)
            elif task_type == "validate_data":
                result = self._validate_data(task)
            elif task_type == "save_data":
                result = self._save_data(task)
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
    
    def _collect_sample_data(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect sample data from all states.
        
        Args:
            task: Sample data collection task
            
        Returns:
            Collection results
        """
        self.logger.info("Collecting sample data from all states")
        
        parameters = task.get('parameters', {})
        max_jurisdictions = parameters.get('max_jurisdictions_per_state', 2)
        max_codes = parameters.get('max_codes_per_jurisdiction', 3)
        
        try:
            # Collect sample data
            codes_by_state = self.collector.collect_sample_data(
                max_jurisdictions_per_state=max_jurisdictions,
                max_codes_per_jurisdiction=max_codes
            )
            
            # Generate summary
            summary = self.collector.get_collection_summary(codes_by_state)
            
            # Save data if requested
            if parameters.get('save_data', True):
                file_paths = self.collector.save_collected_data(
                    codes_by_state, 
                    filename_prefix=parameters.get('filename_prefix', 'sample_data')
                )
            else:
                file_paths = {}
            
            return {
                'status': 'success',
                'data': codes_by_state,
                'summary': summary,
                'file_paths': file_paths,
                'total_codes': summary['total_codes'],
                'collection_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Sample data collection failed: {e}")
            raise
    
    def _collect_jurisdiction_data(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect data for a specific jurisdiction.
        
        Args:
            task: Jurisdiction data collection task
            
        Returns:
            Collection results
        """
        state = task.get('state')
        jurisdiction = task.get('jurisdiction')
        max_codes = task.get('max_codes')
        
        if not state or not jurisdiction:
            raise ValueError("State and jurisdiction must be specified")
        
        self.logger.info(f"Collecting data for {jurisdiction}, {state}")
        
        try:
            codes = self.collector.collect_jurisdiction_data(
                state, jurisdiction, max_codes
            )
            
            return {
                'status': 'success',
                'state': state,
                'jurisdiction': jurisdiction,
                'codes': codes,
                'code_count': len(codes),
                'collection_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Jurisdiction data collection failed: {e}")
            raise
    
    def _collect_state_data(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect data for all jurisdictions in a state.
        
        Args:
            task: State data collection task
            
        Returns:
            Collection results
        """
        state = task.get('state')
        max_jurisdictions = task.get('max_jurisdictions', 5)
        max_codes_per_jurisdiction = task.get('max_codes_per_jurisdiction', 10)
        
        if not state:
            raise ValueError("State must be specified")
        
        self.logger.info(f"Collecting data for {state}")
        
        try:
            # Get available jurisdictions
            jurisdictions = self.collector.get_jurisdictions_for_state(state)
            jurisdictions = jurisdictions[:max_jurisdictions]
            
            state_codes = []
            for jurisdiction in jurisdictions:
                try:
                    codes = self.collector.collect_jurisdiction_data(
                        state, jurisdiction, max_codes_per_jurisdiction
                    )
                    state_codes.extend(codes)
                except Exception as e:
                    self.logger.warning(f"Failed to collect from {jurisdiction}: {e}")
                    continue
            
            return {
                'status': 'success',
                'state': state,
                'jurisdictions_processed': len(jurisdictions),
                'codes': state_codes,
                'total_codes': len(state_codes),
                'collection_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"State data collection failed: {e}")
            raise
    
    def _validate_data(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate collected data quality.
        
        Args:
            task: Data validation task
            
        Returns:
            Validation results
        """
        data = task.get('data')
        
        if not data:
            raise ValueError("No data provided for validation")
        
        validation_results = {
            'total_codes': 0,
            'valid_codes': 0,
            'invalid_codes': 0,
            'validation_errors': [],
            'quality_metrics': {}
        }
        
        # Flatten codes if organized by state
        all_codes = []
        if isinstance(data, dict):
            for state_codes in data.values():
                all_codes.extend(state_codes)
        else:
            all_codes = data
        
        validation_results['total_codes'] = len(all_codes)
        
        for i, code in enumerate(all_codes):
            try:
                # Validate required fields
                if not code.jurisdiction or not code.state:
                    validation_results['validation_errors'].append(
                        f"Code {i}: Missing jurisdiction or state"
                    )
                    continue
                
                if not code.title or not code.content:
                    validation_results['validation_errors'].append(
                        f"Code {i}: Missing title or content"
                    )
                    continue
                
                # Check content quality
                if len(code.content.split()) < 10:
                    validation_results['validation_errors'].append(
                        f"Code {i}: Content too short (less than 10 words)"
                    )
                    continue
                
                validation_results['valid_codes'] += 1
                
            except Exception as e:
                validation_results['validation_errors'].append(
                    f"Code {i}: Validation error - {str(e)}"
                )
        
        validation_results['invalid_codes'] = (
            validation_results['total_codes'] - validation_results['valid_codes']
        )
        
        # Calculate quality metrics
        if validation_results['total_codes'] > 0:
            validation_results['quality_metrics'] = {
                'validity_rate': validation_results['valid_codes'] / validation_results['total_codes'],
                'error_rate': validation_results['invalid_codes'] / validation_results['total_codes'],
                'avg_content_length': sum(len(code.content.split()) for code in all_codes) / len(all_codes)
            }
        
        return {
            'status': 'success',
            'validation_results': validation_results,
            'validation_time': datetime.now().isoformat()
        }
    
    def _save_data(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save collected data to files.
        
        Args:
            task: Data saving task
            
        Returns:
            Save results
        """
        data = task.get('data')
        filename_prefix = task.get('filename_prefix', 'municipal_codes')
        
        if not data:
            raise ValueError("No data provided for saving")
        
        try:
            file_paths = self.collector.save_collected_data(data, filename_prefix)
            
            return {
                'status': 'success',
                'file_paths': file_paths,
                'save_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Data saving failed: {e}")
            raise
    
    def get_available_states(self) -> List[str]:
        """Get list of available states for data collection."""
        return self.collector.get_available_states()
    
    def get_available_jurisdictions(self, state: str) -> List[str]:
        """Get list of available jurisdictions for a state."""
        return self.collector.get_jurisdictions_for_state(state)