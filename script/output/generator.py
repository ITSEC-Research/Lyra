#!/usr/bin/env python3
"""
Output generator for domain blocklist files and statistics.
"""

import os
import json
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils import get_jakarta_time

class OutputGenerator:
    """Handles generation of output files and statistics"""
    
    def __init__(self, output_dir="blocklist", stats_dir="blocklist/stats", encoding="utf-8", root_dir="."):
        self.output_dir = output_dir
        self.stats_dir = stats_dir
        self.encoding = encoding
        self.root_dir = root_dir
        
        # Ensure directories exist
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(stats_dir, exist_ok=True)
    
    def save_domains(self, domains_list, filename):
        """
        Save domains list to a file
        
        Args:
            domains_list (list): List of domains to save
            filename (str): Output filename
            
        Returns:
            str: Full path to saved file
        """
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, "w", encoding=self.encoding) as f:
            for domain in domains_list:
                f.write(domain + "\n")
        
        print(f"[INFO] Saved {len(domains_list):,} domains to {filepath}")
        return filepath
    
    def save_stats(self, stats, category_name):
        """
        Save statistics to JSON file
        
        Args:
            stats (dict): Statistics dictionary
            category_name (str): Category name for filename
            
        Returns:
            str: Full path to saved stats file
        """
        filename = f"{category_name}.json"
        filepath = os.path.join(self.stats_dir, filename)
        
        with open(filepath, "w", encoding=self.encoding) as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"[INFO] Saved statistics to {filepath}")
        return filepath
    
    def load_stats(self, category_name):
        """
        Load statistics from JSON file
        
        Args:
            category_name (str): Category name
            
        Returns:
            dict: Statistics dictionary or empty dict if not found
        """
        filename = f"{category_name}.json"
        filepath = os.path.join(self.stats_dir, filename)
        
        if not os.path.exists(filepath):
            return {}
        
        try:
            with open(filepath, "r", encoding=self.encoding) as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load stats from {filepath}: {e}")
            return {}
    
    def generate_combined_stats(self, category_stats_list):
        """
        Generate combined statistics from multiple categories
        
        Args:
            category_stats_list (list): List of category statistics
            
        Returns:
            dict: Combined statistics
        """
        combined_stats = {
            'last_updated': get_jakarta_time().isoformat(),
            'total_categories': len(category_stats_list),
            'categories': {},
            'summary': {
                'total_domains': 0,
                'total_sources': 0,
                'successful_sources': 0
            }
        }
        
        for stats in category_stats_list:
            category_name = stats.get('category', 'unknown')
            combined_stats['categories'][category_name] = {
                'name': stats.get('name', category_name.title()),
                'description': stats.get('description', ''),
                'total_domains': stats.get('total_count', 0),
                'sources': stats.get('total_sources', 0),
                'successful_sources': stats.get('successful_sources', 0),
                'last_updated': stats.get('last_updated', ''),
                'output_file': stats.get('output_file', f'{category_name}.txt')
            }
            
            # Update summary
            combined_stats['summary']['total_domains'] += stats.get('total_count', 0)
            combined_stats['summary']['total_sources'] += stats.get('total_sources', 0)
            combined_stats['summary']['successful_sources'] += stats.get('successful_sources', 0)
        
        return combined_stats
    
    def save_combined_stats(self, category_stats_list):
        """
        Save combined statistics for all categories
        
        Args:
            category_stats_list (list): List of category statistics
            
        Returns:
            str: Path to saved combined stats file
        """
        combined_stats = self.generate_combined_stats(category_stats_list)
        filepath = os.path.join(self.stats_dir, "combined.json")
        
        with open(filepath, "w", encoding=self.encoding) as f:
            json.dump(combined_stats, f, indent=2, ensure_ascii=False)
        
        print(f"[INFO] Saved combined statistics to {filepath}")
        return filepath
