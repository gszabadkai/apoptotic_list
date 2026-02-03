# Consolidated Cell Death Gene List

## Overview

This repository contains a curated list of **1,232 cell death-related genes** with functional classifications (pro-death vs pro-survival) derived from multiple sources and analytical approaches.

## Main Output File

**`cell_death_genes_consolidated.csv`** - The final consolidated gene list with 18 columns:

### Identifiers
| Column | Description |
|--------|-------------|
| `human_symbol` | Human gene symbol |
| `mouse_symbol` | Mouse gene symbol (1,152/1,232 mapped) |
| `human_ensembl` | Human Ensembl gene ID |
| `mouse_ensembl` | Mouse Ensembl gene ID |

### Classification
| Column | Description |
|--------|-------------|
| `effect` | Functional effect: `pro-death`, `pro-survival`, `ambiguous`, `unclassified` |
| `pathway` | Cell death pathway: `apoptosis`, `CICD` (caspase-independent), `both` |
| `is_core` | TRUE if gene is a core regulator from literature curation |
| `is_mitochondrial` | TRUE if gene is in MitoCarta 3.0 |

### Database Sources
| Column | Description |
|--------|-------------|
| `sources` | Original source databases (comma-separated) |
| `in_GO` | TRUE if in GO apoptosis terms |
| `in_KEGG` | TRUE if in KEGG apoptosis pathway |
| `in_Reactome` | TRUE if in Reactome apoptosis |
| `in_Hallmark` | TRUE if in MSigDB Hallmark apoptosis |

### Metadata
| Column | Description |
|--------|-------------|
| `confidence` | Classification confidence level |
| `evidence_score` | Evidence strength (1-5) |
| `original_category` | Original K-dense category |
| `family_pathway` | Gene family/pathway annotation |
| `modality` | Cell death modality (e.g., Parthanatos, Ferroptosis) |

## Summary Statistics

### Effect Classification
| Effect | Count |
|--------|-------|
| Pro-death | 512 |
| Pro-survival | 587 |
| Ambiguous | 42 |
| Unclassified | 91 |

### Database Coverage
| Source | Genes |
|--------|-------|
| GO | 1,012 |
| Reactome | 215 |
| Hallmark (MSigDB) | 161 |
| KEGG | 84 |

### Special Annotations
- **Core genes** (literature-curated): 57
- **Mitochondrial** (MitoCarta 3.0): 90

## Data Sources & Methods

### 1. K-dense Initial List (`results/`)
- Source databases: GO, KEGG, Reactome, MSigDB Hallmark
- Initial categories: Pro-apoptotic, Anti-apoptotic, Ambiguous, Unspecified
- 1,232 genes total

### 2. Kosmos Literature Curation (`kosmos_analysis_summaries/`)
- **Core apoptosis genes**: 42 genes from literature review
- **Core CICD genes**: 26 genes (caspase-independent cell death)
- Manual classification of pro-death vs pro-survival roles

### 3. Functional Reclassification via DepMap/PRISM (`kosmos_analysis_summaries/`)
Ambiguous and unspecified genes were reclassified using multiple approaches:

| Step | Analysis | Description |
|------|----------|-------------|
| 1 | DepMap CRISPR | Knockout effects on cell viability |
| 2 | Alternative approaches | UniProt annotations, literature |
| 3 | PRISM drug sensitivity | Correlation with Bcl-2 antagonists and TRAIL |
| 4 | Final integration | Combined all evidence sources |

See `kosmos_analysis_summaries/*.md` for detailed methodology narratives.

> **Note**: Full analysis notebooks and raw data (~2.9GB) are archived separately. 
> Contact repository owner for access or see Zenodo deposit [DOI pending].

### 4. MitoCarta 3.0 Integration
- Mouse mitochondrial proteome annotation
- 90 cell death genes with mitochondrial localization

## Usage

```r
# R
library(tidyverse)
genes <- read_csv("cell_death_genes_consolidated.csv")

# Filter for pro-death mitochondrial genes
mito_prodeath <- genes %>%
  filter(effect == "pro-death", is_mitochondrial)

# Filter for core apoptosis regulators
core_apoptosis <- genes %>%
  filter(is_core, pathway %in% c("apoptosis", "both"))
```

```python
# Python
import pandas as pd
genes = pd.read_csv("cell_death_genes_consolidated.csv")

# Pro-survival genes in KEGG
kegg_prosurvival = genes[(genes['effect'] == 'pro-survival') & genes['in_KEGG']]
```

## Repository Structure

```
├── cell_death_genes_consolidated.csv    # Main output file
├── README_consolidated.md               # This file
├── results/                             # K-dense source files
│   ├── final_apoptotic_gene_list.csv
│   ├── GO_apoptosis_genes.csv
│   ├── KEGG_apoptosis_genes.csv
│   ├── Reactome_apoptosis_genes.csv
│   └── Hallmark_apoptosis_genes.csv
└── kosmos_analysis_summaries/           # Reclassification analysis
    ├── 1_initial_depmap_analysis_kosmos.md
    ├── 2_alternative_approaches_kosmos.md
    ├── 3_PRISM_drug_sensitivity_kosmos.md
    ├── 4_final_analysis_apoptotic_genes_kosmos.md
    ├── core_apoptosis_genes_kosmos.csv
    └── core_caspase_independent_cell_death_genes_kosmos.csv
```

## Citation

If you use this gene list, please cite the underlying databases:
- Gene Ontology (GO)
- KEGG Pathway Database
- Reactome Pathway Database  
- MSigDB Hallmark Gene Sets
- MitoCarta 3.0
- DepMap/PRISM (Broad Institute)
