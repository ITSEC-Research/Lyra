#!/usr/bin/env python3
"""
Domain processor module for normalizing, validating, and processing domains.
"""

import re
import os

class DomainProcessor:
    """Handles domain processing, validation, and management"""
    
    def __init__(self):
        self.domain_regex = re.compile(r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)\.[A-Za-z]{2,}$")
    
    def normalize_domain(self, domain, source_name=None):
        """
        Normalize domain format with source-specific handling

        Args:
            domain (str): Raw domain string
            source_name (str, optional): Name of the source for specific handling

        Returns:
            str: Normalized domain or empty string if invalid
        """
        if not domain or not isinstance(domain, str):
            return ""

        domain = domain.strip().lower()

        # Skip comments and empty lines
        if not domain or domain.startswith('#') or domain.startswith('!') or domain.startswith(';'):
            return ""

        # Handle CSV format (like PhishTank)
        if source_name and 'phishtank' in source_name and ',' in domain:
            parts = domain.split(',')
            if len(parts) > 1:
                # PhishTank CSV: phish_id,url,phish_detail_url,submission_time,verified,verification_time,online,target
                url = parts[1].strip('"')
                if url.startswith('http'):
                    from urllib.parse import urlparse
                    try:
                        parsed = urlparse(url)
                        domain = parsed.netloc
                    except:
                        return ""
                else:
                    domain = url

        # Handle AdGuard filter format
        if domain.startswith('||') and domain.endswith('^'):
            domain = domain[2:-1]
        elif domain.startswith('||'):
            domain = domain[2:]

        # Handle hosts file format (0.0.0.0 domain.com or 127.0.0.1 domain.com)
        if domain.startswith(("0.0.0.0", "127.0.0.1", "::1", "localhost")):
            parts = domain.split()
            domain = parts[1] if len(parts) > 1 else ""

        # Remove various adblock format markers
        domain = domain.lstrip("|").rstrip("^")
        domain = domain.lstrip("*.").lstrip(".")

        # Remove protocol prefixes
        if domain.startswith(("http://", "https://", "ftp://")):
            from urllib.parse import urlparse
            try:
                parsed = urlparse(domain if domain.startswith(('http://', 'https://')) else 'http://' + domain)
                domain = parsed.netloc
            except:
                pass

        # Remove port numbers
        if ':' in domain and not domain.count(':') > 1:  # Not IPv6
            domain = domain.split(':')[0]

        # Remove path and query parameters
        if '/' in domain:
            domain = domain.split('/')[0]
        if '?' in domain:
            domain = domain.split('?')[0]

        # Clean up any remaining unwanted characters
        domain = domain.strip('.,;:!@#$%^&*()[]{}"\' \t\n\r')

        return domain
    
    def is_valid_domain(self, domain):
        """
        Check if domain is valid
        
        Args:
            domain (str): Domain to validate
            
        Returns:
            bool: True if domain is valid
        """
        return bool(self.domain_regex.search(domain))
    
    def has_priority_keywords(self, domain, keywords):
        """
        Check if domain contains priority keywords
        
        Args:
            domain (str): Domain to check
            keywords (list): List of keywords to search for
            
        Returns:
            bool: True if domain contains any priority keyword
        """
        return any(keyword in domain for keyword in keywords)
    
    def process_domains(self, raw_domains, priority_keywords=None, source_name=None):
        """
        Process and normalize a list of raw domains with source-specific handling

        Args:
            raw_domains (list): List of raw domain strings
            priority_keywords (list, optional): Keywords for priority domains
            source_name (str, optional): Name of the source for specific handling

        Returns:
            tuple: (normalized_domains, priority_domains)
                normalized_domains (set): Set of all valid normalized domains
                priority_domains (set): Set of domains with priority keywords
        """
        normalized_domains = set()
        priority_domains = set()

        for raw_domain in raw_domains:
            domain = self.normalize_domain(raw_domain, source_name)
            if domain and self.is_valid_domain(domain):
                normalized_domains.add(domain)

                if priority_keywords and self.has_priority_keywords(domain, priority_keywords):
                    priority_domains.add(domain)

        return normalized_domains, priority_domains
    
    def load_existing_domains(self, filepath):
        """
        Load existing domains from a file
        
        Args:
            filepath (str): Path to the existing domains file
            
        Returns:
            set: Set of existing domains
        """
        if not os.path.exists(filepath):
            print(f"[INFO] File {filepath} not found. Starting fresh.")
            return set()
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                domains = {line.strip() for line in f if line.strip()}
            print(f"[INFO] Loaded {len(domains):,} existing domains from {filepath}")
            return domains
        except Exception as e:
            print(f"[ERROR] Could not read existing file {filepath}: {e}")
            return set()
    
    def merge_domains(self, existing_domains, new_domains, priority_domains=None):
        """
        Merge existing and new domains with alphabetical sorting

        Args:
            existing_domains (set): Set of existing domains
            new_domains (set): Set of new domains to add
            priority_domains (set, optional): Set of priority domains (ignored for general sorting)

        Returns:
            tuple: (final_domains_list, merge_stats)
                final_domains_list (list): Sorted list of all domains
                merge_stats (dict): Statistics about the merge
        """
        # Merge all domains
        all_domains = existing_domains.union(new_domains)
        newly_added = new_domains - existing_domains

        # Sort alphabetically (no priority)
        final_domains_list = sorted(list(all_domains))

        merge_stats = {
            'existing_count': len(existing_domains),
            'new_count': len(new_domains),
            'newly_added_count': len(newly_added),
            'total_count': len(all_domains),
            'priority_count': 0  # No priority domains
        }

        return final_domains_list, merge_stats
