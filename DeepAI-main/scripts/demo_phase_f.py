#!/usr/bin/env python
"""
Complete DeepAI Pipeline Demonstration
Demonstrates full system integration from data collection to explainability
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

from src.pipeline.integrated_pipeline import IntegratedPipeline

# Configure logging
logger.enable("src")


def main():
    """Run complete pipeline demonstration."""
    
    logger.info("=" * 80)
    logger.info("DeepAI Complete Security Analysis System - Demonstration")
    logger.info("=" * 80)
    
    # Initialize pipeline
    logger.info("\n[1/3] Initializing integrated pipeline...")
    pipeline = IntegratedPipeline()
    
    # Test domains for demonstration
    test_domains = [
        "example.com",
        "google.com",
        "github.com",
    ]
    
    # Analyze domains
    logger.info(f"\n[2/3] Analyzing {len(test_domains)} domains...")
    results = pipeline.analyze_batch(
        test_domains,
        generate_reports=True,
        report_dir=Path("data/reports")
    )
    
    # Summary and export
    logger.info("\n[3/3] Generating summary report...")
    
    successful = sum(1 for r in results if r.status == "success")
    failed = len(results) - successful
    
    logger.info(f"\n{'='*80}")
    logger.info("ANALYSIS SUMMARY")
    logger.info(f"{'='*80}")
    logger.info(f"Total domains analyzed: {len(results)}")
    logger.info(f"Successful: {successful}")
    logger.info(f"Failed: {failed}")
    
    if results:
        total_time = sum(r.total_time for r in results)
        avg_time = total_time / len(results)
        logger.info(f"Total time: {total_time:.2f}s")
        logger.info(f"Average per domain: {avg_time:.2f}s")
    
    # Export detailed results
    output_file = Path("data/results") / f"analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    results_data = [r.to_dict() for r in results]
    with open(output_file, 'w') as f:
        json.dump(results_data, f, indent=2)
    
    logger.info(f"\nDetailed results exported to: {output_file}")
    
    # Print sample result
    if results and results[0].status == "success":
        logger.info(f"\nSample Analysis Result for {results[0].domain}:")
        logger.info(f"  - ML Prediction: {results[0].ml_prediction}")
        logger.info(f"  - ML Confidence: {results[0].ml_score:.3f}")
        logger.info(f"  - Features Analyzed: {results[0].collected_features}")
        logger.info(f"  - Total Analysis Time: {results[0].total_time:.3f}s")
        if results[0].html_report_path:
            logger.info(f"  - HTML Report: {results[0].html_report_path}")
    
    logger.info(f"\n{'='*80}")
    logger.info("✓ Demonstration completed successfully!")
    logger.info(f"{'='*80}")


if __name__ == '__main__':
    main()
