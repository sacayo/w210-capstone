"""Georgia municipal legal code collector."""

from typing import List, Dict
import re
import logging
from .base_collector import BaseCollector, LegalCode

logger = logging.getLogger(__name__)


class GeorgiaCollector(BaseCollector):
    """Collector for Georgia municipal legal codes."""
    
    def __init__(self):
        super().__init__(
            state="Georgia",
            base_url="https://library.municode.com/ga",
            rate_limit=1.0
        )
        
    def get_jurisdictions(self) -> List[str]:
        """Get list of Georgia cities and counties."""
        try:
            response = self._make_request(self.base_url)
            soup = self._parse_html(response.text)
            
            jurisdictions = []
            jurisdiction_links = soup.find_all('a', href=re.compile(r'/ga/'))
            
            for link in jurisdiction_links:
                jurisdiction_name = link.get_text().strip()
                if jurisdiction_name and len(jurisdiction_name) > 2:
                    jurisdictions.append(jurisdiction_name)
                    
            # Add major Georgia cities
            example_jurisdictions = [
                "Atlanta", "Augusta", "Columbus", "Savannah", "Athens",
                "Sandy Springs", "Roswell", "Macon", "Albany", "Marietta"
            ]
            
            jurisdictions.extend(example_jurisdictions)
            return list(set(jurisdictions))
            
        except Exception as e:
            logger.error(f"Failed to get Georgia jurisdictions: {e}")
            return [
                "Atlanta", "Augusta", "Columbus", "Savannah", "Athens",
                "Sandy Springs", "Roswell", "Macon", "Albany", "Marietta"
            ]
    
    def get_code_sections(self, jurisdiction: str) -> List[Dict[str, str]]:
        """Get code sections for a Georgia jurisdiction."""
        try:
            jurisdiction_slug = jurisdiction.lower().replace(' ', '_')
            url = f"{self.base_url}/{jurisdiction_slug}"
            
            response = self._make_request(url)
            soup = self._parse_html(response.text)
            
            sections = []
            section_links = soup.find_all('a', href=re.compile(r'chapter|section|article'))
            
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
                    {'id': 'zoning', 'title': 'Zoning Ordinance', 'url': f'{url}/zoning'},
                    {'id': 'subdivision', 'title': 'Subdivision Regulations', 'url': f'{url}/subdivision'},
                    {'id': 'business', 'title': 'Business License', 'url': f'{url}/business'},
                    {'id': 'public_works', 'title': 'Public Works', 'url': f'{url}/public_works'},
                    {'id': 'health', 'title': 'Health and Safety', 'url': f'{url}/health'}
                ]
                
            return sections[:10]
            
        except Exception as e:
            logger.error(f"Failed to get code sections for {jurisdiction}: {e}")
            return []
    
    def collect_code(self, jurisdiction: str, code_section: str) -> LegalCode:
        """Collect a specific Georgia legal code section."""
        try:
            jurisdiction_slug = jurisdiction.lower().replace(' ', '_')
            url = f"{self.base_url}/{jurisdiction_slug}/{code_section}"
            
            response = self._make_request(url)
            soup = self._parse_html(response.text)
            
            title_elem = soup.find(['h1', 'h2', '.ordinance-title'])
            title = title_elem.get_text().strip() if title_elem else f"{jurisdiction} - {code_section}"
            
            content_selectors = [
                '.code-section-text',
                '.ordinance-content', 
                'article.ordinance',
                'div.section-content',
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
            
            metadata = {
                'word_count': len(content.split()),
                'character_count': len(content),
                'source_type': 'municipal_ordinance',
                'state_specific': 'georgia'
            }
            
            return LegalCode(
                jurisdiction=jurisdiction,
                state=self.state,
                code_section=code_section,
                title=title,
                content=content,
                url=url,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Failed to collect code {code_section} for {jurisdiction}: {e}")
            raise