#!/usr/bin/env python3
"""
01_data_acquisition.py
======================
Retrieve apoptotic gene sets from MSigDB (GO, KEGG, Reactome, Hallmark)
for Human and Mouse organisms.

This script queries MSigDB collections via gseapy to fetch:
- GO Biological Process: Pro-apoptotic and Anti-apoptotic gene sets
- KEGG: KEGG_APOPTOSIS pathway
- Reactome: REACTOME_APOPTOSIS pathway
- Hallmark: HALLMARK_APOPTOSIS

Author: K-Dense Coding Agent
Date: 2026-01-27
"""

import os
import sys
import time
import pandas as pd
import gseapy as gp
from pathlib import Path

# Configuration
SESSION_DIR = "/app/sandbox/session_20260126_235914_ecc6fdd54e23"
OUTPUT_DIR = Path(SESSION_DIR) / "workflow" / "raw_data"


def log_progress(msg):
    """Print timestamped progress message."""
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def get_msigdb_gene_set(library_name, gene_set_name, organism="Human"):
    """
    Retrieve a specific gene set from MSigDB.

    Parameters
    ----------
    library_name : str
        MSigDB library name (e.g., 'GO_Biological_Process_2023')
    gene_set_name : str
        Name or partial name of the gene set to search
    organism : str
        Organism ('Human' or 'Mouse')

    Returns
    -------
    dict or None
        Dictionary mapping gene set names to gene lists
    """
    try:
        log_progress(f"  Fetching library: {library_name} for {organism}...")
        # Get the full library
        lib = gp.get_library(name=library_name, organism=organism)

        # Search for matching gene sets
        matching = {}
        search_term = gene_set_name.upper()

        for gs_name, genes in lib.items():
            if search_term in gs_name.upper():
                matching[gs_name] = genes

        if matching:
            log_progress(f"    Found {len(matching)} matching gene set(s)")
        else:
            log_progress(f"    No exact match for '{gene_set_name}', returning full library for search")
            # Return some related gene sets for manual inspection
            related = {k: v for k, v in lib.items() if 'APOPTOSIS' in k.upper() or 'APOPTOTIC' in k.upper()}
            return related

        return matching

    except Exception as e:
        log_progress(f"    Error retrieving {library_name}: {e}")
        return None


def get_available_libraries(organism="Human"):
    """Get list of available MSigDB libraries."""
    try:
        libraries = gp.get_library_name(organism=organism)
        return libraries
    except Exception as e:
        log_progress(f"Error getting library list: {e}")
        return []


def save_gene_set_to_csv(gene_sets, output_path, source, category):
    """
    Save gene set(s) to CSV file.

    Parameters
    ----------
    gene_sets : dict
        Dictionary mapping gene set names to gene lists
    output_path : Path
        Output file path
    source : str
        Source database (GO, KEGG, Reactome, Hallmark)
    category : str
        Category (Pro, Anti, General)
    """
    if not gene_sets:
        log_progress(f"  No gene sets to save for {source} {category}")
        return False

    # Convert to DataFrame
    rows = []
    for gs_name, genes in gene_sets.items():
        for gene in genes:
            rows.append({
                "gene_symbol": gene,
                "gene_set_name": gs_name,
                "source": source,
                "category": category,
                "organism": "Human"
            })

    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    log_progress(f"  Saved {len(df)} gene entries to {output_path.name}")
    return True


def main():
    """Main function to orchestrate data acquisition."""
    log_progress("=" * 60)
    log_progress("DATA ACQUISITION: Apoptotic Gene Sets from MSigDB")
    log_progress("=" * 60)

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    log_progress(f"Output directory: {OUTPUT_DIR}")

    # Get available libraries
    log_progress("\nStep 1: Checking available MSigDB libraries...")
    libraries = get_available_libraries("Human")
    log_progress(f"Found {len(libraries)} libraries for Human")

    # Print relevant libraries
    relevant_libs = [l for l in libraries if any(x in l.upper() for x in ['GO', 'KEGG', 'REACTOME', 'HALLMARK', 'C2', 'C5', 'H_'])]
    log_progress(f"Relevant libraries: {len(relevant_libs)}")
    for lib in relevant_libs[:20]:
        print(f"    - {lib}")

    results_summary = {}

    # =====================================================
    # GO Biological Process - Pro-apoptotic
    # =====================================================
    log_progress("\nStep 2: Retrieving GO Pro-apoptotic gene sets...")

    # Try multiple GO library naming conventions
    go_libraries = [l for l in libraries if 'GO' in l.upper() and 'BIOLOGICAL' in l.upper()]
    log_progress(f"  Found GO Biological Process libraries: {go_libraries[:5]}")

    go_pro_genes = {}
    go_anti_genes = {}

    for go_lib in go_libraries[:3]:  # Try first 3 matches
        try:
            log_progress(f"  Trying library: {go_lib}")
            lib_data = gp.get_library(name=go_lib, organism="Human")

            # Search for pro-apoptotic terms
            for gs_name, genes in lib_data.items():
                gs_upper = gs_name.upper()
                if 'POSITIVE' in gs_upper and ('APOPTOTIC' in gs_upper or 'APOPTOSIS' in gs_upper):
                    go_pro_genes[gs_name] = genes
                    log_progress(f"    Found PRO: {gs_name} ({len(genes)} genes)")
                elif 'NEGATIVE' in gs_upper and ('APOPTOTIC' in gs_upper or 'APOPTOSIS' in gs_upper):
                    go_anti_genes[gs_name] = genes
                    log_progress(f"    Found ANTI: {gs_name} ({len(genes)} genes)")

            if go_pro_genes or go_anti_genes:
                break  # Found what we need

        except Exception as e:
            log_progress(f"    Error with {go_lib}: {e}")

    # Save GO Pro-apoptotic
    if go_pro_genes:
        save_gene_set_to_csv(
            go_pro_genes,
            OUTPUT_DIR / "human_go_pro.csv",
            "GO_BP",
            "Pro"
        )
        results_summary["GO_Pro"] = sum(len(g) for g in go_pro_genes.values())

    # Save GO Anti-apoptotic
    if go_anti_genes:
        save_gene_set_to_csv(
            go_anti_genes,
            OUTPUT_DIR / "human_go_anti.csv",
            "GO_BP",
            "Anti"
        )
        results_summary["GO_Anti"] = sum(len(g) for g in go_anti_genes.values())

    # =====================================================
    # KEGG Apoptosis
    # =====================================================
    log_progress("\nStep 3: Retrieving KEGG_APOPTOSIS gene set...")

    kegg_libraries = [l for l in libraries if 'KEGG' in l.upper()]
    log_progress(f"  Found KEGG libraries: {kegg_libraries[:5]}")

    kegg_apoptosis = {}
    for kegg_lib in kegg_libraries[:3]:
        try:
            log_progress(f"  Trying library: {kegg_lib}")
            lib_data = gp.get_library(name=kegg_lib, organism="Human")

            for gs_name, genes in lib_data.items():
                if 'APOPTOSIS' in gs_name.upper():
                    kegg_apoptosis[gs_name] = genes
                    log_progress(f"    Found: {gs_name} ({len(genes)} genes)")

            if kegg_apoptosis:
                break

        except Exception as e:
            log_progress(f"    Error with {kegg_lib}: {e}")

    if kegg_apoptosis:
        save_gene_set_to_csv(
            kegg_apoptosis,
            OUTPUT_DIR / "human_kegg_apoptosis.csv",
            "KEGG",
            "General"
        )
        results_summary["KEGG"] = sum(len(g) for g in kegg_apoptosis.values())

    # =====================================================
    # Reactome Apoptosis
    # =====================================================
    log_progress("\nStep 4: Retrieving Reactome Apoptosis gene sets...")

    reactome_libraries = [l for l in libraries if 'REACTOME' in l.upper()]
    log_progress(f"  Found Reactome libraries: {reactome_libraries[:5]}")

    reactome_apoptosis = {}
    for reactome_lib in reactome_libraries[:3]:
        try:
            log_progress(f"  Trying library: {reactome_lib}")
            lib_data = gp.get_library(name=reactome_lib, organism="Human")

            for gs_name, genes in lib_data.items():
                if 'APOPTOSIS' in gs_name.upper() or 'APOPTOTIC' in gs_name.upper():
                    reactome_apoptosis[gs_name] = genes
                    log_progress(f"    Found: {gs_name} ({len(genes)} genes)")

            if reactome_apoptosis:
                break

        except Exception as e:
            log_progress(f"    Error with {reactome_lib}: {e}")

    if reactome_apoptosis:
        save_gene_set_to_csv(
            reactome_apoptosis,
            OUTPUT_DIR / "human_reactome_apoptosis.csv",
            "Reactome",
            "General"
        )
        results_summary["Reactome"] = sum(len(g) for g in reactome_apoptosis.values())

    # =====================================================
    # Hallmark Apoptosis
    # =====================================================
    log_progress("\nStep 5: Retrieving HALLMARK_APOPTOSIS gene set...")

    hallmark_libraries = [l for l in libraries if 'HALLMARK' in l.upper() or l.startswith('H_') or l == 'MSigDB_Hallmark_2020']
    log_progress(f"  Found Hallmark libraries: {hallmark_libraries}")

    hallmark_apoptosis = {}
    for hallmark_lib in hallmark_libraries[:5]:
        try:
            log_progress(f"  Trying library: {hallmark_lib}")
            lib_data = gp.get_library(name=hallmark_lib, organism="Human")

            for gs_name, genes in lib_data.items():
                if 'APOPTOSIS' in gs_name.upper():
                    hallmark_apoptosis[gs_name] = genes
                    log_progress(f"    Found: {gs_name} ({len(genes)} genes)")

            if hallmark_apoptosis:
                break

        except Exception as e:
            log_progress(f"    Error with {hallmark_lib}: {e}")

    if hallmark_apoptosis:
        save_gene_set_to_csv(
            hallmark_apoptosis,
            OUTPUT_DIR / "human_hallmark_apoptosis.csv",
            "Hallmark",
            "General"
        )
        results_summary["Hallmark"] = sum(len(g) for g in hallmark_apoptosis.values())

    # =====================================================
    # Mouse Gene Sets (attempt)
    # =====================================================
    log_progress("\nStep 6: Attempting to retrieve Mouse gene sets...")

    try:
        mouse_libraries = get_available_libraries("Mouse")
        log_progress(f"Found {len(mouse_libraries)} libraries for Mouse")

        mouse_go_libs = [l for l in mouse_libraries if 'GO' in l.upper() and 'BIOLOGICAL' in l.upper()]

        if mouse_go_libs:
            log_progress(f"  Found Mouse GO libraries: {mouse_go_libs[:3]}")

            mouse_go_pro = {}
            mouse_go_anti = {}

            for go_lib in mouse_go_libs[:2]:
                try:
                    lib_data = gp.get_library(name=go_lib, organism="Mouse")

                    for gs_name, genes in lib_data.items():
                        gs_upper = gs_name.upper()
                        if 'POSITIVE' in gs_upper and ('APOPTOTIC' in gs_upper or 'APOPTOSIS' in gs_upper):
                            mouse_go_pro[gs_name] = genes
                        elif 'NEGATIVE' in gs_upper and ('APOPTOTIC' in gs_upper or 'APOPTOSIS' in gs_upper):
                            mouse_go_anti[gs_name] = genes

                    if mouse_go_pro or mouse_go_anti:
                        break

                except Exception as e:
                    log_progress(f"    Error with {go_lib}: {e}")

            if mouse_go_pro:
                rows = []
                for gs_name, genes in mouse_go_pro.items():
                    for gene in genes:
                        rows.append({
                            "gene_symbol": gene,
                            "gene_set_name": gs_name,
                            "source": "GO_BP",
                            "category": "Pro",
                            "organism": "Mouse"
                        })
                df = pd.DataFrame(rows)
                df.to_csv(OUTPUT_DIR / "mouse_go_pro.csv", index=False)
                log_progress(f"  Saved Mouse GO Pro: {len(df)} entries")
                results_summary["Mouse_GO_Pro"] = len(df)

            if mouse_go_anti:
                rows = []
                for gs_name, genes in mouse_go_anti.items():
                    for gene in genes:
                        rows.append({
                            "gene_symbol": gene,
                            "gene_set_name": gs_name,
                            "source": "GO_BP",
                            "category": "Anti",
                            "organism": "Mouse"
                        })
                df = pd.DataFrame(rows)
                df.to_csv(OUTPUT_DIR / "mouse_go_anti.csv", index=False)
                log_progress(f"  Saved Mouse GO Anti: {len(df)} entries")
                results_summary["Mouse_GO_Anti"] = len(df)
        else:
            log_progress("  No Mouse GO Biological Process libraries found")
            log_progress("  Human data will be used for ortholog mapping in next step")

    except Exception as e:
        log_progress(f"  Error retrieving Mouse data: {e}")
        log_progress("  Human data will be used for ortholog mapping in next step")

    # =====================================================
    # Summary
    # =====================================================
    log_progress("\n" + "=" * 60)
    log_progress("DATA ACQUISITION COMPLETE")
    log_progress("=" * 60)

    log_progress("\nResults Summary:")
    for source, count in results_summary.items():
        log_progress(f"  {source}: {count} gene entries")

    # List output files
    log_progress("\nOutput files:")
    for f in sorted(OUTPUT_DIR.glob("*.csv")):
        df = pd.read_csv(f)
        log_progress(f"  {f.name}: {len(df)} rows")

    return results_summary


if __name__ == "__main__":
    try:
        results = main()
        if results:
            print("\n[SUCCESS] Data acquisition completed successfully")
            sys.exit(0)
        else:
            print("\n[WARNING] Data acquisition completed but with limited results")
            sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Data acquisition failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
