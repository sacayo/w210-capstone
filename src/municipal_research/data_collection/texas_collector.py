"""Texas municipal legal code collector."""

from typing import List, Dict
import re
import logging
from .base_collector import BaseCollector, LegalCode

logger = logging.getLogger(__name__)


class TexasCollector(BaseCollector):
    """Collector for Texas municipal legal codes."""
    
    def __init__(self):
        super().__init__(
            state="Texas",
            base_url="https://library.municode.com/tx",
            rate_limit=1.0
        )
        
    def get_jurisdictions(self) -> List[str]:
        """Get list of Texas cities and counties."""
        try:
            response = self._make_request(self.base_url)
            soup = self._parse_html(response.text)
            
            jurisdictions = []
            jurisdiction_links = soup.find_all('a', href=re.compile(r'/tx/'))
            
            for link in jurisdiction_links:
                jurisdiction_name = link.get_text().strip()
                if jurisdiction_name and len(jurisdiction_name) > 2:
                    jurisdictions.append(jurisdiction_name)
                    
            # Add major Texas cities as examples
            example_jurisdictions = [
                "Houston", "Dallas", "San Antonio", "Austin", "Fort Worth",
                "El Paso", "Arlington", "Corpus Christi", "Plano", "Lubbock"
            ]
            
            jurisdictions.extend(example_jurisdictions)
            return list(set(jurisdictions))
            
        except Exception as e:
            logger.error(f"Failed to get Texas jurisdictions: {e}")
            return [
                "Houston", "Dallas", "San Antonio", "Austin", "Fort Worth",
                "El Paso", "Arlington", "Corpus Christi", "Plano", "Lubbock"
            ]
    
    def get_code_sections(self, jurisdiction: str) -> List[Dict[str, str]]:
        """Get code sections for a Texas jurisdiction.""" 
        try:
            jurisdiction_slug = jurisdiction.lower().replace(' ', '_')
            url = f"{self.base_url}/{jurisdiction_slug}"
            
            response = self._make_request(url)
            soup = self._parse_html(response.text)
            
            sections = []
            section_links = soup.find_all('a', href=re.compile(r'chapter|title|article'))
            
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
                    {'id': 'zoning', 'title': 'Zoning and Development', 'url': f'{url}/zoning'},
                    {'id': 'building', 'title': 'Building Standards', 'url': f'{url}/building'},
                    {'id': 'business', 'title': 'Business License Code', 'url': f'{url}/business'},
                    {'id': 'traffic', 'title': 'Traffic and Vehicles', 'url': f'{url}/traffic'},
                    {'id': 'utilities', 'title': 'Utilities', 'url': f'{url}/utilities'}
                ]
                
            return sections[:10]
            
        except Exception as e:
            logger.error(f"Failed to get code sections for {jurisdiction}: {e}")
            return []
    
    def collect_code(self, jurisdiction: str, code_section: str) -> LegalCode:
        """Collect a specific Texas legal code section."""
        try:
            jurisdiction_slug = jurisdiction.lower().replace(' ', '_')
            url = f"{self.base_url}/{jurisdiction_slug}/{code_section}"
            
            response = self._make_request(url)
            soup = self._parse_html(response.text)
            
            # Extract title
            title_elem = soup.find(['h1', 'h2', '.section-title', '.chapter-title'])
            title = title_elem.get_text().strip() if title_elem else f"{jurisdiction} - {code_section}"
            
            # Extract content
            content_selectors = [
                '.ordinance-body',
                '.section-body', 
                '.chapter-body',
                'article.code-section',
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
            
            # Extract effective date if available
            date_elem = soup.find(text=re.compile(r'effective|adopted|enacted', re.I))
            effective_date = None
            if date_elem:
                date_match = re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', str(date_elem))
                if date_match:
                    effective_date = date_match.group()
            
            metadata = {
                'word_count': len(content.split()),
                'character_count': len(content),
                'source_type': 'municipal_code',
                'state_specific': 'texas'
            }
            
            return LegalCode(
                jurisdiction=jurisdiction,
                state=self.state,
                code_section=code_section,
                title=title,
                content=content,
                url=url,
                effective_date=effective_date,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Failed to collect code {code_section} for {jurisdiction}: {e}")
            raise