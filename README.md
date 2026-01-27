# Apoptotic Gene List Analysis

A comprehensive bioinformatics pipeline for assembling and annotating apoptotic protein lists from multiple database sources (GO, KEGG, Reactome, MSigDB Hallmark).

## Quick Start

### Prerequisites
- Python 3.10+
- pip or uv package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/apoptotic-gene-list.git
cd apoptotic-gene-list

# Install dependencies
pip install -r requirements.txt

# Or with uv (faster)
uv sync
```

### Running the Analysis

The workflow scripts are designed to be run sequentially:

```bash
# Step 1: Data Acquisition (fetch gene sets from MSigDB)
python workflow/01_data_acquisition.py

# Step 2: Homology Mapping (Human-Mouse ortholog mapping)
python workflow/02_homology_mapping.py

# Step 3: Gene Consolidation (merge and categorize)
python workflow/03_gene_consolidation.py

# Step 4: ID Annotation (add Ensembl IDs, generate output)
python workflow/04_id_annotation.py
```

### Output

The main deliverable is `results/final_apoptotic_gene_list.csv` containing:
- **1,232 apoptotic genes** with Human and Mouse gene symbols
- Ensembl IDs for both species (98%+ coverage)
- Functional categories: Pro-apoptotic, Anti-apoptotic, Ambiguous, Unspecified
- Evidence sources and confidence scores

---

## Directory Structure

- `user_data/` - Input files from user
- `workflow/` - Implementation scripts and notebooks
- `data/` - Intermediate data files
- `logs/` - Execution logs
- `figures/` - Generated plots and visualizations
- `results/` - Final analysis outputs
- `reports/` - Generated reports

## Implementation Progress

### Step 1: Data Acquisition (COMPLETED)

**Objective**: Retrieve apoptotic gene sets from MSigDB (GO, KEGG, Reactome, Hallmark) for Human and Mouse.

**Script**: `workflow/01_data_acquisition.py`

**Execution Summary**:
- Successfully queried MSigDB via gseapy library
- Retrieved gene sets from multiple databases
- Saved structured CSV files with source and category metadata

**Output Files** (in `workflow/raw_data/`):

| File | Rows | Description |
|------|------|-------------|
| `human_go_pro.csv` | 787 | GO Biological Process - Pro-apoptotic genes (24 gene sets) |
| `human_go_anti.csv` | 1,171 | GO Biological Process - Anti-apoptotic genes (31 gene sets) |
| `human_kegg_apoptosis.csv` | 84 | KEGG Apoptosis pathway (HSA04210) |
| `human_reactome_apoptosis.csv` | 539 | Reactome Apoptosis pathways (17 pathways) |
| `human_hallmark_apoptosis.csv` | 161 | MSigDB Hallmark Apoptosis |
| `mouse_go_pro.csv` | 787 | Mouse GO Pro-apoptotic genes |
| `mouse_go_anti.csv` | 1,171 | Mouse GO Anti-apoptotic genes |

**Data Structure** (all CSV files):
```
gene_symbol,gene_set_name,source,category,organism
```

**Key Gene Sets Retrieved**:
- **GO Pro-apoptotic**: positive regulation of apoptotic process, positive regulation of cysteine-type endopeptidase activity, etc.
- **GO Anti-apoptotic**: negative regulation of apoptotic process, negative regulation of neuron apoptotic process, etc.
- **KEGG**: HSA04210 APOPTOSIS (84 genes including BAD, APAF1, CASP3, etc.)
- **Reactome**: Apoptosis R-HSA-109581 (178 genes), Intrinsic Pathway, Extrinsic signaling, etc.
- **Hallmark**: Apoptosis (161 genes)

**Libraries Used**:
- gseapy 1.1.11
- pandas 2.3.3

---

### Step 2: Species & Homology Mapping (COMPLETED)

**Objective**: Create a comprehensive orthology mapping between Human and Mouse genes to enable cross-species analysis.

**Script**: `workflow/02_homology_mapping.py`

**Methodology**:
1. Loaded all raw data CSV files to extract unique Human (1,232 genes) and Mouse (1,012 genes) gene symbols
2. Used MyGene.info API with HomoloGene database for ortholog lookup
3. Performed bidirectional mapping (Human→Mouse and Mouse→Human)
4. Converted Entrez Gene IDs to proper gene symbols
5. Handled one-to-many mappings (kept all valid orthologs)

**Execution Summary**:
- Human → Mouse lookup: 93.1% success rate (1,147/1,232 genes)
- Mouse → Human lookup: 90.6% success rate (917/1,012 genes)
- Total unique ortholog pairs: 1,183
- Mapping cardinality: 18 human genes have multiple mouse orthologs, 4 mouse genes have multiple human orthologs

**Output Files** (in `workflow/data/`):

| File | Rows | Description |
|------|------|-------------|
| `orthology_mapping.csv` | 1,183 | Simplified Human-Mouse symbol mapping (2 columns) |
| `orthology_mapping_full.csv` | 1,183 | Full mapping with Entrez IDs and source information |

**Data Structure** (`orthology_mapping.csv`):
```
human_symbol,mouse_symbol
AATF,Aatf
ABCA7,Abca7
ABL1,Abl1
...
```

**Libraries Used**:
- mygene (MyGene.info Python client)
- pandas 2.3.3

---

### Step 3: Gene Set Consolidation (COMPLETED)

**Objective**: Consolidate raw gene sets into a unified list of apoptotic proteins, resolving Human/Mouse orthology and assigning functional categories.

**Script**: `workflow/03_gene_consolidation.py`

**Methodology**:
1. Loaded orthology mapping (1,183 human-mouse pairs)
2. Loaded all raw data sources (GO Pro/Anti, KEGG, Reactome, Hallmark)
3. Created master dataset keyed by Human gene symbol
4. Aggregated evidence from all sources for each gene
5. Applied categorization logic:
   - **Ambiguous/Dual-role**: Gene has BOTH Pro AND Anti evidence
   - **Pro-apoptotic**: Gene has ONLY Pro evidence (regardless of general sources)
   - **Anti-apoptotic**: Gene has ONLY Anti evidence (regardless of general sources)
   - **Unspecified**: Gene appears ONLY in general sources (KEGG/Reactome/Hallmark)

**Execution Summary**:
- Total consolidated genes: 1,232
- Genes with mouse orthologs: 1,150 (93.3%)
- Average evidence score: 1.28 sources per gene
- Multi-source genes: 241 (19.6%)

**Category Distribution**:
| Category | Count | Percentage |
|----------|-------|------------|
| Anti-apoptotic | 525 | 42.6% |
| Pro-apoptotic | 390 | 31.7% |
| Unspecified | 220 | 17.9% |
| Ambiguous | 97 | 7.9% |

**Top Genes by Evidence Score (5 sources)**:
- BCL2L1, BID, CASP3, CASP8, CFLAR, FASLG, TNF, TNFSF10 - All classified as "Ambiguous" due to presence in both GO Pro and Anti-apoptotic gene sets

**Output Files** (in `workflow/data/`):

| File | Rows | Description |
|------|------|-------------|
| `consolidated_apoptosis_genes.csv` | 1,232 | Unified gene list with categories and sources |
| `gene_category_summary.txt` | - | Summary statistics for categorization |

**Data Structure** (`consolidated_apoptosis_genes.csv`):
```
human_symbol,mouse_symbol,category,sources,evidence_score
BCL2L1,Bcl2l1,Ambiguous,"GO_Anti_Human,GO_Pro_Human,Hallmark,KEGG,Reactome",5
BAX,Bax,Pro-apoptotic,"GO_Pro_Human,Hallmark,KEGG,Reactome",4
DFFA,Dffa,Anti-apoptotic,"GO_Anti_Human,Hallmark,KEGG,Reactome",4
...
```

**Libraries Used**:
- pandas 2.3.3
- collections (defaultdict)

**Notes**:
- The high number of Anti-apoptotic genes (42.6%) reflects the GO Biological Process annotation strategy which includes many "negative regulation" terms
- Ambiguous genes (7.9%) are scientifically interesting as they often represent context-dependent regulators
- The 8 genes with maximum evidence score (5 sources) are key apoptosis regulators well-documented across databases

---

### Step 4: ID Annotation & Finalization (COMPLETED)

**Objective**: Annotate the consolidated gene list with Ensembl IDs and generate final deliverables.

**Script**: `workflow/04_id_annotation.py`

**Methodology**:
1. Loaded consolidated gene list (1,232 genes)
2. Used MyGene.info API to batch-query Ensembl Gene IDs for Human and Mouse symbols
3. Merged Ensembl IDs into the dataset
4. Generated category distribution visualization

**Execution Summary**:
- Human Ensembl ID coverage: 98.6% (1,215/1,232 genes)
- Mouse Ensembl ID coverage: 98.3% (1,131/1,150 genes with orthologs)
- Unmapped genes: typically retired symbols, pseudogenes, or alternate nomenclature

**Category Distribution**:
| Category | Count | Percentage |
|----------|-------|------------|
| Anti-apoptotic | 525 | 42.6% |
| Pro-apoptotic | 390 | 31.7% |
| Unspecified | 220 | 17.9% |
| Ambiguous | 97 | 7.9% |

**Primary Deliverables**:

| File | Description |
|------|-------------|
| `results/final_apoptotic_gene_list.csv` | **Final annotated gene list** with Human/Mouse symbols, Ensembl IDs, and categories (1,232 genes) |
| `figures/category_distribution.png` | Bar chart showing distribution of functional categories |

**Data Structure** (`results/final_apoptotic_gene_list.csv`):
```
human_symbol,human_ensembl_id,mouse_symbol,mouse_ensembl_id,category,sources,evidence_score
BCL2L1,ENSG00000171552,Bcl2l1,ENSMUSG00000007659,Ambiguous,"GO_Anti_Human,GO_Pro_Human,Hallmark,KEGG,Reactome",5
BAX,ENSG00000087088,Bax,ENSMUSG00000003873,Pro-apoptotic,"GO_Pro_Human,Hallmark,KEGG,Reactome",4
...
```

**Libraries Used**:
- mygene (MyGene.info Python client)
- pandas 2.3.3
- matplotlib 3.10.3

---

### Step 5: Source-Specific Breakdown (COMPLETED)

**Objective**: Generate separate gene lists filtered by data source (KEGG, Reactome, MSigDB Hallmark, GO), preserving the consensus functional categorization.

**Script**: `workflow/05_source_breakdown.py`

**Methodology**:
1. Loaded the final consolidated gene list (1,232 genes)
2. Filtered genes by source presence in the `sources` column
3. Preserved the consensus category (Pro/Anti/Ambiguous/Unspecified) from the consolidated analysis
4. Sorted output by category, then by gene symbol

**Execution Summary**:
| Source | Total Genes | Pro | Anti | Ambiguous | Unspecified |
|--------|-------------|-----|------|-----------|-------------|
| **KEGG** | 84 | 13 | 17 | 17 | 37 |
| **Reactome** | 215 | 47 | 24 | 24 | 120 |
| **Hallmark** | 161 | 29 | 25 | 26 | 81 |
| **GO** | 1,012 | 390 | 525 | 97 | 0 |

**Output Files** (in `results/source_breakdown/`):

| File | Description |
|------|-------------|
| `apoptosis_genes_KEGG.csv` | 84 genes from KEGG Apoptosis pathway |
| `apoptosis_genes_Reactome.csv` | 215 genes from Reactome Apoptosis pathways |
| `apoptosis_genes_Hallmark.csv` | 161 genes from MSigDB Hallmark Apoptosis |
| `apoptosis_genes_GO.csv` | 1,012 genes from GO Biological Process annotations |
| `breakdown_summary.txt` | Summary statistics for all sources |

**Data Structure** (all breakdown CSVs):
```
human_symbol,human_ensembl_id,mouse_symbol,mouse_ensembl_id,category,sources,evidence_score
```

**Notes**:
- GO has the highest coverage (1,012 genes) because it includes detailed GO Biological Process annotations
- GO has no "Unspecified" genes because all GO genes have explicit Pro or Anti directionality in the source data
- KEGG/Reactome/Hallmark contain "Unspecified" genes that appear only in general apoptosis pathways without directional annotation
- The category assigned is the **consensus category** from the consolidated analysis, adding directional value to sources like KEGG and Reactome

---

## Project Complete

All steps have been successfully completed. The final deliverables are:

**`results/final_apoptotic_gene_list.csv`** - A comprehensive list of 1,232 apoptotic genes with:
- Human gene symbols and Ensembl IDs (98.6% coverage)
- Mouse ortholog symbols and Ensembl IDs (98.3% coverage)
- Functional categories (Pro-apoptotic, Anti-apoptotic, Ambiguous, Unspecified)
- Evidence sources and confidence scores

**`results/source_breakdown/`** - Source-specific gene lists:
- `apoptosis_genes_KEGG.csv` - 84 genes from KEGG pathway
- `apoptosis_genes_Reactome.csv` - 215 genes from Reactome pathways
- `apoptosis_genes_Hallmark.csv` - 161 genes from MSigDB Hallmark
- `apoptosis_genes_GO.csv` - 1,012 genes from GO Biological Process

---

## Data Sources

This analysis integrates data from the following curated databases:

| Source | Description | Reference |
|--------|-------------|-----------|
| **GO Biological Process** | Gene Ontology annotations for apoptotic process regulation | [Gene Ontology](http://geneontology.org/) |
| **KEGG** | KEGG Apoptosis pathway (hsa04210) | [KEGG](https://www.kegg.jp/) |
| **Reactome** | Reactome Apoptosis pathways | [Reactome](https://reactome.org/) |
| **MSigDB Hallmark** | Hallmark Apoptosis gene set | [MSigDB](https://www.gsea-msigdb.org/) |
| **MyGene.info** | Gene ID mapping and ortholog lookup | [MyGene.info](https://mygene.info/) |

---

## Citation

If you use this gene list in your research, please cite the underlying databases:

```
Gene Ontology Consortium. The Gene Ontology resource: enriching a GOld mine. Nucleic Acids Research. 2021.
Kanehisa M, et al. KEGG: Kyoto Encyclopedia of Genes and Genomes. Nucleic Acids Research. 2000.
Jassal B, et al. The Reactome Pathway Knowledgebase. Nucleic Acids Research. 2020.
Liberzon A, et al. The Molecular Signatures Database Hallmark Gene Set Collection. Cell Systems. 2015.
Wu C, et al. BioGPS and MyGene.info: organizing online, gene-centric information. Nucleic Acids Research. 2013.
```

---

## License

This repository is provided for research purposes. The gene list data is derived from public databases; please refer to each source's licensing terms for commercial use.

---

*Generated with [K-Dense](https://www.k-dense.ai) - AI-powered scientific computing*
