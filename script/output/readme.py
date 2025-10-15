#!/usr/bin/env python3
"""
README generator for domain blocklist documentation.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils import format_number, format_datetime

class ReadmeGenerator:
    """Handles generation of README files for categories and main project"""
    
    def __init__(self, encoding="utf-8"):
        self.encoding = encoding
    
    def generate_category_readme(self, category, stats, output_dir="blocklist"):
        """
        Generate README for a specific category
        
        Args:
            category: Category instance with get_readme_content method
            stats (dict): Category statistics
            output_dir (str): Output directory for README
            
        Returns:
            str: Path to generated README file
        """
        readme_content = category.get_readme_content(stats)
        
        # Save to category-specific README
        readme_filename = f"README_{category.category_name}.md"
        readme_path = os.path.join(output_dir, readme_filename)
        
        with open(readme_path, "w", encoding=self.encoding) as f:
            f.write(readme_content)
        
        print(f"[INFO] Generated README for {category.name}: {readme_path}")
        return readme_path
    
    def generate_main_readme(self, combined_stats, output_dir="."):
        """
        Generate main project README
        
        Args:
            combined_stats (dict): Combined statistics from all categories
            output_dir (str): Output directory for main README
            
        Returns:
            str: Path to generated main README file
        """
        last_updated = format_datetime(combined_stats.get('last_updated', 'Unknown'))
        total_categories = combined_stats.get('total_categories', 0)
        summary = combined_stats.get('summary', {})
        categories = combined_stats.get('categories', {})
        
        readme_content = f"""# 🌌 Lyra - Mapping the universe of threats

From scattered stars to a unified galaxy, collects and harmonizes blocklists from across the public universe, creating a singular, clean, and unique list.

## 📊 Overview Statistics

- **Last Updated**: {last_updated}
- **Total Categories**: {total_categories}
- **Total Domains**: {format_number(summary.get('total_domains', 0))}
- **Total Sources**: {summary.get('total_sources', 0)}
- **Active Sources**: {summary.get('successful_sources', 0)}

## 📂 Available Categories

| Category | Domains | Sources | Status | File |
|----------|---------|---------|--------|------|
"""

        for category_name, category_data in categories.items():
            name = category_data.get('name', category_name.title())
            domains_count = format_number(category_data.get('total_domains', 0))
            sources_status = f"{category_data.get('successful_sources', 0)}/{category_data.get('sources', 0)}"
            status = "✅ Active" if category_data.get('successful_sources', 0) > 0 else "❌ Inactive"
            output_file = category_data.get('output_file', f'{category_name}.txt')

            readme_content += f"| {name} | {domains_count} | {sources_status} | {status} | [`{output_file}`](blocklist/{output_file}) |\n"

        # Generate unique sources list from all categories
        unique_sources = self._extract_unique_sources(categories)
        sources_text = ", ".join(unique_sources)

        readme_content += f"""

## 📚 Sources

{sources_text}

---

*Last updated: {last_updated}*
*Generated automatically by Lyra - Mapping the universe of threats*
"""
        
        readme_path = os.path.join(output_dir, "README.md")
        with open(readme_path, "w", encoding=self.encoding) as f:
            f.write(readme_content)
        
        print(f"[INFO] Generated main README: {readme_path}")
        return readme_path

    def _extract_unique_sources(self, categories):
        """
        Extract unique sources from all categories (hardcoded)

        Args:
            categories (dict): Dictionary of category data

        Returns:
            list: List of unique source names with links
        """
        # Hardcoded unique sources list
        sources = [
            "[Hagezi DNS Blocklists](https://github.com/hagezi/dns-blocklists)",
            "[Steven Black Hosts](https://github.com/StevenBlack/hosts)",
            "[Blocklist Project](https://blocklistproject.github.io/)",
            "[MajkiIT Polish Filters](https://github.com/MajkiIT/polish-ads-filter)",
            "[ShadowWhisperer BlockLists](https://github.com/ShadowWhisperer/BlockLists)",
            "[TrustPositif Indonesia](https://github.com/alsyundawy/TrustPositif)",
            "[OISD Blocklist](https://oisd.nl/)",
            "[OpenPhish](https://openphish.com/)",
            "[CERT.PL](https://cert.pl/)",
            "[Spam404](https://github.com/Spam404/lists)",
            "[Malware-Filter Project](https://gitlab.com/malware-filter/malware-filter)",
            "[Firebog](https://firebog.net/)",
            "[Abuse.ch](https://abuse.ch/)",
            "[AdGuard DNS Filter](https://github.com/AdguardTeam/AdGuardSDNSFilter)",
            "[AWAvenue Ads Rule](https://github.com/TG-Twilight/AWAvenue-Ads-Rule)",
            "[Peter Lowe's Ad Server List](https://pgl.yoyo.org/adservers/)",
            "[1Hosts](https://github.com/badmojr/1Hosts)",
            "[Dan Pollock's Hosts](https://someonewhocares.org/hosts/)",
            "[ABPindo](https://github.com/ABPindo/indonesianadblockrules)"
        ]

        return sources
