"""California municipal legal code collector."""

from typing import List, Dict
import re
import logging
from .base_collector import BaseCollector, LegalCode

logger = logging.getLogger(__name__)


class CaliforniaCollector(BaseCollector):
    """Collector for California municipal legal codes."""
    
    def __init__(self):
        # California municipal codes are often found on municode.com or city websites
        super().__init__(
            state="California",
            base_url="https://municode.com/library/ca",
            rate_limit=1.5
        )
        
    def get_jurisdictions(self) -> List[str]:
        """Get list of California cities and counties."""
        try:
            response = self._make_request(self.base_url)
            soup = self._parse_html(response.text)
            
            # Look for jurisdiction links
            jurisdictions = []
            
            # This is a simplified example - actual implementation would 
            # need to parse the specific website structure
            jurisdiction_links = soup.find_all('a', href=re.compile(r'/library/ca/'))
            
            for link in jurisdiction_links:
                jurisdiction_name = link.get_text().strip()
                if jurisdiction_name and len(jurisdiction_name) > 2:
                    jurisdictions.append(jurisdiction_name)
                    
            # Add some common California cities as examples
            example_jurisdictions = [
                "San Francisco", "Los Angeles", "San Diego", "Oakland", 
                "San Jose", "Sacramento", "Fresno", "Long Beach"
            ]
            
            jurisdictions.extend(example_jurisdictions)
            return list(set(jurisdictions))
            
        except Exception as e:
            logger.error(f"Failed to get California jurisdictions: {e}")
            # Return example jurisdictions as fallback
            return [
                "San Francisco", "Los Angeles", "San Diego", "Oakland",
                "San Jose", "Sacramento", "Fresno", "Long Beach"
            ]
    
    def get_code_sections(self, jurisdiction: str) -> List[Dict[str, str]]:
        """Get code sections for a California jurisdiction."""
        try:
            # Construct URL for jurisdiction
            jurisdiction_slug = jurisdiction.lower().replace(' ', '_')
            url = f"{self.base_url}/{jurisdiction_slug}"
            
            response = self._make_request(url)
            soup = self._parse_html(response.text)
            
            sections = []
            
            # Look for code section links
            section_links = soup.find_all('a', href=re.compile(r'chapter|title|section'))
            
            for link in section_links:
                section_text = link.get_text().strip()
                href = link.get('href', '')
                
                if section_text and href:
                    sections.append({
                        'id': href.split('/')[-1],
                        'title': section_text,
                        'url': href
                    })
                    
            # If no sections found, return common municipal code sections
            if not sections:
                sections = [
                    {'id': 'zoning', 'title': 'Zoning Ordinances', 'url': f'{url}/zoning'},
                    {'id': 'building', 'title': 'Building Code', 'url': f'{url}/building'},
                    {'id': 'business', 'title': 'Business Regulations', 'url': f'{url}/business'},
                    {'id': 'public_safety', 'title': 'Public Safety', 'url': f'{url}/public_safety'},
                    {'id': 'environmental', 'title': 'Environmental Regulations', 'url': f'{url}/environmental'}
                ]
                
            return sections[:10]  # Limit to first 10 sections
            
        except Exception as e:
            logger.error(f"Failed to get code sections for {jurisdiction}: {e}")
            return []
    
    def collect_code(self, jurisdiction: str, code_section: str) -> LegalCode:
        """Collect a specific California legal code section."""
        try:
            jurisdiction_slug = jurisdiction.lower().replace(' ', '_')
            url = f"{self.base_url}/{jurisdiction_slug}/{code_section}"
            
            response = self._make_request(url)
            soup = self._parse_html(response.text)
            
            # Extract title
            title_elem = soup.find(['h1', 'h2', 'title'])
            title = title_elem.get_text().strip() if title_elem else f"{jurisdiction} - {code_section}"
            
            # Extract content
            content_selectors = [
                'div.code-content',
                'div.ordinance-text', 
                'div.section-content',
                'article',
                'main'
            ]
            
            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text(separator='\n').strip()
                    break
            
            # If no specific content found, get all paragraph text
            if not content:
                paragraphs = soup.find_all('p')
                content = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            
            # Extract metadata
            metadata = {
                'word_count': len(content.split()),
                'character_count': len(content),
                'source_type': 'municipal_code'
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