"""Main municipal data collector that coordinates all state collectors."""

from typing import List, Dict, Optional
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from datetime import datetime

from .base_collector import LegalCode
from .california_collector import CaliforniaCollector
from .texas_collector import TexasCollector  
from .georgia_collector import GeorgiaCollector
from .florida_collector import FloridaCollector

logger = logging.getLogger(__name__)


class MunicipalDataCollector:
    """Main collector for municipal legal codes across multiple states."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the municipal data collector.
        
        Args:
            data_dir: Directory to save collected data
        """
        self.data_dir = data_dir
        self.collectors = {
            'California': CaliforniaCollector(),
            'Texas': TexasCollector(),
            'Georgia': GeorgiaCollector(), 
            'Florida': FloridaCollector()
        }
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
    def get_available_states(self) -> List[str]:
        """Get list of available states for data collection."""
        return list(self.collectors.keys())
        
    def get_jurisdictions_for_state(self, state: str) -> List[str]:
        """Get list of jurisdictions for a specific state."""
        if state not in self.collectors:
            raise ValueError(f"State {state} not supported. Available: {list(self.collectors.keys())}")
            
        return self.collectors[state].get_jurisdictions()
        
    def collect_sample_data(self, max_jurisdictions_per_state: int = 3, 
                          max_codes_per_jurisdiction: int = 5) -> Dict[str, List[LegalCode]]:
        """
        Collect sample data from all states for exploratory analysis.
        
        Args:
            max_jurisdictions_per_state: Maximum jurisdictions to collect per state
            max_codes_per_jurisdiction: Maximum codes to collect per jurisdiction
            
        Returns:
            Dictionary mapping state names to lists of legal codes
        """
        all_codes = {}
        
        for state_name, collector in self.collectors.items():
            logger.info(f"Collecting sample data for {state_name}")
            
            try:
                # Get available jurisdictions
                jurisdictions = collector.get_jurisdictions()[:max_jurisdictions_per_state]
                state_codes = []
                
                for jurisdiction in jurisdictions:
                    logger.info(f"Collecting from {jurisdiction}, {state_name}")
                    
                    try:
                        # Get available code sections
                        sections = collector.get_code_sections(jurisdiction)[:max_codes_per_jurisdiction]
                        
                        for section in sections:
                            try:
                                code = collector.collect_code(jurisdiction, section['id'])
                                state_codes.append(code)
                                logger.info(f"Collected: {jurisdiction} - {section['title']}")
                                
                            except Exception as e:
                                logger.warning(f"Failed to collect {section['id']} from {jurisdiction}: {e}")
                                continue
                                
                    except Exception as e:
                        logger.warning(f"Failed to get sections for {jurisdiction}: {e}")
                        continue
                        
                all_codes[state_name] = state_codes
                logger.info(f"Collected {len(state_codes)} codes for {state_name}")
                
            except Exception as e:
                logger.error(f"Failed to collect data for {state_name}: {e}")
                all_codes[state_name] = []
                
        return all_codes
        
    def collect_jurisdiction_data(self, state: str, jurisdiction: str, 
                                max_codes: Optional[int] = None) -> List[LegalCode]:
        """
        Collect all available codes for a specific jurisdiction.
        
        Args:
            state: State name
            jurisdiction: Jurisdiction name 
            max_codes: Maximum number of codes to collect (None for all)
            
        Returns:
            List of collected legal codes
        """
        if state not in self.collectors:
            raise ValueError(f"State {state} not supported")
            
        collector = self.collectors[state]
        sections = collector.get_code_sections(jurisdiction)
        
        if max_codes:
            sections = sections[:max_codes]
            
        codes = []
        for section in sections:
            try:
                code = collector.collect_code(jurisdiction, section['id'])
                codes.append(code)
                
            except Exception as e:
                logger.warning(f"Failed to collect {section['id']}: {e}")
                continue
                
        return codes
        
    def save_collected_data(self, codes_by_state: Dict[str, List[LegalCode]], 
                          filename_prefix: str = "municipal_codes") -> Dict[str, str]:
        """
        Save collected legal codes to files.
        
        Args:
            codes_by_state: Dictionary mapping states to lists of legal codes
            filename_prefix: Prefix for output files
            
        Returns:
            Dictionary mapping file types to file paths
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Flatten all codes into a single list
        all_codes = []
        for state_codes in codes_by_state.values():
            all_codes.extend(state_codes)
            
        # Save as JSON
        json_path = os.path.join(self.data_dir, f"{filename_prefix}_{timestamp}.json")
        if all_codes:
            self.collectors['California'].save_codes_to_file(all_codes, json_path)
        
        # Create DataFrame and save as CSV
        csv_path = os.path.join(self.data_dir, f"{filename_prefix}_{timestamp}.csv")
        if all_codes:
            df_data = []
            for code in all_codes:
                df_data.append({
                    'state': code.state,
                    'jurisdiction': code.jurisdiction,
                    'code_section': code.code_section,
                    'title': code.title,
                    'content': code.content[:1000] + '...' if len(code.content) > 1000 else code.content,
                    'url': code.url,
                    'last_updated': code.last_updated,
                    'effective_date': code.effective_date,
                    'word_count': code.metadata.get('word_count', 0) if code.metadata else 0,
                    'character_count': code.metadata.get('character_count', 0) if code.metadata else 0
                })
                
            df = pd.DataFrame(df_data)
            df.to_csv(csv_path, index=False)
        
        # Save summary statistics
        summary_path = os.path.join(self.data_dir, f"{filename_prefix}_summary_{timestamp}.txt")
        with open(summary_path, 'w') as f:
            f.write(f"Municipal Legal Code Collection Summary\n")
            f.write(f"Generated: {datetime.now()}\n\n")
            
            for state, codes in codes_by_state.items():
                f.write(f"{state}: {len(codes)} codes collected\n")
                
                if codes:
                    jurisdictions = set(code.jurisdiction for code in codes)
                    f.write(f"  Jurisdictions: {', '.join(jurisdictions)}\n")
                    
                    total_words = sum(code.metadata.get('word_count', 0) for code in codes if code.metadata)
                    f.write(f"  Total words: {total_words:,}\n")
                    
                f.write("\n")
                
            f.write(f"Total codes collected: {len(all_codes)}\n")
            
        return {
            'json': json_path,
            'csv': csv_path, 
            'summary': summary_path
        }
        
    def get_collection_summary(self, codes_by_state: Dict[str, List[LegalCode]]) -> Dict:
        """
        Generate summary statistics for collected data.
        
        Args:
            codes_by_state: Dictionary mapping states to lists of legal codes
            
        Returns:
            Dictionary containing summary statistics
        """
        summary = {
            'total_codes': 0,
            'states': {},
            'total_words': 0,
            'total_characters': 0,
            'jurisdictions': set()
        }
        
        for state, codes in codes_by_state.items():
            state_words = 0
            state_chars = 0
            state_jurisdictions = set()
            
            for code in codes:
                if code.metadata:
                    state_words += code.metadata.get('word_count', 0)
                    state_chars += code.metadata.get('character_count', 0)
                state_jurisdictions.add(code.jurisdiction)
                summary['jurisdictions'].add(f"{code.jurisdiction}, {code.state}")
                
            summary['states'][state] = {
                'code_count': len(codes),
                'word_count': state_words,
                'character_count': state_chars,
                'jurisdiction_count': len(state_jurisdictions),
                'jurisdictions': list(state_jurisdictions)
            }
            
            summary['total_codes'] += len(codes)
            summary['total_words'] += state_words
            summary['total_characters'] += state_chars
            
        summary['jurisdiction_count'] = len(summary['jurisdictions'])
        summary['jurisdictions'] = list(summary['jurisdictions'])
        
        return summary