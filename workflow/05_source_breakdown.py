#!/usr/bin/env python3
"""
05_source_breakdown.py
Generate source-specific breakdown lists for apoptotic genes.

This script creates separate CSV files for each data source (KEGG, Reactome,
MSigDB Hallmark, GO), preserving the consensus functional categorization
(Pro-apoptotic, Anti-apoptotic, Ambiguous, Unspecified) and all identifiers.

Author: K-Dense Coding Agent
Date: 2026-01-27
"""

import pandas as pd
from pathlib import Path
import json
from datetime import datetime

# Configuration
BASE_DIR = Path("/app/sandbox/session_20260126_235914_ecc6fdd54e23")
RESULTS_DIR = BASE_DIR / "results"
INPUT_FILE = RESULTS_DIR / "final_apoptotic_gene_list.csv"
OUTPUT_DIR = RESULTS_DIR / "source_breakdown"

# Source detection patterns
SOURCE_PATTERNS = {
    "KEGG": "KEGG",
    "Reactome": "Reactome",
    "Hallmark": "Hallmark",
    "GO": "GO_"  # Matches GO_Anti_Human and GO_Pro_Human
}

# Category ordering for consistent output
CATEGORY_ORDER = ["Pro-apoptotic", "Anti-apoptotic", "Ambiguous", "Unspecified"]


def load_gene_list():
    """Load the consolidated apoptotic gene list."""
    print(f"Loading gene list from: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)
    print(f"  Loaded {len(df)} genes")
    print(f"  Columns: {list(df.columns)}")
    return df


def filter_by_source(df: pd.DataFrame, source_name: str, pattern: str) -> pd.DataFrame:
    """
    Filter genes that have the specified source in their sources column.

    Parameters
    ----------
    df : pd.DataFrame
        The full gene list
    source_name : str
        Human-readable source name (for logging)
    pattern : str
        The pattern to search for in the sources column

    Returns
    -------
    pd.DataFrame
        Filtered dataframe containing only genes from this source
    """
    mask = df['sources'].str.contains(pattern, na=False)
    filtered = df[mask].copy()
    print(f"  {source_name}: {len(filtered)} genes found")
    return filtered


def add_category_stats(df: pd.DataFrame, source_name: str) -> dict:
    """Calculate category statistics for a source."""
    stats = {}
    for cat in CATEGORY_ORDER:
        count = len(df[df['category'] == cat])
        stats[cat] = count
    stats['Total'] = len(df)
    return stats


def sort_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Sort dataframe by category in defined order, then by human symbol."""
    # Create a categorical type with our desired order
    df['category'] = pd.Categorical(
        df['category'],
        categories=CATEGORY_ORDER,
        ordered=True
    )
    # Sort by category, then by human symbol
    df_sorted = df.sort_values(['category', 'human_symbol']).reset_index(drop=True)
    return df_sorted


def save_source_breakdown(df: pd.DataFrame, source_name: str, output_dir: Path) -> Path:
    """
    Save the source-specific gene list to CSV.

    Parameters
    ----------
    df : pd.DataFrame
        Filtered gene list for this source
    source_name : str
        Name of the source (used in filename)
    output_dir : Path
        Directory to save the output

    Returns
    -------
    Path
        Path to the saved file
    """
    # Sort by category and gene symbol
    df_sorted = sort_by_category(df)

    # Create output filename
    filename = f"apoptosis_genes_{source_name}.csv"
    output_path = output_dir / filename

    # Save to CSV
    df_sorted.to_csv(output_path, index=False)
    print(f"  Saved: {output_path}")

    return output_path


def generate_summary_report(all_stats: dict, output_dir: Path) -> Path:
    """Generate a summary report of all breakdowns."""
    report_path = output_dir / "breakdown_summary.txt"

    with open(report_path, 'w') as f:
        f.write("=" * 60 + "\n")
        f.write("APOPTOTIC GENE LIST - SOURCE BREAKDOWN SUMMARY\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")

        for source, stats in all_stats.items():
            f.write(f"\n{source}\n")
            f.write("-" * 40 + "\n")
            for cat in CATEGORY_ORDER:
                if cat in stats:
                    f.write(f"  {cat:20s}: {stats[cat]:4d} genes\n")
            f.write(f"  {'TOTAL':20s}: {stats['Total']:4d} genes\n")

        f.write("\n" + "=" * 60 + "\n")
        f.write("Notes:\n")
        f.write("- Categories are consensus annotations derived from multiple sources\n")
        f.write("- A gene may appear in multiple source lists\n")
        f.write("- GO includes both GO_Pro_Human and GO_Anti_Human annotations\n")
        f.write("=" * 60 + "\n")

    print(f"\nSummary report saved: {report_path}")
    return report_path


def main():
    """Main execution function."""
    print("=" * 60)
    print("APOPTOTIC GENE LIST - SOURCE BREAKDOWN")
    print("=" * 60)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\nOutput directory: {OUTPUT_DIR}")

    # Load data
    print("\n[Step 1] Loading consolidated gene list...")
    df = load_gene_list()

    # Filter by each source
    print("\n[Step 2] Filtering genes by source...")
    all_stats = {}
    output_files = []

    for source_name, pattern in SOURCE_PATTERNS.items():
        print(f"\nProcessing {source_name}...")

        # Filter genes for this source
        df_source = filter_by_source(df, source_name, pattern)

        # Calculate statistics
        stats = add_category_stats(df_source, source_name)
        all_stats[source_name] = stats

        # Print category breakdown
        print(f"  Category breakdown:")
        for cat in CATEGORY_ORDER:
            print(f"    {cat}: {stats[cat]}")

        # Save to file
        output_path = save_source_breakdown(df_source, source_name, OUTPUT_DIR)
        output_files.append(output_path)

    # Generate summary report
    print("\n[Step 3] Generating summary report...")
    summary_path = generate_summary_report(all_stats, OUTPUT_DIR)
    output_files.append(summary_path)

    # Print final summary
    print("\n" + "=" * 60)
    print("BREAKDOWN COMPLETE")
    print("=" * 60)
    print(f"\nFiles generated:")
    for f in output_files:
        print(f"  - {f.name}")

    print("\nSummary:")
    print("-" * 40)
    for source, stats in all_stats.items():
        print(f"  {source:15s}: {stats['Total']:4d} genes")

    # Return stats for manifest update
    return all_stats, output_files


if __name__ == "__main__":
    stats, files = main()
