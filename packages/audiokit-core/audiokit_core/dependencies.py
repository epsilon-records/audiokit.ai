"""
Dependency monitoring system that checks for:
- Available updates
- Security vulnerabilities
- Compatibility issues
"""

import subprocess
import requests
from typing import Dict, Any
from pydantic import BaseModel
from rich.console import Console
from packaging.version import Version
import os
import json
from datetime import datetime, timedelta

console = Console()

class DependencyStatus(BaseModel):
    current_version: str
    latest_version: str
    security_status: str
    compatibility_risk: bool

def get_installed_dependencies() -> Dict[str, str]:
    """Get currently installed dependencies using Poetry"""
    result = subprocess.run(['poetry', 'show'], capture_output=True, text=True)
    deps = {}
    for line in result.stdout.split('\n'):
        if ' ' in line:
            pkg, version = line.split(' ', 1)
            deps[pkg] = version.strip()
    return deps

def check_pypi_versions(package: str) -> str:
    """Check PyPI for latest version"""
    try:
        response = requests.get(f'https://pypi.org/pypi/{package}/json', timeout=3)
        return response.json()['info']['version']
    except Exception as e:
        console.print(f"[yellow]Warning: Could not check PyPI for {package} - {str(e)}[/]")
        return "unknown"

CVE_CACHE_DIR = ".cve_cache"
CACHE_EXPIRY_HOURS = 24
MAX_CACHE_SIZE_MB = 100  # 100MB max cache size
MAX_CACHE_FILES = 200    # Max number of cache files to retain

def _get_cache_path(package: str) -> str:
    os.makedirs(CVE_CACHE_DIR, exist_ok=True)
    return os.path.join(CVE_CACHE_DIR, f"{package}.json")

def _read_cache(package: str) -> dict:
    cache_path = _get_cache_path(package)
    try:
        with open(cache_path, 'r') as f:
            data = json.load(f)
            if datetime.fromisoformat(data['timestamp']) > datetime.now() - timedelta(hours=CACHE_EXPIRY_HOURS):
                return data
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        pass
    return None

def _clean_cache():
    """Enforce cache size limits by removing oldest files"""
    try:
        # Get all cache files with timestamps
        files = []
        for f in os.listdir(CVE_CACHE_DIR):
            path = os.path.join(CVE_CACHE_DIR, f)
            if f.endswith('.json'):
                files.append((path, os.path.getmtime(path)))
        
        # Check size limits
        total_size = sum(os.path.getsize(f[0]) for f in files) / (1024*1024)
        if total_size < MAX_CACHE_SIZE_MB and len(files) < MAX_CACHE_FILES:
            return
        
        # Sort by modification time (oldest first)
        files.sort(key=lambda x: x[1])
        
        # Remove oldest files until under limits
        removed = 0
        for path, _ in files:
            if total_size >= MAX_CACHE_SIZE_MB or len(files)-removed > MAX_CACHE_FILES:
                os.remove(path)
                total_size -= os.path.getsize(path)/(1024*1024)
                removed += 1
            else:
                break
                
        console.print(f"[yellow]Cleaned {removed} old cache files[/]")
        
    except Exception as e:
        console.print(f"[red]Cache cleanup failed: {str(e)}[/]")

def _write_cache(package: str, cve_data: list):
    cache_path = _get_cache_path(package)
    try:
        with open(cache_path, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'cves': cve_data
            }, f)
        _clean_cache()  # Enforce size limits after write
    except IOError as e:
        console.print(f"[yellow]Warning: Failed to cache {package} - {str(e)}[/]")

def check_security(package: str, version: str) -> str:
    """Check for known vulnerabilities using NVD database with caching"""
    # Check cache first
    cached = _read_cache(package)
    if cached:
        return "\n  ".join(cached['cves']) if cached['cves'] else "No known vulnerabilities (cached)"
    
    # Proceed with API call if no cache
    try:
        response = requests.get(
            f"https://services.nvd.nist.gov/rest/json/cves/2.0",
            params={
                'keywordSearch': package,
                'versionStart': f'={version}',
                'versionStartType': 'including'
            },
            timeout=5
        )
        response.raise_for_status()
        
        cves = []
        for vuln in response.json().get('vulnerabilities', []):
            cve_id = vuln['cve']['id']
            descriptions = [d['value'] for d in vuln['cve']['descriptions'] 
                          if d['lang'] == 'en']
            cves.append(f"{cve_id}: {descriptions[0][:60]}..." if descriptions else cve_id)
        
        # Update cache
        _write_cache(package, cves)
        
        return "\n  ".join(cves) if cves else "No known vulnerabilities"
        
    except Exception as e:
        console.print(f"[red]Security check failed for {package}: {str(e)}[/]")
        return "Unknown security status"

def monitor_dependencies():
    """Main monitoring function"""
    deps = get_installed_dependencies()
    status_report = {}
    
    for pkg, version in deps.items():
        latest = check_pypi_versions(pkg)
        security = check_security(pkg, version)
        
        status_report[pkg] = DependencyStatus(
            current_version=version,
            latest_version=latest,
            security_status=security,
            compatibility_risk=False  # TODO: Implement compatibility checks
        )
    
    return status_report

def print_status_report(report: Dict[str, DependencyStatus]):
    """Display results using Rich"""
    console.print("\n[bold]Dependency Status Report[/]")
    for pkg, status in report.items():
        version_color = "green" if status.current_version == status.latest_version else "yellow"
        security_color = "green" if "No known" in status.security_status else "red"
        
        console.print(
            f"[bold]{pkg}[/] {status.current_version} → [{version_color}]{status.latest_version}[/]"
            f"\n  Security: [{security_color}]{status.security_status}[/]"
        ) 