"""
Municipal Legal Research System

An end-to-end agentic research system for conducting exploratory data analysis
of municipal legal code ordinances for California, Georgia, Florida, and Texas.
"""

__version__ = "0.1.0"
__author__ = "W210 Capstone Team"

from .agents import ResearchAgent
from .data_collection import MunicipalDataCollector
from .analysis import LegalCodeAnalyzer

__all__ = ["ResearchAgent", "MunicipalDataCollector", "LegalCodeAnalyzer"]