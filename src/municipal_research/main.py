"""Main entry point for the municipal legal research system."""

import argparse
import sys
import os
from datetime import datetime
from typing import Optional, Dict, Any

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from municipal_research.agents import ResearchAgent
from municipal_research.utils import setup_logging, ConfigManager


def main() -> None:
    """Main entry point for the municipal legal research system."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Municipal Legal Code Research System"
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--log-level', '-l',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Logging level'
    )
    
    parser.add_argument(
        '--data-dir', '-d',
        type=str,
        default='data',
        help='Directory for data storage'
    )
    
    parser.add_argument(
        '--max-jurisdictions',
        type=int,
        default=2,
        help='Maximum jurisdictions per state to collect'
    )
    
    parser.add_argument(
        '--max-codes',
        type=int,
        default=3,
        help='Maximum codes per jurisdiction to collect'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        default='output',
        help='Directory for output files'
    )
    
    parser.add_argument(
        '--no-visualizations',
        action='store_true',
        help='Skip visualization generation'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config_manager = ConfigManager(args.config)
    config = config_manager.config
    
    # Override config with command line arguments
    if args.data_dir:
        config_manager.set('output.data_dir', args.data_dir)
    
    # Set up logging
    setup_logging(
        log_level=args.log_level,
        log_file=config_manager.get('logging.log_file') if config_manager.get('logging.log_to_file') else None
    )
    
    # Create necessary directories
    config_manager.create_directories()
    
    print("=" * 60)
    print("MUNICIPAL LEGAL CODE RESEARCH SYSTEM")
    print("=" * 60)
    print(f"Starting research at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Configuration: {config_manager.config_path}")
    print(f"Data directory: {config_manager.get('output.data_dir')}")
    print(f"Max jurisdictions per state: {args.max_jurisdictions}")
    print(f"Max codes per jurisdiction: {args.max_codes}")
    print()
    
    try:
        # Initialize research agent
        research_config = {
            'data_dir': config_manager.get('output.data_dir'),
            'visualization_dir': config_manager.get('output.visualization_dir'),
            'reports_dir': config_manager.get('output.reports_dir')
        }
        
        agent = ResearchAgent(research_config)
        
        # Define research task
        task = {
            'type': 'conduct_research',
            'collection_parameters': {
                'max_jurisdictions_per_state': args.max_jurisdictions,
                'max_codes_per_jurisdiction': args.max_codes,
                'save_data': True,
                'filename_prefix': f'research_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            },
            'analysis_parameters': {
                'generate_visualizations': not args.no_visualizations,
                'visualization_dir': config_manager.get('output.visualization_dir')
            }
        }
        
        print("🚀 Starting data collection and analysis...")
        print()
        
        # Execute research
        results = agent.execute_task(task)
        
        # Display results
        print("✅ Research completed successfully!")
        print()
        print("RESULTS SUMMARY:")
        print("-" * 40)
        
        workflow_summary = results.get('workflow_summary', {})
        print(f"Codes collected: {workflow_summary.get('codes_collected', 0)}")
        print(f"States analyzed: {workflow_summary.get('states_analyzed', 0)}")
        print(f"Analysis completed: {workflow_summary.get('analysis_completed', False)}")
        print(f"Report generated: {workflow_summary.get('report_generated', False)}")
        print()
        
        # Display file paths
        collection_results = results.get('collection_results', {})
        file_paths = collection_results.get('file_paths', {})
        
        if file_paths:
            print("OUTPUT FILES:")
            print("-" * 40)
            for file_type, path in file_paths.items():
                print(f"{file_type.upper()}: {path}")
        
        # Display visualizations
        analysis_results = results.get('analysis_results', {})
        visualizations = analysis_results.get('visualizations', {})
        
        if visualizations:
            print()
            print("VISUALIZATIONS:")
            print("-" * 40)
            for viz_type, path in visualizations.items():
                print(f"{viz_type.replace('_', ' ').title()}: {path}")
        
        # Display key findings
        report = results.get('report', {}).get('report', {})
        findings = report.get('findings', [])
        
        if findings:
            print()
            print("KEY FINDINGS:")
            print("-" * 40)
            for i, finding in enumerate(findings[:5], 1):
                print(f"{i}. {finding}")
        
        print()
        print(f"Research completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n⚠️  Research interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Research failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()