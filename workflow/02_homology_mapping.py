#!/usr/bin/env python3
"""
Step 2: Species & Homology Mapping

This script creates a comprehensive orthology mapping between Human and Mouse genes
found in the raw apoptosis gene sets from Step 1.

Uses MyGene.info API to convert Entrez Gene IDs to symbols and perform ortholog lookups.

Author: K-Dense Coding Agent
Date: 2026-01-27
"""

import os
import sys
import time
import pandas as pd
import mygene
from pathlib import Path
from typing import Set, Dict, Tuple, List

# Configuration
SESSION_DIR = Path("/app/sandbox/session_20260126_235914_ecc6fdd54e23")
RAW_DATA_DIR = SESSION_DIR / "workflow" / "raw_data"
OUTPUT_DIR = SESSION_DIR / "workflow" / "data"

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_gene_symbols(directory: Path) -> Tuple[Set[str], Set[str]]:
    """
    Load all CSV files from raw_data directory and extract unique gene symbols.

    Returns:
        Tuple of (human_genes, mouse_genes) as sets of gene symbols.
    """
    human_genes = set()
    mouse_genes = set()

    print(f"Loading gene symbols from {directory}...")
    csv_files = list(directory.glob("*.csv"))
    print(f"Found {len(csv_files)} CSV files")

    for csv_file in csv_files:
        print(f"  Reading: {csv_file.name}")
        df = pd.read_csv(csv_file)

        if "gene_symbol" not in df.columns:
            print(f"    Warning: 'gene_symbol' column not found in {csv_file.name}, skipping")
            continue

        # Check organism column to separate human vs mouse
        if "organism" in df.columns:
            human_subset = df[df["organism"].str.lower() == "human"]
            mouse_subset = df[df["organism"].str.lower() == "mouse"]

            human_genes.update(human_subset["gene_symbol"].dropna().astype(str).unique())
            mouse_genes.update(mouse_subset["gene_symbol"].dropna().astype(str).unique())

            print(f"    Found {len(human_subset['gene_symbol'].unique())} human, "
                  f"{len(mouse_subset['gene_symbol'].unique())} mouse genes")
        else:
            # Infer from filename
            filename_lower = csv_file.name.lower()
            symbols = df["gene_symbol"].dropna().astype(str).unique()

            if "human" in filename_lower:
                human_genes.update(symbols)
                print(f"    Added {len(symbols)} human genes (inferred from filename)")
            elif "mouse" in filename_lower:
                mouse_genes.update(symbols)
                print(f"    Added {len(symbols)} mouse genes (inferred from filename)")
            else:
                print(f"    Warning: Cannot determine organism for {csv_file.name}")

    return human_genes, mouse_genes


def entrez_ids_to_symbols(mg: mygene.MyGeneInfo, entrez_ids: List[int], species: str) -> Dict[int, str]:
    """
    Convert Entrez Gene IDs to gene symbols.

    Args:
        mg: MyGene.info client
        entrez_ids: List of Entrez Gene IDs
        species: Species ('human' or 'mouse')

    Returns:
        Dictionary mapping Entrez ID to gene symbol.
    """
    if not entrez_ids:
        return {}

    species_taxid = {"human": 9606, "mouse": 10090}[species]
    unique_ids = list(set(entrez_ids))

    print(f"  Converting {len(unique_ids)} Entrez IDs to symbols for {species}...")

    id_to_symbol = {}

    # Query in batches
    batch_size = 500
    for i in range(0, len(unique_ids), batch_size):
        batch = unique_ids[i:i+batch_size]

        try:
            results = mg.getgenes(batch, fields="symbol", species=species_taxid)

            for hit in results:
                if isinstance(hit, dict) and "symbol" in hit:
                    entrez_id = hit.get("query", hit.get("_id"))
                    if entrez_id:
                        try:
                            id_to_symbol[int(entrez_id)] = hit["symbol"]
                        except (ValueError, TypeError):
                            pass

            if (i // batch_size) % 5 == 0:
                print(f"    Progress: {min(i+batch_size, len(unique_ids))}/{len(unique_ids)}")

        except Exception as e:
            print(f"    Warning: Batch error: {e}")
            continue

    print(f"  Resolved {len(id_to_symbol)}/{len(unique_ids)} Entrez IDs to symbols")
    return id_to_symbol


def fetch_homologene_mappings(
    mg: mygene.MyGeneInfo,
    genes: List[str],
    source_species: str,
    target_species: str
) -> Tuple[Dict[str, List[int]], Set[int]]:
    """
    Fetch homologene data for genes and extract target species Entrez IDs.

    Returns:
        Tuple of (source_symbol -> target_entrez_ids dict, all target entrez IDs set)
    """
    species_taxid = {"human": 9606, "mouse": 10090}[source_species]
    target_taxid = {"human": 9606, "mouse": 10090}[target_species]

    print(f"\nFetching homologene data for {len(genes)} {source_species} genes...")

    # Query in batches for better reliability
    batch_size = 500
    orthologs = {}
    all_target_ids = set()

    for i in range(0, len(genes), batch_size):
        batch = genes[i:i+batch_size]

        try:
            results = mg.querymany(
                batch,
                scopes="symbol",
                fields="symbol,homologene",
                species=species_taxid,
                returnall=True
            )

            for hit in results.get("out", []):
                query = hit.get("query", "")
                if hit.get("notfound", False):
                    continue

                source_symbol = hit.get("symbol", query)
                homologene = hit.get("homologene", {})

                if isinstance(homologene, dict):
                    cluster_genes = homologene.get("genes", [])
                    target_ids = []

                    for g in cluster_genes:
                        if isinstance(g, list) and len(g) >= 2:
                            if g[0] == target_taxid:
                                target_ids.append(int(g[1]))
                                all_target_ids.add(int(g[1]))

                    if target_ids:
                        orthologs[source_symbol] = target_ids

            if (i // batch_size) % 3 == 0:
                print(f"  Progress: {min(i+batch_size, len(genes))}/{len(genes)} genes processed")

        except Exception as e:
            print(f"  Warning: Batch error: {e}")
            continue

    print(f"Found orthologs for {len(orthologs)}/{len(genes)} genes ({100*len(orthologs)/len(genes):.1f}%)")
    return orthologs, all_target_ids


def build_comprehensive_mapping(
    human_genes: Set[str],
    mouse_genes: Set[str]
) -> pd.DataFrame:
    """
    Build a comprehensive orthology mapping between Human and Mouse genes.
    Properly converts Entrez Gene IDs to symbols.
    """
    mg = mygene.MyGeneInfo()

    human_list = sorted(list(human_genes))
    mouse_list = sorted(list(mouse_genes))

    print(f"\n{'='*60}")
    print(f"Building orthology mapping:")
    print(f"  Human genes: {len(human_list)}")
    print(f"  Mouse genes: {len(mouse_list)}")
    print(f"{'='*60}")

    # Phase 1: Human -> Mouse orthologs
    print("\n--- Phase 1: Human -> Mouse lookup ---")
    human_to_mouse_ids, mouse_entrez_ids = fetch_homologene_mappings(
        mg, human_list, "human", "mouse"
    )

    # Phase 2: Mouse -> Human orthologs
    print("\n--- Phase 2: Mouse -> Human lookup ---")
    mouse_to_human_ids, human_entrez_ids = fetch_homologene_mappings(
        mg, mouse_list, "mouse", "human"
    )

    # Phase 3: Convert all Entrez IDs to symbols
    print("\n--- Phase 3: Converting Entrez IDs to Symbols ---")

    mouse_id_to_symbol = entrez_ids_to_symbols(mg, list(mouse_entrez_ids), "mouse")
    human_id_to_symbol = entrez_ids_to_symbols(mg, list(human_entrez_ids), "human")

    # Phase 4: Build final mapping records
    print("\n--- Phase 4: Building final mapping ---")

    mapping_records = []

    # Human -> Mouse mappings
    for human_sym, mouse_ids in human_to_mouse_ids.items():
        for mouse_id in mouse_ids:
            mouse_sym = mouse_id_to_symbol.get(mouse_id)
            if mouse_sym:
                mapping_records.append({
                    "human_symbol": human_sym.upper(),
                    "mouse_symbol": mouse_sym,
                    "human_entrez": None,  # We don't have it for this direction
                    "mouse_entrez": mouse_id,
                    "mapping_source": "human_to_mouse"
                })

    # Mouse -> Human mappings
    for mouse_sym, human_ids in mouse_to_human_ids.items():
        for human_id in human_ids:
            human_sym = human_id_to_symbol.get(human_id)
            if human_sym:
                mapping_records.append({
                    "human_symbol": human_sym.upper(),
                    "mouse_symbol": mouse_sym,
                    "human_entrez": human_id,
                    "mouse_entrez": None,
                    "mapping_source": "mouse_to_human"
                })

    df = pd.DataFrame(mapping_records)

    if len(df) == 0:
        print("WARNING: No ortholog mappings found!")
        return df

    # Remove duplicates, keeping the most complete record
    initial_count = len(df)
    df = df.drop_duplicates(subset=["human_symbol", "mouse_symbol"], keep="first")
    print(f"  Removed {initial_count - len(df)} duplicate pairs")

    # Sort by human symbol
    df = df.sort_values(["human_symbol", "mouse_symbol"]).reset_index(drop=True)

    # Create final output with just symbol columns (keeping Entrez for reference)
    return df


def print_mapping_summary(df: pd.DataFrame, human_genes: Set[str], mouse_genes: Set[str]):
    """Print a summary of the orthology mapping results."""
    print(f"\n{'='*60}")
    print("ORTHOLOGY MAPPING SUMMARY")
    print(f"{'='*60}")

    # Total pairs
    print(f"\nTotal ortholog pairs: {len(df)}")

    # Unique genes mapped
    unique_human = set(df["human_symbol"].str.upper().unique())
    unique_mouse = set(df["mouse_symbol"].unique())

    # Calculate coverage vs input
    human_input_upper = {g.upper() for g in human_genes}
    mouse_input_caps = {g.capitalize() for g in mouse_genes}

    human_covered = unique_human.intersection(human_input_upper)
    mouse_covered = len([m for m in unique_mouse if m.capitalize() in mouse_input_caps or m.upper() in {g.upper() for g in mouse_genes}])

    print(f"\nCoverage Statistics:")
    print(f"  Human genes in input: {len(human_genes)}")
    print(f"  Unique human genes with mouse orthologs: {len(unique_human)}")
    print(f"  Human genes from input that have mappings: {len(human_covered)} ({100*len(human_covered)/len(human_genes):.1f}%)")

    print(f"\n  Mouse genes in input: {len(mouse_genes)}")
    print(f"  Unique mouse genes with human orthologs: {len(unique_mouse)}")

    # Mapping types
    print(f"\nMapping Sources:")
    for source in df["mapping_source"].unique():
        count = len(df[df["mapping_source"] == source])
        print(f"  {source}: {count} pairs")

    # One-to-many statistics
    h2m_counts = df.groupby("human_symbol")["mouse_symbol"].count()
    m2h_counts = df.groupby("mouse_symbol")["human_symbol"].count()

    print(f"\nMapping Cardinality:")
    print(f"  Human genes with multiple mouse orthologs: {sum(h2m_counts > 1)}")
    print(f"  Mouse genes with multiple human orthologs: {sum(m2h_counts > 1)}")
    print(f"  Max mouse orthologs for one human gene: {h2m_counts.max()}")
    print(f"  Max human orthologs for one mouse gene: {m2h_counts.max()}")

    print(f"\n{'='*60}")


def main():
    """Main execution function."""
    print("=" * 60)
    print("STEP 2: Species & Homology Mapping")
    print("=" * 60)
    print(f"Session directory: {SESSION_DIR}")
    print(f"Raw data directory: {RAW_DATA_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")

    # Step 1: Load gene symbols
    human_genes, mouse_genes = load_gene_symbols(RAW_DATA_DIR)
    print(f"\nUnique genes loaded:")
    print(f"  Human: {len(human_genes)} genes")
    print(f"  Mouse: {len(mouse_genes)} genes")

    if not human_genes and not mouse_genes:
        print("ERROR: No genes found in raw data files!")
        sys.exit(1)

    # Step 2: Build orthology mapping
    mapping_df = build_comprehensive_mapping(human_genes, mouse_genes)

    if len(mapping_df) == 0:
        print("ERROR: No orthology mappings were found!")
        sys.exit(1)

    # Step 3: Save output - both full and simplified versions
    full_output = OUTPUT_DIR / "orthology_mapping_full.csv"
    mapping_df.to_csv(full_output, index=False)
    print(f"\nFull orthology mapping saved to: {full_output}")

    # Save simplified version with just symbol columns
    simple_df = mapping_df[["human_symbol", "mouse_symbol"]].drop_duplicates()
    simple_output = OUTPUT_DIR / "orthology_mapping.csv"
    simple_df.to_csv(simple_output, index=False)
    print(f"Simplified mapping saved to: {simple_output}")
    print(f"Total unique pairs: {len(simple_df)}")

    # Step 4: Print summary
    print_mapping_summary(mapping_df, human_genes, mouse_genes)

    # Step 5: Display sample of the output
    print("\nSample of orthology mapping (first 15 rows):")
    print(simple_df.head(15).to_string(index=False))

    print("\n✓ Step 2 completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
