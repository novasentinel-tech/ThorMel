#!/usr/bin/env python3
"""
Phase A Collectors - Exemplo de uso integrado.
Demonstra como usar todos os 6 coletores de dados.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from datetime import datetime

from src.collectors.http_collector import HTTPHeadersCollector
from src.collectors.tls_collector import TLSCollector
from src.collectors.dns_collector import DNSCollector
from src.collectors.whois_collector import WHOISCollector
from src.collectors.port_scanner import PortScanner
from src.collectors.tech_stack_detector import TechStackDetector
from config.logging_config import get_logger

logger = get_logger(__name__)


def run_comprehensive_scan(target: str, verbose: bool = True) -> dict:
    """
    Run all Phase A collectors on target.

    Args:
        target: Target domain or URL
        verbose: Enable verbose output

    Returns:
        Dictionary with all collector results
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"DeepAI Phase A - Comprehensive Scan")
        print(f"Target: {target}")
        print(f"Started: {datetime.now().isoformat()}")
        print(f"{'='*70}\n")

    results = {
        "target": target,
        "timestamp": datetime.now().isoformat(),
        "collectors": {},
    }

    # 1. HTTP Headers Collector
    if verbose:
        print("[1/6] Running HTTP Headers Collector...")
    try:
        http_collector = HTTPHeadersCollector()
        http_results = http_collector.collect(target)
        results["collectors"]["http"] = http_results
        if verbose:
            print(f"      ✓ Status: {http_results.get('status')}")
    except Exception as e:
        logger.error(f"HTTP collector failed: {e}")
        results["collectors"]["http"] = {"status": "error", "error": str(e)}

    # 2. TLS Collector
    if verbose:
        print("[2/6] Running TLS/SSL Inspector...")
    try:
        tls_collector = TLSCollector()
        tls_results = tls_collector.collect(target)
        results["collectors"]["tls"] = tls_results
        if verbose:
            print(f"      ✓ Status: {tls_results.get('status')}")
    except Exception as e:
        logger.error(f"TLS collector failed: {e}")
        results["collectors"]["tls"] = {"status": "error", "error": str(e)}

    # 3. DNS Collector
    if verbose:
        print("[3/6] Running DNS Records Analyzer...")
    try:
        dns_collector = DNSCollector()
        dns_results = dns_collector.collect(target)
        results["collectors"]["dns"] = dns_results
        if verbose:
            print(f"      ✓ Status: {dns_results.get('status')}")
    except Exception as e:
        logger.error(f"DNS collector failed: {e}")
        results["collectors"]["dns"] = {"status": "error", "error": str(e)}

    # 4. WHOIS Collector
    if verbose:
        print("[4/6] Running WHOIS Information Collector...")
    try:
        whois_collector = WHOISCollector(use_cache=True)
        whois_results = whois_collector.collect(target)
        results["collectors"]["whois"] = whois_results
        if verbose:
            print(f"      ✓ Status: {whois_results.get('status')}")
    except Exception as e:
        logger.error(f"WHOIS collector failed: {e}")
        results["collectors"]["whois"] = {"status": "error", "error": str(e)}

    # 5. Port Scanner
    if verbose:
        print("[5/6] Running Port Scanner...")
    try:
        port_scanner = PortScanner()
        port_results = port_scanner.collect(target)
        results["collectors"]["ports"] = port_results
        if verbose:
            print(f"      ✓ Status: {port_results.get('status')}")
            if port_results.get("open_ports"):
                print(f"      ✓ Open ports found: {port_results['open_ports']}")
    except Exception as e:
        logger.error(f"Port scanner failed: {e}")
        results["collectors"]["ports"] = {"status": "error", "error": str(e)}

    # 6. Tech Stack Detector
    if verbose:
        print("[6/6] Running Technology Stack Detector...")
    try:
        tech_detector = TechStackDetector()
        # Pass HTTP results if available for enhanced detection
        http_data = results["collectors"].get("http", {})
        tech_results = tech_detector.collect(target, http_data=http_data)
        results["collectors"]["tech_stack"] = tech_results
        if verbose:
            print(f"      ✓ Status: {tech_results.get('status')}")
            if tech_results.get("detected_technologies"):
                print(
                    f"      ✓ Technologies: {tech_results['detected_technologies']}"
                )
    except Exception as e:
        logger.error(f"Tech stack detector failed: {e}")
        results["collectors"]["tech_stack"] = {"status": "error", "error": str(e)}

    if verbose:
        print(f"\n{'='*70}")
        print(f"Scan completed: {datetime.now().isoformat()}")
        print(f"{'='*70}\n")

    return results


def print_summary(results: dict) -> None:
    """
    Print summary of scan results.

    Args:
        results: Results dictionary from run_comprehensive_scan
    """
    print("\n" + "="*70)
    print("SCAN SUMMARY")
    print("="*70)

    collectors = results.get("collectors", {})

    for col_name, col_results in collectors.items():
        status = col_results.get("status", "unknown")
        status_emoji = "✓" if status == "success" else "✗"
        print(f"{status_emoji} {col_name.upper()}: {status}")

        if status == "error":
            print(f"  Error: {col_results.get('error')}")
        elif status == "success":
            # Print key information per collector
            if col_name == "http":
                headers = col_results.get("security_headers", {})
                print(f"  Security headers found: {len(headers)}")

            elif col_name == "tls":
                print(f"  Protocol: {col_results.get('protocol_version')}")
                print(f"  Vulns: {col_results.get('vulnerabilities', [])}")

            elif col_name == "dns":
                dns_recs = col_results.get("dns_records", {})
                print(f"  DNS records: {len([r for r in dns_recs.values() if r])}")

            elif col_name == "whois":
                print(f"  Registrar: {col_results.get('registrar')}")
                exp_risk = col_results.get("expiration_risk")
                print(f"  Expiration risk: {exp_risk}")

            elif col_name == "ports":
                ports = col_results.get("open_ports", [])
                print(f"  Open ports: {ports}")

            elif col_name == "tech_stack":
                techs = col_results.get("detected_technologies", [])
                print(f"  Technologies: {len(techs)}")

    print("="*70 + "\n")


def export_results(results: dict, format: str = "json") -> str:
    """
    Export scan results to file.

    Args:
        results: Results dictionary
        format: Export format (json, csv, etc)

    Returns:
        Filename where results were saved
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = results["target"].replace(".", "_").replace("/", "_")

    if format == "json":
        filename = f"scan_result_{target}_{timestamp}.json"
        with open(filename, "w") as f:
            json.dump(results, f, indent=2)
        return filename

    return None


if __name__ == "__main__":
    # Example usage
    test_domains = [
        "example.com",
        # "google.com",
        # "github.com",
    ]

    for domain in test_domains:
        try:
            # Run scan
            results = run_comprehensive_scan(domain, verbose=True)

            # Print summary
            print_summary(results)

            # Export results
            # filename = export_results(results, format="json")
            # print(f"Results exported to: {filename}")

        except KeyboardInterrupt:
            print("\nScan interrupted by user")
            break
        except Exception as e:
            logger.error(f"Scan failed for {domain}: {e}")
