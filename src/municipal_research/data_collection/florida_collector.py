"""Florida municipal legal code collector."""

from typing import List, Dict
import re
import logging
from .base_collector import BaseCollector, LegalCode

logger = logging.getLogger(__name__)


class FloridaCollector(BaseCollector):
    """Collector for Florida municipal legal codes."""
    
    def __init__(self):
        super().__init__(
            state="Florida",
            base_url="https://library.municode.com/fl",
            rate_limit=1.0
        )
        
    def get_jurisdictions(self) -> List[str]:
        """Get list of Florida cities and counties."""
        try:
            response = self._make_request(self.base_url)
            soup = self._parse_html(response.text)
            
            jurisdictions = []
            jurisdiction_links = soup.find_all('a', href=re.compile(r'/fl/'))
            
            for link in jurisdiction_links:
                jurisdiction_name = link.get_text().strip()
                if jurisdiction_name and len(jurisdiction_name) > 2:
                    jurisdictions.append(jurisdiction_name)
                    
            # Add major Florida cities
            example_jurisdictions = [
                "Jacksonville", "Miami", "Tampa", "Orlando", "St. Petersburg",
                "Hialeah", "Tallahassee", "Fort Lauderdale", "Port St. Lucie", "Cape Coral"
            ]
            
            jurisdictions.extend(example_jurisdictions)
            return list(set(jurisdictions))
            
        except Exception as e:
            logger.error(f"Failed to get Florida jurisdictions: {e}")
            return [
                "Jacksonville", "Miami", "Tampa", "Orlando", "St. Petersburg",
                "Hialeah", "Tallahassee", "Fort Lauderdale", "Port St. Lucie", "Cape Coral"
            ]
    
    def get_code_sections(self, jurisdiction: str) -> List[Dict[str, str]]:
        """Get code sections for a Florida jurisdiction."""
        try:
            jurisdiction_slug = jurisdiction.lower().replace(' ', '_').replace('.', '')
            url = f"{self.base_url}/{jurisdiction_slug}"
            
            response = self._make_request(url)
            soup = self._parse_html(response.text)
            
            sections = []
            section_links = soup.find_all('a', href=re.compile(r'chapter|part|section'))
            
            for link in section_links:
                section_text = link.get_text().strip()
                href = link.get('href', '')
                
                if section_text and href:
                    sections.append({
                        'id': href.split('/')[-1],
                        'title': section_text,
                        'url': href
                    })
                    
            if not sections:
                sections = [
                    {'id': 'land_development', 'title': 'Land Development Code', 'url': f'{url}/land_development'},
                    {'id': 'zoning', 'title': 'Zoning Code', 'url': f'{url}/zoning'},
                    {'id': 'business', 'title': 'Business Tax Receipts', 'url': f'{url}/business'},
                    {'id': 'building', 'title': 'Building Code', 'url': f'{url}/building'},
                    {'id': 'environmental', 'title': 'Environmental Protection', 'url': f'{url}/environmental'}
                ]
                
            return sections[:10]
            
        except Exception as e:
            logger.error(f"Failed to get code sections for {jurisdiction}: {e}")
            return []
    
    def collect_code(self, jurisdiction: str, code_section: str) -> LegalCode:
        """Collect a specific Florida legal code section."""
        try:
            jurisdiction_slug = jurisdiction.lower().replace(' ', '_').replace('.', '')
            url = f"{self.base_url}/{jurisdiction_slug}/{code_section}"
            
            response = self._make_request(url)
            soup = self._parse_html(response.text)
            
            title_elem = soup.find(['h1', 'h2', '.code-title'])
            title = title_elem.get_text().strip() if title_elem else f"{jurisdiction} - {code_section}"
            
            content_selectors = [
                '.code-text',
                '.section-text', 
                'div.ordinance-body',
                '.chapter-content',
                'main'
            ]
            
            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text(separator='\n').strip()
                    break
            
            if not content:
                paragraphs = soup.find_all('p')
                content = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            
            # Look for last updated information
            updated_elem = soup.find(text=re.compile(r'last updated|revised|amended', re.I))
            last_updated = None
            if updated_elem:
                date_match = re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', str(updated_elem))
                if date_match:
                    last_updated = date_match.group()
            
            metadata = {
                'word_count': len(content.split()),
                'character_count': len(content),
                'source_type': 'municipal_code',
                'state_specific': 'florida'
            }
            
            return LegalCode(
                jurisdiction=jurisdiction,
                state=self.state,
                code_section=code_section,
                title=title,
                content=content,
                url=url,
                last_updated=last_updated,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Failed to collect code {code_section} for {jurisdiction}: {e}")
            raise