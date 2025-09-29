"""Base class for municipal legal code data collectors."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import time
import logging

logger = logging.getLogger(__name__)


@dataclass
class LegalCode:
    """Data structure for legal code ordinances."""
    
    jurisdiction: str
    state: str
    code_section: str
    title: str
    content: str
    url: str
    last_updated: Optional[str] = None
    effective_date: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseCollector(ABC):
    """Abstract base class for municipal legal code collectors."""
    
    def __init__(self, state: str, base_url: str, rate_limit: float = 1.0):
        """
        Initialize the collector.
        
        Args:
            state: State name (e.g., 'California', 'Texas')
            base_url: Base URL for the legal code website
            rate_limit: Minimum delay between requests in seconds
        """
        self.state = state
        self.base_url = base_url
        self.rate_limit = rate_limit
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Municipal Research Bot 1.0 (Academic Research)'
        })
        
    def _make_request(self, url: str, **kwargs) -> requests.Response:
        """Make a rate-limited HTTP request."""
        time.sleep(self.rate_limit)
        try:
            response = self.session.get(url, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            raise
            
    def _parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content with BeautifulSoup."""
        return BeautifulSoup(html, 'html.parser')
        
    @abstractmethod
    def get_jurisdictions(self) -> List[str]:
        """Get list of available jurisdictions for this state."""
        pass
        
    @abstractmethod
    def get_code_sections(self, jurisdiction: str) -> List[Dict[str, str]]:
        """Get list of available code sections for a jurisdiction."""
        pass
        
    @abstractmethod
    def collect_code(self, jurisdiction: str, code_section: str) -> LegalCode:
        """Collect a specific legal code section."""
        pass
        
    def collect_all_codes(self, jurisdiction: str) -> List[LegalCode]:
        """Collect all legal codes for a jurisdiction."""
        codes = []
        sections = self.get_code_sections(jurisdiction)
        
        for section in sections:
            try:
                code = self.collect_code(jurisdiction, section['id'])
                codes.append(code)
                logger.info(f"Collected {jurisdiction} - {section['id']}")
            except Exception as e:
                logger.error(f"Failed to collect {jurisdiction} - {section['id']}: {e}")
                continue
                
        return codes
        
    def save_codes_to_file(self, codes: List[LegalCode], filepath: str) -> None:
        """Save collected codes to a file."""
        import json
        
        data = []
        for code in codes:
            data.append({
                'jurisdiction': code.jurisdiction,
                'state': code.state,
                'code_section': code.code_section,
                'title': code.title,
                'content': code.content,
                'url': code.url,
                'last_updated': code.last_updated,
                'effective_date': code.effective_date,
                'tags': code.tags,
                'metadata': code.metadata
            })
            
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Saved {len(codes)} codes to {filepath}")