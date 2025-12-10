"""
Port scanning and service detection module.
Identifies open ports and detects running services.
"""

from typing import Dict, Any, List, Optional
import socket
import threading
from datetime import datetime

from src.collectors.base_collector import BaseCollector
from config.logging_config import get_logger
from config.constants import COMMON_PORTS

logger = get_logger(__name__)


class PortScanner(BaseCollector):
    """Scans ports and detects running services."""

    # Common ports with typical services
    SERVICE_FINGERPRINTS = {
        22: ("SSH", ["SSH-2.0", "SSH-1.99"]),
        25: ("SMTP", ["220"]),
        53: ("DNS", ["Query"]),
        80: ("HTTP", ["HTTP/1", "HTTP/2"]),
        110: ("POP3", ["OK", "+OK"]),
        143: ("IMAP", ["OK", "Innotech"]),
        443: ("HTTPS", ["HTTP/1", "HTTP/2"]),
        3306: ("MySQL", ["MySQL"]),
        3389: ("RDP", ["RDP"]),
        5432: ("PostgreSQL", ["PostgreSQL"]),
        5984: ("CouchDB", ["CouchDB"]),
        6379: ("Redis", ["Redis"]),
        8080: ("HTTP-Alt", ["HTTP"]),
        8443: ("HTTPS-Alt", ["HTTP"]),
        1433: ("MSSQL", ["MSSQLSERVER"]),
        27017: ("MongoDB", ["MongoDB"]),
    }

    def __init__(self, timeout: int = 20, max_threads: int = 10):
        """
        Initialize port scanner.

        Args:
            timeout: Timeout per port
            max_threads: Maximum concurrent threads
        """
        super().__init__(timeout=timeout)
        self.max_threads = max_threads

    def collect(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Scan target for open ports.

        Args:
            target: Target domain or IP
            **kwargs: Additional arguments (ports to scan)

        Returns:
            Dictionary with scan results
        """
        self._log_collection_start(target)

        try:
            # Extract host
            host = target.split("://")[-1].split(":")[0]

            # Determine ports to scan
            ports_to_scan = kwargs.get(
                "ports",
                list(self.SERVICE_FINGERPRINTS.keys()),
            )

            # Perform scan
            open_ports = self._scan_ports(host, ports_to_scan)

            # Analyze results
            services_detected = self._identify_services(host, open_ports)

            result = {
                "status": "success",
                "host": host,
                "ports_scanned": len(ports_to_scan),
                "open_ports": open_ports,
                "services_detected": services_detected,
                "scan_time": datetime.utcnow().isoformat(),
            }

            self._log_collection_end(target)
            return result

        except Exception as e:
            logger.error(f"Port scanning failed for {target}: {e}")
            self._log_collection_end(target, success=False)
            return {"status": "error", "error": str(e)}

    def _scan_ports(self, host: str, ports: List[int]) -> List[int]:
        """
        Scan ports on target host.

        Args:
            host: Target hostname or IP
            ports: List of ports to scan

        Returns:
            List of open ports
        """
        open_ports = []
        lock = threading.Lock()

        def scan_port(port: int):
            """Scan a single port."""
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)  # Individual port timeout
                result = sock.connect_ex((host, port))
                sock.close()

                if result == 0:
                    with lock:
                        open_ports.append(port)
            except Exception as e:
                logger.debug(f"Port {port} scan error: {e}")

        # Create threads
        threads = []
        for port in ports:
            thread = threading.Thread(target=scan_port, args=(port,))
            threads.append(thread)

            # Limit concurrent threads
            if len(threads) >= self.max_threads:
                for t in threads:
                    t.start()
                for t in threads:
                    t.join()
                threads = []

        # Join remaining threads
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        return sorted(open_ports)

    def _identify_services(
        self, host: str, open_ports: List[int]
    ) -> Dict[int, Dict[str, Any]]:
        """
        Identify services running on open ports.

        Args:
            host: Target host
            open_ports: List of open ports

        Returns:
            Dictionary mapping ports to service info
        """
        services = {}

        for port in open_ports:
            service_info = {
                "service_name": "Unknown",
                "banner": None,
                "fingerprint_match": False,
            }

            # Get known service
            if port in self.SERVICE_FINGERPRINTS:
                service_name, fingerprints = self.SERVICE_FINGERPRINTS[
                    port
                ]
                service_info["service_name"] = service_name

                # Try banner grabbing
                try:
                    banner = self._grab_banner(host, port)
                    service_info["banner"] = banner

                    # Check fingerprints
                    if any(fp.lower() in banner.lower() for fp in fingerprints):
                        service_info["fingerprint_match"] = True
                except Exception:
                    pass

            services[port] = service_info

        return services

    def _grab_banner(self, host: str, port: int) -> Optional[str]:
        """
        Attempt to grab banner from port.

        Args:
            host: Target host
            port: Target port

        Returns:
            Banner text or None
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((host, port))

            # Receive banner
            banner = sock.recv(1024)
            sock.close()

            return banner.decode("utf-8", errors="ignore").strip()
        except Exception:
            return None
