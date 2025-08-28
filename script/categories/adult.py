#!/usr/bin/env python3
"""
Adult category implementation for domain blocklist.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from categories.base import BaseCategory
from core.utils import format_number, format_datetime

class AdultCategory(BaseCategory):
    """Adult domain blocklist category"""
    
    def __init__(self):
        super().__init__("adult")
    
    def get_readme_content(self, stats):
        """Generate README content for adult category"""
        
        last_updated = format_datetime(stats.get('last_updated', 'Unknown'))
        total_domains = stats.get('total_count', 0)
        total_sources = stats.get('total_sources', 0)
        successful_sources = stats.get('successful_sources', 0)
        added_this_run = stats.get('newly_added_count', 0)
        
        readme_content = f"""# 🚫 {stats.get('name', 'Adult')} Domain Blocklist

{stats.get('description', 'Adult domain blocklist')}

This list is cumulative; domains are only added and never removed to ensure a comprehensive blocklist.

## 📊 Statistics

- **Last Updated**: {last_updated}
- **Total Unique Domains**: {format_number(total_domains)}
- **Domains Added in Last Run**: {format_number(added_this_run)}
- **Sources**: {successful_sources}/{total_sources} active

## 📁 Files

- [`{stats.get('output_file', 'adult.txt')}`]({stats.get('output_file', 'adult.txt')}) - Main blocklist file (cumulative)
- [`stats/{self.category_name}.json`](stats/{self.category_name}.json) - Detailed statistics

## 🔍 Source Breakdown

| Source | Status | Raw Entries | Normalized | Last Updated |
|--------|--------|-------------|------------|--------------|
"""
        
        sources = stats.get('sources', {})
        for source_name, source_data in sources.items():
            status = "❌" if source_data.get('status') == 'error' else "✅"
            raw_count = format_number(source_data.get('total_raw', 0))
            normalized_count = format_number(source_data.get('total_normalized', 0))
            
            source_updated = format_datetime(source_data.get('last_updated', 'Unknown'))
            
            readme_content += f"| {source_name} | {status} | {raw_count} | {normalized_count} | {source_updated} |\n"
        
        readme_content += f"""
## 🔄 Auto Update

This blocklist is automatically updated using a modular system that can be extended for other categories.

## 🛠️ Technical Details

- **Format**: Plain text, one domain per line
- **Encoding**: UTF-8
- **Sorting**: Alphabetical order
- **Deduplication**: Automatic removal of duplicates
- **Cumulative**: Domains are never removed, only added

---

*Last updated: {last_updated}*  
*Generated automatically by modular blocklist system*
"""
        
        return readme_content
