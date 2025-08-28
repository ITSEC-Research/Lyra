#!/usr/bin/env python3
"""
Domain fetcher module for retrieving blocklist data from various sources.
"""

import requests
from .utils import get_jakarta_time

class DomainFetcher:
    """Handles fetching domain data from various sources"""
    
    def __init__(self, timeout=15):
        self.timeout = timeout
    
    def fetch_source(self, name, url):
        """
        Fetch blocklist from a source URL
        
        Args:
            name (str): Name of the source
            url (str): URL to fetch from
            
        Returns:
            tuple: (success, data, stats)
                success (bool): Whether fetch was successful
                data (list): List of raw lines from source
                stats (dict): Statistics about the fetch
        """
        print(f"[INFO] Fetching from {name}...")
        
        stats = {
            'url': url,
            'total_raw': 0,
            'last_updated': get_jakarta_time().isoformat(),
            'status': 'error'
        }
        
        try:
            resp = requests.get(url, timeout=self.timeout)
            resp.raise_for_status()
            lines = resp.text.splitlines()
            
            stats.update({
                'total_raw': len(lines),
                'status': 'success'
            })
            
            print(f"[INFO] {name}: fetched {len(lines)} raw entries")
            return True, lines, stats
            
        except Exception as e:
            print(f"[ERROR] Failed to fetch {name}: {e}")
            return False, [], stats
    
    def fetch_multiple_sources(self, sources):
        """
        Fetch from multiple sources
        
        Args:
            sources (dict): Dictionary of source_name: url pairs
            
        Returns:
            tuple: (all_data, all_stats)
                all_data (list): Combined list of all raw lines
                all_stats (dict): Statistics for each source
        """
        all_data = []
        all_stats = {}
        
        for name, url in sources.items():
            success, data, stats = self.fetch_source(name, url)
            all_stats[name] = stats
            if success:
                all_data.extend(data)
        
        return all_data, all_stats
