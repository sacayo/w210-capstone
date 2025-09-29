"""Main analyzer for municipal legal codes."""

from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from collections import Counter
import re
import logging

from ..data_collection.base_collector import LegalCode
from .text_analyzer import TextAnalyzer
from .visualization import LegalCodeVisualizer

logger = logging.getLogger(__name__)


class LegalCodeAnalyzer:
    """Main analyzer for conducting exploratory data analysis on municipal legal codes."""
    
    def __init__(self):
        """Initialize the legal code analyzer."""
        self.text_analyzer = TextAnalyzer()
        self.visualizer = LegalCodeVisualizer()
        
    def analyze_collection(self, codes_by_state: Dict[str, List[LegalCode]]) -> Dict[str, Any]:
        """
        Conduct comprehensive exploratory data analysis on the collected legal codes.
        
        Args:
            codes_by_state: Dictionary mapping state names to lists of legal codes
            
        Returns:
            Dictionary containing analysis results
        """
        logger.info("Starting comprehensive analysis of legal code collection")
        
        # Flatten codes for analysis
        all_codes = []
        for state_codes in codes_by_state.values():
            all_codes.extend(state_codes)
            
        if not all_codes:
            logger.warning("No codes provided for analysis")
            return {}
            
        analysis = {
            'overview': self._analyze_overview(codes_by_state),
            'text_statistics': self._analyze_text_statistics(all_codes),
            'content_analysis': self._analyze_content_patterns(all_codes),
            'comparative_analysis': self._analyze_state_differences(codes_by_state),
            'topic_analysis': self._analyze_topics(all_codes),
            'readability_analysis': self._analyze_readability(all_codes)
        }
        
        logger.info("Analysis complete")
        return analysis
        
    def _analyze_overview(self, codes_by_state: Dict[str, List[LegalCode]]) -> Dict[str, Any]:
        """Generate overview statistics."""
        overview = {
            'total_codes': 0,
            'total_states': len(codes_by_state),
            'codes_by_state': {},
            'jurisdictions_by_state': {},
            'total_jurisdictions': set()
        }
        
        for state, codes in codes_by_state.items():
            overview['total_codes'] += len(codes)
            overview['codes_by_state'][state] = len(codes)
            
            jurisdictions = set(code.jurisdiction for code in codes)
            overview['jurisdictions_by_state'][state] = list(jurisdictions)
            overview['total_jurisdictions'].update(
                f"{jurisdiction}, {state}" for jurisdiction in jurisdictions
            )
            
        overview['total_jurisdictions'] = len(overview['total_jurisdictions'])
        
        return overview
        
    def _analyze_text_statistics(self, codes: List[LegalCode]) -> Dict[str, Any]:
        """Analyze text statistics across all codes."""
        word_counts = []
        char_counts = []
        
        for code in codes:
            if code.metadata:
                word_counts.append(code.metadata.get('word_count', 0))
                char_counts.append(code.metadata.get('character_count', 0))
            else:
                # Calculate on the fly if not in metadata
                words = len(code.content.split())
                chars = len(code.content)
                word_counts.append(words)
                char_counts.append(chars)
                
        return {
            'word_count_stats': {
                'mean': np.mean(word_counts),
                'median': np.median(word_counts),
                'std': np.std(word_counts),
                'min': np.min(word_counts),
                'max': np.max(word_counts),
                'total': np.sum(word_counts)
            },
            'character_count_stats': {
                'mean': np.mean(char_counts),
                'median': np.median(char_counts),
                'std': np.std(char_counts),
                'min': np.min(char_counts),
                'max': np.max(char_counts),
                'total': np.sum(char_counts)
            }
        }
        
    def _analyze_content_patterns(self, codes: List[LegalCode]) -> Dict[str, Any]:
        """Analyze content patterns and common terms."""
        all_titles = [code.title for code in codes]
        all_content = [code.content for code in codes]
        
        # Analyze titles
        title_words = []
        for title in all_titles:
            title_words.extend(self.text_analyzer.extract_keywords(title))
            
        # Analyze content keywords
        content_keywords = []
        for content in all_content:
            keywords = self.text_analyzer.extract_keywords(content)
            content_keywords.extend(keywords[:10])  # Top 10 keywords per document
            
        # Common legal terms
        legal_terms = self._extract_legal_terms(all_content)
        
        return {
            'common_title_words': dict(Counter(title_words).most_common(20)),
            'common_content_keywords': dict(Counter(content_keywords).most_common(30)),
            'legal_terms': dict(Counter(legal_terms).most_common(25)),
            'code_section_patterns': self._analyze_code_section_patterns(codes)
        }
        
    def _analyze_state_differences(self, codes_by_state: Dict[str, List[LegalCode]]) -> Dict[str, Any]:
        """Analyze differences between states."""
        state_analysis = {}
        
        for state, codes in codes_by_state.items():
            if not codes:
                continue
                
            # Text statistics by state
            word_counts = [
                code.metadata.get('word_count', len(code.content.split())) 
                for code in codes if code.content
            ]
            
            # Common terms by state
            all_content = [code.content for code in codes]
            state_keywords = []
            for content in all_content:
                keywords = self.text_analyzer.extract_keywords(content)
                state_keywords.extend(keywords[:5])
                
            state_analysis[state] = {
                'code_count': len(codes),
                'avg_word_count': np.mean(word_counts) if word_counts else 0,
                'jurisdiction_count': len(set(code.jurisdiction for code in codes)),
                'common_terms': dict(Counter(state_keywords).most_common(10)),
                'avg_readability': self._calculate_avg_readability(codes)
            }
            
        return state_analysis
        
    def _analyze_topics(self, codes: List[LegalCode]) -> Dict[str, Any]:
        """Analyze common topics and themes."""
        # Topic keywords based on common municipal code areas
        topic_keywords = {
            'zoning': ['zoning', 'zone', 'district', 'residential', 'commercial', 'industrial', 'land use'],
            'building': ['building', 'construction', 'permit', 'inspection', 'code', 'safety'],
            'business': ['business', 'license', 'permit', 'tax', 'occupation', 'commercial'],
            'public_safety': ['police', 'fire', 'emergency', 'safety', 'security', 'patrol'],
            'environmental': ['environmental', 'pollution', 'waste', 'water', 'air', 'noise'],
            'traffic': ['traffic', 'parking', 'vehicle', 'street', 'road', 'transportation'],
            'utilities': ['utility', 'utilities', 'water', 'sewer', 'electric', 'gas'],
            'health': ['health', 'sanitation', 'food', 'restaurant', 'public health']
        }
        
        topic_counts = {}
        codes_by_topic = {}
        
        for topic, keywords in topic_keywords.items():
            topic_counts[topic] = 0
            codes_by_topic[topic] = []
            
            for code in codes:
                content_lower = code.content.lower()
                title_lower = code.title.lower()
                
                # Count keyword matches
                matches = sum(
                    content_lower.count(keyword) + title_lower.count(keyword) * 2  # Weight title matches more
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
                    
        # Sort topics by frequency
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'topic_frequencies': dict(sorted_topics),
            'codes_by_topic': codes_by_topic,
            'topic_distribution': {
                topic: len(codes_list) for topic, codes_list in codes_by_topic.items()
            }
        }
        
    def _analyze_readability(self, codes: List[LegalCode]) -> Dict[str, Any]:
        """Analyze readability of legal codes."""
        readability_scores = []
        
        for code in codes:
            score = self.text_analyzer.calculate_readability(code.content)
            if score is not None:
                readability_scores.append({
                    'jurisdiction': code.jurisdiction,
                    'state': code.state,
                    'title': code.title,
                    'score': score
                })
                
        if not readability_scores:
            return {'error': 'No readability scores calculated'}
            
        scores = [r['score'] for r in readability_scores]
        
        return {
            'average_score': np.mean(scores),
            'median_score': np.median(scores),
            'min_score': np.min(scores),
            'max_score': np.max(scores),
            'std_score': np.std(scores),
            'by_jurisdiction': readability_scores,
            'interpretation': self._interpret_readability_score(np.mean(scores))
        }
        
    def _extract_legal_terms(self, contents: List[str]) -> List[str]:
        """Extract common legal terms from content."""
        legal_patterns = [
            r'\b(?:shall|may|must|required|prohibited|authorized|permitted)\b',
            r'\b(?:ordinance|regulation|code|statute|provision|section)\b',
            r'\b(?:violation|penalty|fine|enforcement|compliance)\b',
            r'\b(?:permit|license|application|approval|certificate)\b',
            r'\b(?:public|private|property|owner|tenant)\b'
        ]
        
        terms = []
        for content in contents:
            content_lower = content.lower()
            for pattern in legal_patterns:
                matches = re.findall(pattern, content_lower, re.IGNORECASE)
                terms.extend(matches)
                
        return terms
        
    def _analyze_code_section_patterns(self, codes: List[LegalCode]) -> Dict[str, Any]:
        """Analyze patterns in code section identifiers."""
        section_patterns = []
        
        for code in codes:
            # Extract common patterns from code section identifiers
            section = code.code_section
            
            # Look for numeric patterns
            if re.search(r'\d+', section):
                section_patterns.append('numeric')
            if re.search(r'\d+\.\d+', section):
                section_patterns.append('decimal')
            if re.search(r'[A-Z]+', section):
                section_patterns.append('alphabetic')
            if '-' in section:
                section_patterns.append('hyphenated')
                
        return {
            'pattern_frequency': dict(Counter(section_patterns).most_common()),
            'total_sections': len(codes)
        }
        
    def _calculate_avg_readability(self, codes: List[LegalCode]) -> float:
        """Calculate average readability for a set of codes."""
        scores = []
        for code in codes:
            score = self.text_analyzer.calculate_readability(code.content)
            if score is not None:
                scores.append(score)
                
        return np.mean(scores) if scores else 0.0
        
    def _interpret_readability_score(self, score: float) -> str:
        """Interpret a readability score."""
        if score >= 90:
            return "Very Easy (5th grade level)"
        elif score >= 80:
            return "Easy (6th grade level)"
        elif score >= 70:
            return "Fairly Easy (7th grade level)" 
        elif score >= 60:
            return "Standard (8th-9th grade level)"
        elif score >= 50:
            return "Fairly Difficult (10th-12th grade level)"
        elif score >= 30:
            return "Difficult (College level)"
        else:
            return "Very Difficult (Graduate level)"
            
    def generate_analysis_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a text report from analysis results."""
        report = []
        report.append("MUNICIPAL LEGAL CODE ANALYSIS REPORT")
        report.append("=" * 50)
        report.append("")
        
        # Overview
        if 'overview' in analysis:
            overview = analysis['overview']
            report.append(f"Total Legal Codes Analyzed: {overview['total_codes']}")
            report.append(f"States Covered: {overview['total_states']}")
            report.append(f"Total Jurisdictions: {overview['total_jurisdictions']}")
            report.append("")
            
            report.append("Codes by State:")
            for state, count in overview['codes_by_state'].items():
                report.append(f"  {state}: {count} codes")
            report.append("")
            
        # Text Statistics
        if 'text_statistics' in analysis:
            stats = analysis['text_statistics']
            word_stats = stats['word_count_stats']
            
            report.append("TEXT STATISTICS")
            report.append("-" * 20)
            report.append(f"Average words per code: {word_stats['mean']:.0f}")
            report.append(f"Total words: {word_stats['total']:,}")
            report.append(f"Longest code: {word_stats['max']:,} words")
            report.append(f"Shortest code: {word_stats['min']:,} words")
            report.append("")
            
        # Content Analysis
        if 'content_analysis' in analysis:
            content = analysis['content_analysis']
            
            report.append("COMMON TERMS")
            report.append("-" * 20)
            
            if 'common_title_words' in content:
                report.append("Most common words in titles:")
                for word, count in list(content['common_title_words'].items())[:10]:
                    report.append(f"  {word}: {count}")
                report.append("")
                
        # Topic Analysis
        if 'topic_analysis' in analysis:
            topics = analysis['topic_analysis']
            
            report.append("TOPIC ANALYSIS")
            report.append("-" * 20)
            
            if 'topic_frequencies' in topics:
                report.append("Most common topics:")
                for topic, freq in list(topics['topic_frequencies'].items())[:8]:
                    report.append(f"  {topic.replace('_', ' ').title()}: {freq} mentions")
                report.append("")
                
        # Readability
        if 'readability_analysis' in analysis:
            readability = analysis['readability_analysis']
            
            if 'average_score' in readability:
                report.append("READABILITY ANALYSIS")
                report.append("-" * 20)
                report.append(f"Average readability score: {readability['average_score']:.1f}")
                report.append(f"Interpretation: {readability['interpretation']}")
                report.append("")
        
        return "\n".join(report)