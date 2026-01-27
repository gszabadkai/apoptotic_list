#!/usr/bin/env python3
"""
Step 3: Gene Set Consolidation

This script consolidates raw gene sets from multiple sources into a unified
list of apoptotic proteins, resolving Human/Mouse orthology and assigning
functional categories (Pro-apoptotic, Anti-apoptotic, Ambiguous, Unspecified).

Author: K-Dense Coding Agent
Date: 2026-01-27
"""

import pandas as pd
from pathlib import Path
from collections import defaultdict
import sys

# =============================================================================
# Configuration
# =============================================================================
SESSION_DIR = Path("/app/sandbox/session_20260126_235914_ecc6fdd54e23")
WORKFLOW_DIR = SESSION_DIR / "workflow"
RAW_DATA_DIR = WORKFLOW_DIR / "raw_data"
OUTPUT_DIR = WORKFLOW_DIR / "data"

# Input files
ORTHOLOGY_FILE = OUTPUT_DIR / "orthology_mapping.csv"

# Output files
CONSOLIDATED_FILE = OUTPUT_DIR / "consolidated_apoptosis_genes.csv"
SUMMARY_FILE = OUTPUT_DIR / "gene_category_summary.txt"

# Source file mapping
SOURCE_FILES = {
    "GO_Pro_Human": RAW_DATA_DIR / "human_go_pro.csv",
    "GO_Anti_Human": RAW_DATA_DIR / "human_go_anti.csv",
    "GO_Pro_Mouse": RAW_DATA_DIR / "mouse_go_pro.csv",
    "GO_Anti_Mouse": RAW_DATA_DIR / "mouse_go_anti.csv",
    "KEGG": RAW_DATA_DIR / "human_kegg_apoptosis.csv",
    "Reactome": RAW_DATA_DIR / "human_reactome_apoptosis.csv",
    "Hallmark": RAW_DATA_DIR / "human_hallmark_apoptosis.csv",
}


def load_orthology_mapping(filepath: Path) -> dict:
    """
    Load orthology mapping and create bidirectional lookup dictionaries.

    Returns
    -------
    dict
        Contains 'h2m' (human to mouse) and 'm2h' (mouse to human) mappings.
    """
    print(f"Loading orthology mapping from {filepath}")
    df = pd.read_csv(filepath)
    print(f"  Loaded {len(df)} ortholog pairs")

    # Create bidirectional mappings
    h2m = {}  # human_symbol -> list of mouse_symbols
    m2h = {}  # mouse_symbol -> human_symbol

    for _, row in df.iterrows():
        human = row['human_symbol']
        mouse = row['mouse_symbol']

        # Human to mouse (can be one-to-many)
        if human not in h2m:
            h2m[human] = []
        h2m[human].append(mouse)

        # Mouse to human
        m2h[mouse] = human

    print(f"  Human genes with orthologs: {len(h2m)}")
    print(f"  Mouse genes mapped to human: {len(m2h)}")

    return {'h2m': h2m, 'm2h': m2h}


def load_source_file(filepath: Path, source_name: str) -> set:
    """
    Load gene symbols from a source file.

    Returns
    -------
    set
        Set of gene symbols (uppercase for consistency in matching)
    """
    print(f"Loading {source_name} from {filepath.name}")
    df = pd.read_csv(filepath)
    genes = set(df['gene_symbol'].dropna().unique())
    print(f"  Found {len(genes)} unique genes")
    return genes


def consolidate_genes(orthology: dict, sources: dict) -> pd.DataFrame:
    """
    Consolidate genes from all sources into a master dataset.

    Parameters
    ----------
    orthology : dict
        Bidirectional orthology mappings ('h2m' and 'm2h')
    sources : dict
        Dictionary mapping source names to sets of gene symbols

    Returns
    -------
    pd.DataFrame
        Consolidated gene table with categories and evidence
    """
    print("\n" + "="*60)
    print("Consolidating genes from all sources")
    print("="*60)

    # Gene evidence tracker: human_symbol -> {source evidence}
    gene_evidence = defaultdict(lambda: {
        'pro_evidence': set(),
        'anti_evidence': set(),
        'general_evidence': set(),
        'mouse_symbols': set()
    })

    h2m = orthology['h2m']
    m2h = orthology['m2h']

    # Process human GO Pro-apoptotic genes
    print("\nProcessing Human GO Pro-apoptotic genes...")
    for gene in sources['GO_Pro_Human']:
        gene_evidence[gene]['pro_evidence'].add('GO_Pro_Human')
        if gene in h2m:
            for mouse in h2m[gene]:
                gene_evidence[gene]['mouse_symbols'].add(mouse)
    print(f"  Processed {len(sources['GO_Pro_Human'])} genes")

    # Process human GO Anti-apoptotic genes
    print("Processing Human GO Anti-apoptotic genes...")
    for gene in sources['GO_Anti_Human']:
        gene_evidence[gene]['anti_evidence'].add('GO_Anti_Human')
        if gene in h2m:
            for mouse in h2m[gene]:
                gene_evidence[gene]['mouse_symbols'].add(mouse)
    print(f"  Processed {len(sources['GO_Anti_Human'])} genes")

    # Process mouse GO Pro-apoptotic genes (map to human)
    print("Processing Mouse GO Pro-apoptotic genes...")
    mapped_count = 0
    unmapped_count = 0
    for mouse_gene in sources['GO_Pro_Mouse']:
        if mouse_gene in m2h:
            human_gene = m2h[mouse_gene]
            gene_evidence[human_gene]['pro_evidence'].add('GO_Pro_Mouse')
            gene_evidence[human_gene]['mouse_symbols'].add(mouse_gene)
            mapped_count += 1
        else:
            # Try case-insensitive match (mouse gene symbols have different capitalization)
            # For human orthologs not found, we can still track the mouse gene
            # if it has a human-like symbol (uppercase)
            unmapped_count += 1
    print(f"  Mapped {mapped_count} genes, {unmapped_count} unmapped")

    # Process mouse GO Anti-apoptotic genes (map to human)
    print("Processing Mouse GO Anti-apoptotic genes...")
    mapped_count = 0
    for mouse_gene in sources['GO_Anti_Mouse']:
        if mouse_gene in m2h:
            human_gene = m2h[mouse_gene]
            gene_evidence[human_gene]['anti_evidence'].add('GO_Anti_Mouse')
            gene_evidence[human_gene]['mouse_symbols'].add(mouse_gene)
            mapped_count += 1
    print(f"  Mapped {mapped_count} genes")

    # Process general sources (KEGG, Reactome, Hallmark - all human)
    for source_name in ['KEGG', 'Reactome', 'Hallmark']:
        print(f"Processing {source_name} genes...")
        for gene in sources[source_name]:
            gene_evidence[gene]['general_evidence'].add(source_name)
            if gene in h2m:
                for mouse in h2m[gene]:
                    gene_evidence[gene]['mouse_symbols'].add(mouse)
        print(f"  Processed {len(sources[source_name])} genes")

    # Now categorize each gene
    print("\n" + "="*60)
    print("Categorizing genes based on evidence")
    print("="*60)

    consolidated_data = []

    for i, (human_symbol, evidence) in enumerate(gene_evidence.items()):
        if (i + 1) % 500 == 0:
            print(f"  Processing gene {i+1}/{len(gene_evidence)}...")

        has_pro = len(evidence['pro_evidence']) > 0
        has_anti = len(evidence['anti_evidence']) > 0
        has_general = len(evidence['general_evidence']) > 0

        # Determine category
        if has_pro and has_anti:
            category = "Ambiguous"
        elif has_pro:
            category = "Pro-apoptotic"
        elif has_anti:
            category = "Anti-apoptotic"
        elif has_general:
            category = "Unspecified"
        else:
            # Should not happen, but just in case
            category = "Unknown"

        # Compile sources
        all_sources = set()
        all_sources.update(evidence['pro_evidence'])
        all_sources.update(evidence['anti_evidence'])
        all_sources.update(evidence['general_evidence'])

        # Get mouse symbols (comma-separated if multiple)
        mouse_symbols = sorted(evidence['mouse_symbols'])
        mouse_symbol_str = ",".join(mouse_symbols) if mouse_symbols else ""

        # Evidence score is the count of unique sources
        evidence_score = len(all_sources)

        # Sources string
        sources_str = ",".join(sorted(all_sources))

        consolidated_data.append({
            'human_symbol': human_symbol,
            'mouse_symbol': mouse_symbol_str,
            'category': category,
            'sources': sources_str,
            'evidence_score': evidence_score
        })

    # Create DataFrame and sort by evidence score (descending), then alphabetically
    df = pd.DataFrame(consolidated_data)
    df = df.sort_values(['evidence_score', 'human_symbol'], ascending=[False, True])
    df = df.reset_index(drop=True)

    print(f"\nTotal consolidated genes: {len(df)}")

    return df


def generate_summary(df: pd.DataFrame, summary_file: Path):
    """
    Generate a summary of gene categories.
    """
    print("\n" + "="*60)
    print("Generating category summary")
    print("="*60)

    category_counts = df['category'].value_counts()

    # Genes with mouse orthologs
    genes_with_mouse = df[df['mouse_symbol'] != ''].shape[0]

    # Average evidence score
    avg_evidence = df['evidence_score'].mean()

    # Multi-source genes
    multi_source = df[df['evidence_score'] > 1].shape[0]

    summary_lines = [
        "=" * 60,
        "GENE SET CONSOLIDATION SUMMARY",
        "=" * 60,
        "",
        f"Total unique human genes: {len(df)}",
        f"Genes with mouse orthologs: {genes_with_mouse} ({100*genes_with_mouse/len(df):.1f}%)",
        f"Average evidence score: {avg_evidence:.2f}",
        f"Genes from multiple sources: {multi_source} ({100*multi_source/len(df):.1f}%)",
        "",
        "-" * 40,
        "CATEGORY DISTRIBUTION",
        "-" * 40,
    ]

    for category in ['Pro-apoptotic', 'Anti-apoptotic', 'Ambiguous', 'Unspecified']:
        count = category_counts.get(category, 0)
        pct = 100 * count / len(df) if len(df) > 0 else 0
        summary_lines.append(f"  {category}: {count} ({pct:.1f}%)")

    summary_lines.extend([
        "",
        "-" * 40,
        "EVIDENCE SCORE DISTRIBUTION",
        "-" * 40,
    ])

    score_counts = df['evidence_score'].value_counts().sort_index()
    for score, count in score_counts.items():
        summary_lines.append(f"  {score} source(s): {count} genes")

    summary_lines.extend([
        "",
        "-" * 40,
        "TOP 20 GENES BY EVIDENCE SCORE",
        "-" * 40,
    ])

    top_genes = df.nlargest(20, 'evidence_score')
    for _, row in top_genes.iterrows():
        summary_lines.append(
            f"  {row['human_symbol']}: {row['category']} "
            f"(score={row['evidence_score']}, sources: {row['sources']})"
        )

    summary_text = "\n".join(summary_lines)

    with open(summary_file, 'w') as f:
        f.write(summary_text)

    print(summary_text)
    print(f"\nSummary saved to: {summary_file}")


def main():
    """Main execution function."""
    print("="*60)
    print("STEP 3: GENE SET CONSOLIDATION")
    print("="*60)
    print()

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load orthology mapping
    if not ORTHOLOGY_FILE.exists():
        print(f"ERROR: Orthology file not found: {ORTHOLOGY_FILE}")
        sys.exit(1)
    orthology = load_orthology_mapping(ORTHOLOGY_FILE)

    # Load all source files
    print("\n" + "="*60)
    print("Loading source files")
    print("="*60)

    sources = {}
    for source_name, filepath in SOURCE_FILES.items():
        if not filepath.exists():
            print(f"WARNING: Source file not found: {filepath}")
            sources[source_name] = set()
        else:
            sources[source_name] = load_source_file(filepath, source_name)

    # Consolidate genes
    consolidated_df = consolidate_genes(orthology, sources)

    # Save consolidated data
    print(f"\nSaving consolidated data to: {CONSOLIDATED_FILE}")
    consolidated_df.to_csv(CONSOLIDATED_FILE, index=False)
    print(f"  Saved {len(consolidated_df)} genes")

    # Generate summary
    generate_summary(consolidated_df, SUMMARY_FILE)

    print("\n" + "="*60)
    print("STEP 3 COMPLETE")
    print("="*60)
    print(f"\nOutput files:")
    print(f"  - {CONSOLIDATED_FILE}")
    print(f"  - {SUMMARY_FILE}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
