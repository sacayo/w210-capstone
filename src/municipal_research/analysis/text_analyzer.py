"""Text analysis utilities for legal code content."""

from typing import List, Dict, Optional, Tuple
import re
import string
from collections import Counter
import logging

NLTK_AVAILABLE = False
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.stem import PorterStemmer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

TEXTSTAT_AVAILABLE = False
try:
    import textstat
    TEXTSTAT_AVAILABLE = True
except ImportError:
    TEXTSTAT_AVAILABLE = False

logger = logging.getLogger(__name__)


class TextAnalyzer:
    """Text analysis utilities for legal code content."""
    
    def __init__(self):
        """Initialize the text analyzer."""
        self.stemmer = None
        self.stop_words = set()
        
        # Try to use NLTK if available
        nltk_success = False
        if NLTK_AVAILABLE:
            try:
                # Download required NLTK data
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                
                self.stemmer = PorterStemmer()
                self.stop_words = set(stopwords.words('english'))
                
                # Add legal-specific stop words
                legal_stopwords = {
                    'shall', 'may', 'section', 'subsection', 'paragraph', 
                    'code', 'ordinance', 'chapter', 'article', 'part',
                    'thereof', 'herein', 'hereof', 'wherein'
                }
                self.stop_words.update(legal_stopwords)
                nltk_success = True
                
            except Exception as e:
                logger.warning(f"Failed to initialize NLTK components: {e}")
        
        # Fallback stop words if NLTK not available or failed
        if not nltk_success:
            self.stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                'should', 'may', 'might', 'must', 'can', 'shall', 'this', 'that',
                'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
                'section', 'subsection', 'code', 'ordinance', 'chapter'
            }
    
    def extract_keywords(self, text: str, max_keywords: int = 20) -> List[str]:
        """
        Extract keywords from text.
        
        Args:
            text: Input text
            max_keywords: Maximum number of keywords to return
            
        Returns:
            List of keywords
        """
        if not text:
            return []
            
        # Clean and tokenize text
        cleaned_text = self._clean_text(text)
        
        if NLTK_AVAILABLE and self.stemmer:
            try:
                tokens = word_tokenize(cleaned_text.lower())
            except:
                tokens = cleaned_text.lower().split()
        else:
            tokens = cleaned_text.lower().split()
        
        # Filter tokens
        keywords = []
        for token in tokens:
            if (len(token) > 2 and 
                token not in self.stop_words and
                token.isalpha() and
                not token.isdigit()):
                keywords.append(token)
        
        # Get most common keywords
        keyword_counts = Counter(keywords)
        return [word for word, count in keyword_counts.most_common(max_keywords)]
    
    def calculate_readability(self, text: str) -> Optional[float]:
        """
        Calculate readability score (Flesch Reading Ease).
        
        Args:
            text: Input text
            
        Returns:
            Readability score (0-100, higher = easier to read)
        """
        if not text or not TEXTSTAT_AVAILABLE:
            return None
            
        try:
            return textstat.flesch_reading_ease(text)
        except Exception as e:
            logger.warning(f"Failed to calculate readability: {e}")
            return None
    
    def calculate_complexity_metrics(self, text: str) -> Dict[str, float]:
        """
        Calculate various text complexity metrics.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of complexity metrics
        """
        if not text:
            return {}
        
        metrics = {}
        
        # Basic metrics
        words = len(text.split())
        sentences = len(self._split_sentences(text))
        characters = len(text)
        
        metrics['word_count'] = words
        metrics['sentence_count'] = sentences
        metrics['character_count'] = characters
        
        if sentences > 0:
            metrics['avg_words_per_sentence'] = words / sentences
        else:
            metrics['avg_words_per_sentence'] = 0
            
        if words > 0:
            metrics['avg_characters_per_word'] = characters / words
        else:
            metrics['avg_characters_per_word'] = 0
        
        # Advanced metrics (if textstat is available)
        if TEXTSTAT_AVAILABLE:
            try:
                metrics['flesch_reading_ease'] = textstat.flesch_reading_ease(text)
                metrics['flesch_kincaid_grade'] = textstat.flesch_kincaid_grade(text)
                metrics['automated_readability_index'] = textstat.automated_readability_index(text)
                metrics['coleman_liau_index'] = textstat.coleman_liau_index(text)
            except Exception as e:
                logger.warning(f"Failed to calculate advanced metrics: {e}")
        
        return metrics
    
    def extract_legal_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract legal entities and terms from text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary mapping entity types to lists of entities
        """
        entities = {
            'dates': [],
            'numbers': [],
            'references': [],
            'penalties': [],
            'requirements': []
        }
        
        # Extract dates
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b\w+\s+\d{1,2},?\s+\d{4}\b',
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['dates'].extend(matches)
        
        # Extract numbers and amounts
        number_patterns = [
            r'\$[\d,]+\.?\d*',  # Dollar amounts
            r'\b\d+\.?\d*\s*(?:percent|%)\b',  # Percentages
            r'\b\d+\.?\d*\s*(?:feet|ft|inches|in|yards|yd|miles|mi)\b',  # Measurements
            r'\b\d+\.?\d*\s*(?:days|hours|years|months)\b'  # Time periods
        ]
        
        for pattern in number_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['numbers'].extend(matches)
        
        # Extract section references
        ref_patterns = [
            r'[Ss]ection\s+\d+(?:\.\d+)*',
            r'[Cc]hapter\s+\d+',
            r'[Aa]rticle\s+\d+',
            r'[Pp]aragraph\s+\([a-z0-9]+\)'
        ]
        
        for pattern in ref_patterns:
            matches = re.findall(pattern, text)
            entities['references'].extend(matches)
        
        # Extract penalties and fines
        penalty_patterns = [
            r'fine\s+(?:of\s+)?(?:not\s+)?(?:more\s+than\s+|less\s+than\s+|up\s+to\s+)?\$[\d,]+',
            r'penalty\s+(?:of\s+)?(?:not\s+)?(?:more\s+than\s+|less\s+than\s+|up\s+to\s+)?\$[\d,]+',
            r'imprisonment\s+(?:for\s+)?(?:not\s+)?(?:more\s+than\s+|up\s+to\s+)?\d+\s+(?:days?|months?|years?)'
        ]
        
        for pattern in penalty_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['penalties'].extend(matches)
        
        # Extract requirement keywords
        requirement_patterns = [
            r'(?:shall|must|required to|obligated to)\s+[\w\s]+',
            r'(?:prohibited|forbidden|not permitted)\s+[\w\s]+',
            r'(?:may|allowed to|permitted to)\s+[\w\s]+'
        ]
        
        for pattern in requirement_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            # Limit length to avoid very long matches
            entities['requirements'].extend([m[:100] for m in matches])
        
        # Remove duplicates and empty strings
        for entity_type in entities:
            entities[entity_type] = list(set(filter(None, entities[entity_type])))
        
        return entities
    
    def analyze_sentence_structure(self, text: str) -> Dict[str, float]:
        """
        Analyze sentence structure complexity.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of sentence structure metrics
        """
        sentences = self._split_sentences(text)
        
        if not sentences:
            return {}
        
        sentence_lengths = [len(s.split()) for s in sentences]
        
        # Count complex sentence indicators
        complex_indicators = 0
        for sentence in sentences:
            # Count subordinating conjunctions and relative pronouns
            complex_words = ['although', 'because', 'since', 'unless', 'while', 
                           'whereas', 'which', 'that', 'who', 'whom', 'where']
            for word in complex_words:
                if word in sentence.lower():
                    complex_indicators += 1
                    
        return {
            'avg_sentence_length': sum(sentence_lengths) / len(sentence_lengths),
            'max_sentence_length': max(sentence_lengths),
            'min_sentence_length': min(sentence_lengths),
            'sentence_count': len(sentences),
            'complex_sentence_ratio': complex_indicators / len(sentences) if sentences else 0
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean text for analysis."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)]', ' ', text)
        
        return text.strip()
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        if NLTK_AVAILABLE:
            try:
                return sent_tokenize(text)
            except:
                pass
        
        # Fallback sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def compare_texts(self, texts: List[str], labels: List[str] = None) -> Dict[str, Dict]:
        """
        Compare multiple texts across various metrics.
        
        Args:
            texts: List of texts to compare
            labels: Optional labels for each text
            
        Returns:
            Dictionary comparing texts across metrics
        """
        if not texts:
            return {}
        
        if labels is None:
            labels = [f"Text {i+1}" for i in range(len(texts))]
        
        comparison = {}
        
        for i, (text, label) in enumerate(zip(texts, labels)):
            comparison[label] = {
                'complexity': self.calculate_complexity_metrics(text),
                'keywords': self.extract_keywords(text, 10),
                'entities': self.extract_legal_entities(text),
                'sentence_structure': self.analyze_sentence_structure(text)
            }
        
        return comparison