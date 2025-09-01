#!/usr/bin/env python3
"""
Base category class for domain blocklist categories.
"""

import json
import os
import sys
from abc import ABC, abstractmethod

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import DomainFetcher, DomainProcessor, get_jakarta_time

class BaseCategory(ABC):
    """Base class for all domain blocklist categories"""
    
    def __init__(self, category_name, config_path=None):
        if config_path is None:
            # Get the directory of this file and construct path to config.json
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, "config.json")
        self.category_name = category_name
        self.config_path = config_path
        self.config = self._load_config()
        self.category_config = self.config["categories"].get(category_name, {})
        self.global_config = self.config.get("global_settings", {})
        
        # Initialize core components
        self.fetcher = DomainFetcher(timeout=self.global_config.get("timeout", 15))
        self.processor = DomainProcessor()
    
    def _load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load config from {self.config_path}: {e}")
            return {"categories": {}, "global_settings": {}}
    
    @property
    def name(self):
        """Get category display name"""
        return self.category_config.get("name", self.category_name.title())
    
    @property
    def description(self):
        """Get category description"""
        return self.category_config.get("description", f"{self.name} domain blocklist")
    
    @property
    def output_file(self):
        """Get output filename"""
        return self.category_config.get("output_file", f"{self.category_name}.txt")
    
    @property
    def output_path(self):
        """Get full output file path"""
        output_dir = self.global_config.get("output_directory", "blocklist")
        # Make sure we use the correct relative path from script directory
        if not os.path.isabs(output_dir):
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            parent_dir = os.path.dirname(script_dir)
            output_dir = os.path.join(parent_dir, output_dir)
        return os.path.join(output_dir, self.output_file)
    
    @property
    def stats_path(self):
        """Get stats file path"""
        stats_dir = self.global_config.get("stats_directory", "blocklist/stats")
        # Make sure we use the correct relative path from script directory
        if not os.path.isabs(stats_dir):
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            parent_dir = os.path.dirname(script_dir)
            stats_dir = os.path.join(parent_dir, stats_dir)
        return os.path.join(stats_dir, f"{self.category_name}.json")
    
    @property
    def sources(self):
        """Get sources dictionary"""
        return self.category_config.get("sources", {})
    
    @property
    def priority_keywords(self):
        """Get priority keywords list"""
        return self.category_config.get("priority_keywords", [])
    
    def fetch_domains(self):
        """
        Fetch domains from all configured sources
        
        Returns:
            tuple: (raw_domains, source_stats)
        """
        print(f"[INFO] Fetching domains for category: {self.name}")
        return self.fetcher.fetch_multiple_sources(self.sources)
    
    def process_domains(self, raw_domains, source_name=None):
        """
        Process raw domains into normalized and priority sets

        Args:
            raw_domains (list): List of raw domain strings
            source_name (str, optional): Name of the source for specific handling

        Returns:
            tuple: (normalized_domains, priority_domains)
        """
        return self.processor.process_domains(raw_domains, self.priority_keywords, source_name)
    
    def load_existing_domains(self):
        """Load existing domains from output file"""
        return self.processor.load_existing_domains(self.output_path)
    
    def merge_domains(self, existing_domains, new_domains, priority_domains):
        """Merge existing and new domains"""
        return self.processor.merge_domains(existing_domains, new_domains, priority_domains)
    
    def build_blocklist(self):
        """
        Build complete blocklist for this category
        
        Returns:
            dict: Statistics about the build process
        """
        print(f"[INFO] Building blocklist for category: {self.name}")
        
        # Ensure output directories exist
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.stats_path), exist_ok=True)
        
        # Load existing domains
        existing_domains = self.load_existing_domains()
        
        # Fetch new domains
        raw_domains, source_stats = self.fetch_domains()

        # Process domains
        normalized_domains, priority_domains = self.process_domains(raw_domains)

        # Update source stats with processing info
        for source_name, stats in source_stats.items():
            if stats['status'] == 'success':
                # Calculate domains from this specific source
                source_domains, source_priority = self.process_domains(
                    self.fetcher.fetch_source(source_name, stats['url'])[1],
                    source_name
                )
                stats.update({
                    'total_normalized': len(source_domains),
                    'priority_count': len(source_priority)
                })
        
        # Merge domains
        final_domains_list, merge_stats = self.merge_domains(
            existing_domains, normalized_domains, priority_domains
        )
        
        # Save domains to file
        self._save_domains(final_domains_list)
        
        # Prepare overall stats
        overall_stats = {
            'category': self.category_name,
            'name': self.name,
            'description': self.description,
            'last_updated': get_jakarta_time().isoformat(),
            'output_file': self.output_file,
            'total_sources': len(self.sources),
            'successful_sources': len([s for s in source_stats.values() if s['status'] == 'success']),
            'sources': source_stats,
            **merge_stats
        }
        
        # Save stats
        self._save_stats(overall_stats)
        
        print(f"[INFO] {self.name} blocklist completed: {merge_stats['total_count']:,} domains")
        return overall_stats
    
    def _save_domains(self, domains_list):
        """Save domains list to output file with header"""
        encoding = self.global_config.get("encoding", "utf-8")
        with open(self.output_path, "w", encoding=encoding) as f:
            # Write header
            f.write("/**\n")
            f.write("Lyra - Mapping the universe of threats\n")
            f.write(f"Category: {self.name}\n")
            f.write("Website: https://blog.intellibron.io/\n")
            f.write("Copyright 2025 ITSEC R&D\n")
            f.write("**/\n")
            f.write("\n")

            # Write domains
            for domain in domains_list:
                f.write(domain + "\n")
        print(f"[INFO] Saved {len(domains_list):,} domains to {self.output_path}")
    
    def _save_stats(self, stats):
        """Save statistics to JSON file"""
        encoding = self.global_config.get("encoding", "utf-8")
        with open(self.stats_path, "w", encoding=encoding) as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        print(f"[INFO] Saved statistics to {self.stats_path}")
    
    @abstractmethod
    def get_readme_content(self, stats):
        """
        Generate README content for this category
        
        Args:
            stats (dict): Statistics from build_blocklist()
            
        Returns:
            str: README content in markdown format
        """
        pass
