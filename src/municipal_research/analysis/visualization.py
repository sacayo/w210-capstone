"""Visualization utilities for legal code analysis."""

from typing import List, Dict, Any, Optional, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from collections import Counter
import logging

try:
    from wordcloud import WordCloud
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

logger = logging.getLogger(__name__)


class LegalCodeVisualizer:
    """Visualization utilities for legal code analysis."""
    
    def __init__(self, style: str = 'seaborn-v0_8'):
        """
        Initialize the visualizer.
        
        Args:
            style: Matplotlib style to use
        """
        # Set up matplotlib style
        try:
            plt.style.use(style)
        except:
            try:
                plt.style.use('seaborn')
            except:
                pass  # Use default style
                
        sns.set_palette("husl")
        
    def plot_codes_by_state(self, codes_by_state: Dict[str, int], 
                           save_path: Optional[str] = None) -> plt.Figure:
        """
        Create a bar plot of code counts by state.
        
        Args:
            codes_by_state: Dictionary mapping states to code counts
            save_path: Optional path to save the plot
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        states = list(codes_by_state.keys())
        counts = list(codes_by_state.values())
        
        bars = ax.bar(states, counts, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
        
        ax.set_title('Legal Codes Collected by State', fontsize=16, fontweight='bold')
        ax.set_xlabel('State', fontsize=12)
        ax.set_ylabel('Number of Codes', fontsize=12)
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{count}', ha='center', va='bottom', fontsize=10)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_text_statistics(self, word_stats: Dict[str, float], 
                           save_path: Optional[str] = None) -> plt.Figure:
        """
        Create visualizations for text statistics.
        
        Args:
            word_stats: Dictionary of word count statistics
            save_path: Optional path to save the plot
            
        Returns:
            Matplotlib figure
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        
        # Summary statistics
        stats_to_plot = ['mean', 'median', 'min', 'max']
        values = [word_stats[stat] for stat in stats_to_plot]
        
        ax1.bar(stats_to_plot, values, color=['skyblue', 'lightgreen', 'lightcoral', 'gold'])
        ax1.set_title('Word Count Statistics')
        ax1.set_ylabel('Word Count')
        
        # Add value labels
        for i, v in enumerate(values):
            ax1.text(i, v, f'{v:.0f}', ha='center', va='bottom')
        
        # Create a simple histogram representation (placeholder)
        # In a real implementation, you'd pass the actual word count data
        x = np.random.normal(word_stats['mean'], word_stats['std'], 1000)
        x = np.clip(x, word_stats['min'], word_stats['max'])
        
        ax2.hist(x, bins=20, alpha=0.7, color='lightblue', edgecolor='black')
        ax2.set_title('Word Count Distribution (Simulated)')
        ax2.set_xlabel('Word Count')
        ax2.set_ylabel('Frequency')
        
        # Box plot representation
        box_data = [x]
        ax3.boxplot(box_data, labels=['All Codes'])
        ax3.set_title('Word Count Box Plot')
        ax3.set_ylabel('Word Count')
        
        # Summary text
        ax4.axis('off')
        summary_text = f"""
        Text Statistics Summary:
        
        Total Words: {word_stats['total']:,.0f}
        Average: {word_stats['mean']:.0f} words
        Median: {word_stats['median']:.0f} words
        Range: {word_stats['min']:.0f} - {word_stats['max']:.0f}
        Std Dev: {word_stats['std']:.0f}
        """
        ax4.text(0.1, 0.5, summary_text, fontsize=12, va='center')
        
        plt.suptitle('Legal Code Text Statistics', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_common_terms(self, terms_dict: Dict[str, int], title: str = "Common Terms",
                         max_terms: int = 15, save_path: Optional[str] = None) -> plt.Figure:
        """
        Create a horizontal bar plot of common terms.
        
        Args:
            terms_dict: Dictionary mapping terms to frequencies
            title: Plot title
            max_terms: Maximum number of terms to display
            save_path: Optional path to save the plot
            
        Returns:
            Matplotlib figure
        """
        # Get top terms
        top_terms = dict(Counter(terms_dict).most_common(max_terms))
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        terms = list(top_terms.keys())
        counts = list(top_terms.values())
        
        # Create horizontal bar plot
        bars = ax.barh(terms, counts, color=plt.cm.viridis(np.linspace(0, 1, len(terms))))
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Frequency', fontsize=12)
        
        # Add value labels
        for bar, count in zip(bars, counts):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f'{count}', ha='left', va='center', fontsize=9)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def create_wordcloud(self, text_data: str, title: str = "Word Cloud",
                        save_path: Optional[str] = None) -> Optional[plt.Figure]:
        """
        Create a word cloud visualization.
        
        Args:
            text_data: Text data for word cloud
            title: Plot title
            save_path: Optional path to save the plot
            
        Returns:
            Matplotlib figure or None if wordcloud not available
        """
        if not WORDCLOUD_AVAILABLE:
            logger.warning("WordCloud library not available")
            return None
        
        try:
            wordcloud = WordCloud(
                width=800, 
                height=400, 
                background_color='white',
                max_words=100,
                colormap='viridis'
            ).generate(text_data)
            
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to create word cloud: {e}")
            return None
    
    def plot_topic_distribution(self, topic_data: Dict[str, int],
                              save_path: Optional[str] = None) -> plt.Figure:
        """
        Create a pie chart of topic distribution.
        
        Args:
            topic_data: Dictionary mapping topics to frequencies
            save_path: Optional path to save the plot
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        topics = list(topic_data.keys())
        values = list(topic_data.values())
        
        # Create pie chart
        colors = plt.cm.Set3(np.linspace(0, 1, len(topics)))
        wedges, texts, autotexts = ax.pie(values, labels=topics, autopct='%1.1f%%',
                                         colors=colors, startangle=90)
        
        ax.set_title('Topic Distribution in Legal Codes', fontsize=16, fontweight='bold')
        
        # Improve text readability
        for autotext in autotexts:
            autotext.set_color('black')
            autotext.set_fontweight('bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_readability_comparison(self, readability_data: List[Dict],
                                  save_path: Optional[str] = None) -> plt.Figure:
        """
        Create a scatter plot comparing readability scores.
        
        Args:
            readability_data: List of dicts with jurisdiction, state, and score
            save_path: Optional path to save the plot
            
        Returns:
            Matplotlib figure
        """
        if not readability_data:
            logger.warning("No readability data provided")
            return None
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Prepare data
        states = [item['state'] for item in readability_data]
        scores = [item['score'] for item in readability_data]
        jurisdictions = [item['jurisdiction'] for item in readability_data]
        
        # Create scatter plot with different colors for each state
        unique_states = list(set(states))
        colors = plt.cm.tab10(np.linspace(0, 1, len(unique_states)))
        state_colors = {state: color for state, color in zip(unique_states, colors)}
        
        for state in unique_states:
            state_scores = [score for s, score in zip(states, scores) if s == state]
            state_indices = [i for i, s in enumerate(states) if s == state]
            
            ax.scatter(state_indices, state_scores, 
                      label=state, color=state_colors[state], s=50, alpha=0.7)
        
        ax.set_title('Readability Scores by Jurisdiction', fontsize=16, fontweight='bold')
        ax.set_xlabel('Jurisdiction Index', fontsize=12)
        ax.set_ylabel('Readability Score', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Add readability level annotations
        ax.axhline(y=90, color='green', linestyle='--', alpha=0.5, label='Very Easy')
        ax.axhline(y=70, color='yellow', linestyle='--', alpha=0.5, label='Fairly Easy')
        ax.axhline(y=50, color='orange', linestyle='--', alpha=0.5, label='Fairly Difficult')
        ax.axhline(y=30, color='red', linestyle='--', alpha=0.5, label='Difficult')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def create_dashboard(self, analysis_results: Dict[str, Any], 
                        save_dir: str = "visualizations") -> Dict[str, str]:
        """
        Create a complete dashboard of visualizations.
        
        Args:
            analysis_results: Complete analysis results
            save_dir: Directory to save visualizations
            
        Returns:
            Dictionary mapping plot types to file paths
        """
        import os
        os.makedirs(save_dir, exist_ok=True)
        
        plot_paths = {}
        
        try:
            # State distribution plot
            if 'overview' in analysis_results:
                overview = analysis_results['overview']
                if 'codes_by_state' in overview:
                    fig = self.plot_codes_by_state(
                        overview['codes_by_state'],
                        save_path=os.path.join(save_dir, 'codes_by_state.png')
                    )
                    plt.close(fig)
                    plot_paths['codes_by_state'] = os.path.join(save_dir, 'codes_by_state.png')
            
            # Text statistics
            if 'text_statistics' in analysis_results:
                stats = analysis_results['text_statistics']['word_count_stats']
                fig = self.plot_text_statistics(
                    stats,
                    save_path=os.path.join(save_dir, 'text_statistics.png')
                )
                plt.close(fig)
                plot_paths['text_statistics'] = os.path.join(save_dir, 'text_statistics.png')
            
            # Common terms
            if 'content_analysis' in analysis_results:
                content = analysis_results['content_analysis']
                if 'common_title_words' in content:
                    fig = self.plot_common_terms(
                        content['common_title_words'],
                        title="Most Common Words in Titles",
                        save_path=os.path.join(save_dir, 'common_title_words.png')
                    )
                    plt.close(fig)
                    plot_paths['common_title_words'] = os.path.join(save_dir, 'common_title_words.png')
                
                if 'common_content_keywords' in content:
                    fig = self.plot_common_terms(
                        content['common_content_keywords'],
                        title="Most Common Content Keywords",
                        save_path=os.path.join(save_dir, 'common_keywords.png')
                    )
                    plt.close(fig)
                    plot_paths['common_keywords'] = os.path.join(save_dir, 'common_keywords.png')
            
            # Topic distribution
            if 'topic_analysis' in analysis_results:
                topics = analysis_results['topic_analysis']
                if 'topic_frequencies' in topics:
                    fig = self.plot_topic_distribution(
                        topics['topic_frequencies'],
                        save_path=os.path.join(save_dir, 'topic_distribution.png')
                    )
                    plt.close(fig)
                    plot_paths['topic_distribution'] = os.path.join(save_dir, 'topic_distribution.png')
            
            # Readability comparison
            if 'readability_analysis' in analysis_results:
                readability = analysis_results['readability_analysis']
                if 'by_jurisdiction' in readability:
                    fig = self.plot_readability_comparison(
                        readability['by_jurisdiction'],
                        save_path=os.path.join(save_dir, 'readability_comparison.png')
                    )
                    if fig:
                        plt.close(fig)
                        plot_paths['readability_comparison'] = os.path.join(save_dir, 'readability_comparison.png')
            
        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
        
        return plot_paths