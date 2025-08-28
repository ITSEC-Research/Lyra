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

        readme_content += f"""

---

*Last updated: {last_updated}*
*Generated automatically by Lyra - Mapping the universe of threats*
"""
        
        readme_path = os.path.join(output_dir, "README.md")
        with open(readme_path, "w", encoding=self.encoding) as f:
            f.write(readme_content)
        
        print(f"[INFO] Generated main README: {readme_path}")
        return readme_path
