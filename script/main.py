#!/usr/bin/env python3
"""
Main script for modular domain blocklist system.
"""

import sys
import os
import argparse
import json
from categories import GamblingCategory, SuspiciousCategory, MaliciousCategory, AdultCategory
from output import OutputGenerator, ReadmeGenerator

# Registry of available categories
CATEGORY_REGISTRY = {
    'gambling': GamblingCategory,
    'suspicious': SuspiciousCategory,
    'malicious': MaliciousCategory,
    'adult': AdultCategory
}

def get_available_categories():
    """Get list of available category names"""
    return list(CATEGORY_REGISTRY.keys())

def create_category(category_name):
    """
    Create category instance by name
    
    Args:
        category_name (str): Name of the category
        
    Returns:
        BaseCategory: Category instance or None if not found
    """
    category_class = CATEGORY_REGISTRY.get(category_name)
    if category_class:
        return category_class()
    return None

def process_category(category_name):
    """
    Process a single category
    
    Args:
        category_name (str): Name of the category to process
        
    Returns:
        dict: Statistics from processing or None if failed
    """
    print(f"\n{'='*60}")
    print(f"Processing category: {category_name.upper()}")
    print(f"{'='*60}")
    
    try:
        # Create category instance
        category = create_category(category_name)
        if not category:
            print(f"[ERROR] Unknown category: {category_name}")
            print(f"Available categories: {', '.join(get_available_categories())}")
            return None
        
        # Build blocklist
        stats = category.build_blocklist()
        
        # Skip category README generation - only main README needed
        
        print(f"\n✅ {category.name} completed successfully!")
        print(f"📊 Total domains: {stats.get('total_count', 0):,}")
        print(f"➕ Domains added this run: {stats.get('newly_added_count', 0):,}")
        print(f"📡 Active sources: {stats.get('successful_sources', 0)}/{stats.get('total_sources', 0)}")
        
        return stats
        
    except Exception as e:
        print(f"\n❌ Error processing {category_name}: {e}")
        import traceback
        traceback.print_exc()
        return None

def process_all_categories():
    """
    Process all available categories
    
    Returns:
        list: List of statistics from all processed categories
    """
    all_stats = []
    
    for category_name in get_available_categories():
        stats = process_category(category_name)
        if stats:
            all_stats.append(stats)
    
    return all_stats

def generate_combined_output(all_stats):
    """
    Generate combined statistics and main README

    Args:
        all_stats (list): List of statistics from all categories
    """
    if not all_stats:
        print("[WARNING] No statistics available for combined output")
        return

    print(f"\n{'='*60}")
    print("Generating Combined Output")
    print(f"{'='*60}")

    try:
        # Generate combined statistics - save to parent directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)

        output_gen = OutputGenerator(
            output_dir=os.path.join(parent_dir, "blocklist"),
            stats_dir=os.path.join(parent_dir, "blocklist", "stats"),
            root_dir=parent_dir
        )
        combined_stats_path = output_gen.save_combined_stats(all_stats)

        # Load combined stats for README generation
        with open(combined_stats_path, 'r', encoding='utf-8') as f:
            combined_stats = json.load(f)

        # Generate main README in root directory
        readme_gen = ReadmeGenerator()
        main_readme_path = readme_gen.generate_main_readme(combined_stats, output_dir=parent_dir)

        print(f"\n✅ Combined output generated successfully!")
        print(f"📊 Combined stats: {combined_stats_path}")
        print(f"📖 Main README: {main_readme_path}")

    except Exception as e:
        print(f"\n❌ Error generating combined output: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Modular Domain Blocklist System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Available categories: {', '.join(get_available_categories())}

Examples:
  python main.py                    # Process all categories
  python main.py gambling           # Process only gambling category
  python main.py gambling --no-combined  # Skip combined output generation
        """
    )
    
    parser.add_argument(
        'category',
        nargs='?',
        help='Category to process (if not specified, all categories will be processed)'
    )
    
    parser.add_argument(
        '--no-combined',
        action='store_true',
        help='Skip combined statistics and main README generation'
    )
    
    parser.add_argument(
        '--list-categories',
        action='store_true',
        help='List available categories and exit'
    )
    
    args = parser.parse_args()
    
    # Handle list categories
    if args.list_categories:
        print("Available categories:")
        for cat_name in get_available_categories():
            category = create_category(cat_name)
            if category:
                print(f"  {cat_name}: {category.name} - {category.description}")
        return
    
    print("🚫 Modular Domain Blocklist System")
    print("=" * 60)
    
    all_stats = []
    
    try:
        if args.category:
            # Process single category
            if args.category not in get_available_categories():
                print(f"[ERROR] Unknown category: {args.category}")
                print(f"Available categories: {', '.join(get_available_categories())}")
                sys.exit(1)
            
            stats = process_category(args.category)
            if stats:
                all_stats.append(stats)
        else:
            # Process all categories
            all_stats = process_all_categories()
        
        # Generate combined output unless disabled
        if not args.no_combined and all_stats:
            generate_combined_output(all_stats)
        
        # Final summary
        if all_stats:
            print(f"\n🎉 System completed successfully!")
            print(f"📊 Processed {len(all_stats)} categories")
            total_domains = sum(stats.get('total_count', 0) for stats in all_stats)
            print(f"🌐 Total domains across all categories: {total_domains:,}")
        else:
            print(f"\n⚠️  No categories were processed successfully")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
