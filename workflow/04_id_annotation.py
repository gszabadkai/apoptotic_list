#!/usr/bin/env python3
"""
Step 4: ID Annotation & Finalization

Annotates the consolidated gene list with Ensembl IDs and generates final deliverables.

Objectives:
- Fetch Ensembl IDs for Human and Mouse gene symbols using mygene
- Create the final annotated gene list
- Generate category distribution visualization
"""

import pandas as pd
import numpy as np
import mygene
import matplotlib.pyplot as plt
from pathlib import Path
import time
import warnings

warnings.filterwarnings('ignore')

# Set paths
SESSION_DIR = Path('/app/sandbox/session_20260126_235914_ecc6fdd54e23')
WORKFLOW_DATA = SESSION_DIR / 'workflow' / 'data'
RESULTS_DIR = SESSION_DIR / 'results'
FIGURES_DIR = SESSION_DIR / 'figures'

# Ensure output directories exist
RESULTS_DIR.mkdir(exist_ok=True)
FIGURES_DIR.mkdir(exist_ok=True)


def fetch_ensembl_ids_batched(gene_symbols, species='human', batch_size=200):
    """
    Fetch Ensembl IDs for a list of gene symbols using mygene.

    Parameters
    ----------
    gene_symbols : list
        List of gene symbols to query
    species : str
        Species: 'human' or 'mouse'
    batch_size : int
        Number of genes to query per batch

    Returns
    -------
    dict
        Mapping of gene symbol to Ensembl ID
    """
    mg = mygene.MyGeneInfo()

    # Filter out empty/null symbols
    valid_symbols = [s for s in gene_symbols if pd.notna(s) and s.strip() != '']

    if not valid_symbols:
        return {}

    species_name = 'human' if species == 'human' else 'mouse'
    print(f"\nFetching Ensembl IDs for {len(valid_symbols)} {species_name} genes...")

    symbol_to_ensembl = {}
    total_batches = (len(valid_symbols) + batch_size - 1) // batch_size

    for i in range(0, len(valid_symbols), batch_size):
        batch = valid_symbols[i:i+batch_size]
        batch_num = (i // batch_size) + 1

        print(f"  Processing batch {batch_num}/{total_batches} ({len(batch)} genes)...")

        try:
            results = mg.querymany(
                batch,
                scopes='symbol',
                fields='ensembl.gene',
                species=species_name,
                returnall=True
            )

            for hit in results.get('out', []):
                query = hit.get('query', '')
                ensembl_data = hit.get('ensembl', None)

                if ensembl_data:
                    # ensembl can be a dict or list of dicts
                    if isinstance(ensembl_data, list):
                        # Take the first one
                        gene_id = ensembl_data[0].get('gene', None)
                    else:
                        gene_id = ensembl_data.get('gene', None)

                    if gene_id:
                        symbol_to_ensembl[query] = gene_id

            # Brief pause between batches
            if i + batch_size < len(valid_symbols):
                time.sleep(0.5)

        except Exception as e:
            print(f"  Warning: Error in batch {batch_num}: {e}")
            continue

    mapped_count = len(symbol_to_ensembl)
    coverage = (mapped_count / len(valid_symbols)) * 100 if valid_symbols else 0
    print(f"  Mapped {mapped_count}/{len(valid_symbols)} genes ({coverage:.1f}% coverage)")

    return symbol_to_ensembl


def create_category_visualization(df, output_path):
    """
    Create a bar chart showing distribution of apoptosis categories.

    Parameters
    ----------
    df : pd.DataFrame
        Gene dataframe with 'category' column
    output_path : Path
        Path to save the figure
    """
    print("\nGenerating category distribution visualization...")

    # Count categories
    category_counts = df['category'].value_counts()

    # Define colors for each category
    color_map = {
        'Pro-apoptotic': '#E74C3C',      # Red
        'Anti-apoptotic': '#27AE60',     # Green
        'Ambiguous': '#F39C12',          # Orange
        'Unspecified': '#95A5A6'         # Gray
    }

    # Ensure consistent order
    categories = ['Pro-apoptotic', 'Anti-apoptotic', 'Ambiguous', 'Unspecified']
    counts = [category_counts.get(cat, 0) for cat in categories]
    colors = [color_map[cat] for cat in categories]

    # Create figure
    plt.figure(figsize=(10, 6))
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.size'] = 11

    bars = plt.bar(categories, counts, color=colors, edgecolor='black', linewidth=0.5)

    # Add value labels on bars
    for bar, count in zip(bars, counts):
        if count > 0:
            plt.text(
                bar.get_x() + bar.get_width()/2,
                bar.get_height() + 5,
                str(count),
                ha='center',
                va='bottom',
                fontsize=12,
                fontweight='bold'
            )

    plt.xlabel('Apoptosis Category', fontsize=13)
    plt.ylabel('Number of Genes', fontsize=13)
    plt.title('Distribution of Apoptotic Genes by Functional Category', fontsize=14, fontweight='bold')

    # Add total annotation
    total = sum(counts)
    plt.text(
        0.98, 0.95,
        f'Total: {total} genes',
        transform=plt.gca().transAxes,
        ha='right',
        va='top',
        fontsize=11,
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"  Saved: {output_path}")


def main():
    print("=" * 60)
    print("Step 4: ID Annotation & Finalization")
    print("=" * 60)

    # Load consolidated gene list
    input_path = WORKFLOW_DATA / 'consolidated_apoptosis_genes.csv'
    print(f"\nLoading consolidated gene list from: {input_path}")
    df = pd.read_csv(input_path)
    print(f"  Loaded {len(df)} genes")
    print(f"  Columns: {list(df.columns)}")

    # Check category distribution
    print("\nCategory distribution:")
    for cat, count in df['category'].value_counts().items():
        print(f"  {cat}: {count}")

    # Fetch Human Ensembl IDs
    human_symbols = df['human_symbol'].tolist()
    human_ensembl_map = fetch_ensembl_ids_batched(human_symbols, species='human')

    # Fetch Mouse Ensembl IDs
    mouse_symbols = df['mouse_symbol'].tolist()
    mouse_ensembl_map = fetch_ensembl_ids_batched(mouse_symbols, species='mouse')

    # Add Ensembl IDs to dataframe
    print("\nMerging Ensembl IDs into dataset...")
    df['human_ensembl_id'] = df['human_symbol'].map(human_ensembl_map)
    df['mouse_ensembl_id'] = df['mouse_symbol'].map(mouse_ensembl_map)

    # Calculate coverage statistics
    human_with_id = df['human_ensembl_id'].notna().sum()
    mouse_valid = df['mouse_symbol'].notna() & (df['mouse_symbol'] != '')
    mouse_with_id = df.loc[mouse_valid, 'mouse_ensembl_id'].notna().sum()
    total_mouse_valid = mouse_valid.sum()

    print("\n" + "=" * 60)
    print("ID Mapping Coverage Summary")
    print("=" * 60)
    print(f"Human Ensembl ID coverage: {human_with_id}/{len(df)} ({100*human_with_id/len(df):.1f}%)")
    print(f"Mouse Ensembl ID coverage: {mouse_with_id}/{total_mouse_valid} ({100*mouse_with_id/total_mouse_valid:.1f}%)")

    # Reorder columns for final output
    final_columns = [
        'human_symbol',
        'human_ensembl_id',
        'mouse_symbol',
        'mouse_ensembl_id',
        'category',
        'sources',
        'evidence_score'
    ]
    df_final = df[final_columns]

    # Save final annotated gene list
    output_path = RESULTS_DIR / 'final_apoptotic_gene_list.csv'
    df_final.to_csv(output_path, index=False)
    print(f"\nSaved final gene list: {output_path}")

    # Generate visualization
    fig_path = FIGURES_DIR / 'category_distribution.png'
    create_category_visualization(df_final, fig_path)

    # Print final summary
    print("\n" + "=" * 60)
    print("STEP 4 COMPLETE - Final Summary")
    print("=" * 60)
    print(f"Total genes in final list: {len(df_final)}")
    print(f"Human Ensembl ID mapping: {human_with_id}/{len(df)} ({100*human_with_id/len(df):.1f}%)")
    print(f"Mouse Ensembl ID mapping: {mouse_with_id}/{total_mouse_valid} ({100*mouse_with_id/total_mouse_valid:.1f}%)")
    print("\nOutputs generated:")
    print(f"  1. {output_path}")
    print(f"  2. {fig_path}")

    # Preview final data
    print("\nFinal dataset preview (first 10 rows):")
    print(df_final.head(10).to_string(index=False))

    return df_final


if __name__ == '__main__':
    df_result = main()
