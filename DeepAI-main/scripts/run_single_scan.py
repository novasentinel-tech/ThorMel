"""
Example: Single domain scan.
Demonstrates complete pipeline usage.

Usage:
    python scripts/run_single_scan.py google.com
    python scripts/run_single_scan.py https://google.com
    python scripts/run_single_scan.py https://qqtechs.com.br/qqtech/login/index.php
"""

import sys
from pathlib import Path
from urllib.parse import urlparse

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.logging_config import get_logger
from src.security import domain_validator, rate_limiter, audit_log
from src.pipeline import ScanPipeline

logger = get_logger(__name__)


def extract_domain_from_url(url_or_domain: str) -> str:
    """
    Extract domain from URL or return domain as-is.
    
    Examples:
        https://google.com -> google.com
        https://qqtechs.com.br/qqtech/login/index.php -> qqtechs.com.br
        google.com -> google.com
        http://example.com:8080 -> example.com
    
    Args:
        url_or_domain: URL or domain name
        
    Returns:
        Extracted domain name
    """
    # Remove whitespace
    url_or_domain = url_or_domain.strip()
    
    # If it looks like a URL (has protocol), parse it
    if "://" in url_or_domain:
        try:
            parsed = urlparse(url_or_domain)
            domain = parsed.netloc  # Gets domain:port if port exists
            
            # Remove port if present
            if ":" in domain:
                domain = domain.split(":")[0]
            
            return domain
        except Exception as e:
            logger.warning(f"Error parsing URL: {e}. Using as-is: {url_or_domain}")
            return url_or_domain
    
    # Remove port if present (e.g., "example.com:8080" -> "example.com")
    if ":" in url_or_domain and "/" not in url_or_domain:
        url_or_domain = url_or_domain.split(":")[0]
    
    # Remove path if present (e.g., "example.com/path" -> "example.com")
    if "/" in url_or_domain:
        url_or_domain = url_or_domain.split("/")[0]
    
    return url_or_domain


def scan_domain(domain: str, user_ip: str = "127.0.0.1") -> dict:
    """
    Scan a single domain end-to-end.
    
    Args:
        domain: Target domain to scan
        user_ip: User's IP address (for rate limiting)
        
    Returns:
        Complete analysis result
    """
    
    logger.info(f"Starting scan for {domain}")
    
    # STEP 1: Validate domain
    try:
        domain_validator.validate_strict(domain)
        logger.info(f"Domain {domain} passed validation")
    except Exception as e:
        logger.error(f"Domain validation failed: {e}")
        return {"status": "blocked", "error": str(e)}
    
    # STEP 2: Check rate limits
    try:
        rate_limiter.check_and_raise(user_ip, domain)
        logger.info(f"Rate limits OK for {user_ip}")
    except Exception as e:
        logger.error(f"Rate limit exceeded: {e}")
        return {"status": "rate_limited", "error": str(e)}
    
    # STEP 3: Log audit event
    audit_log.log_event(
        event_type="scan_initiated",
        details={
            "target": domain,
            "user_ip": user_ip,
            "validation": "passed"
        }
    )
    
    # STEP 4: Run analysis pipeline
    try:
        pipeline = ScanPipeline()
        result = pipeline.analyze(domain)
        
        # STEP 5: Log result
        audit_log.log_event(
            event_type="scan_completed",
            details={
                "target": domain,
                "classification": result.get("classification"),
                "confidence": result.get("confidence")
            }
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        
        audit_log.log_event(
            event_type="scan_failed",
            details={
                "target": domain,
                "error": str(e)
            }
        )
        
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    import json
    import argparse
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Scan a domain or URL for security analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_single_scan.py google.com
  python scripts/run_single_scan.py https://google.com
  python scripts/run_single_scan.py https://qqtechs.com.br/qqtech/login/index.php
  python scripts/run_single_scan.py example.com --verbose
        """
    )
    
    parser.add_argument(
        "target",
        nargs="?",
        default="example.com",
        help="Domain or URL to scan (default: example.com)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--output-html",
        type=str,
        help="Save HTML report to file"
    )
    
    args = parser.parse_args()
    
    # Extract domain from URL or use as-is
    target_input = args.target
    domain = extract_domain_from_url(target_input)
    
    logger.info(f"Input: {target_input}")
    logger.info(f"Extracted domain: {domain}")
    
    # Run scan
    print("\n" + "="*70)
    print(f"🔍 SCANNING: {target_input}")
    print(f"📍 Domain extracted: {domain}")
    print("="*70 + "\n")
    
    result = scan_domain(domain)
    
    print("\n" + "="*70)
    print(f"✅ SCAN RESULT FOR: {domain}")
    print("="*70)
    print(json.dumps(result, indent=2, default=str))
    print("="*70 + "\n")
    
    # Optionally save HTML report
    if args.output_html:
        try:
            # Simple HTML report generation
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>DeepAI Security Report - {domain}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; background: #ecf0f1; border-radius: 5px; }}
        .low {{ background: #d4edda; }}
        .medium {{ background: #fff3cd; }}
        .high {{ background: #f5c6cb; }}
        .critical {{ background: #f8d7da; }}
        pre {{ background: #f5f5f5; padding: 10px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔒 DeepAI Security Analysis Report</h1>
        <p>Domain: <strong>{domain}</strong></p>
        <p>Generated: {__import__('datetime').datetime.now().isoformat()}</p>
    </div>
    
    <div class="section">
        <h2>Analysis Results</h2>
        <pre>{json.dumps(result, indent=2, default=str)}</pre>
    </div>
</body>
</html>
            """
            
            with open(args.output_html, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            print(f"✅ HTML report saved to: {args.output_html}\n")
        except Exception as e:
            logger.error(f"Failed to save HTML report: {e}")
