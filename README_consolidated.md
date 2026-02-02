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

### 1. K-dense Initial List
- Source databases: GO, KEGG, Reactome, MSigDB Hallmark
- Initial categories: Pro-apoptotic, Anti-apoptotic, Ambiguous, Unspecified
- 1,232 genes total

### 2. Kosmos Literature Curation
- Core apoptosis genes: 42 genes from literature review
- Core CICD genes: 26 genes (caspase-independent cell death)
- Manual classification of pro-death vs pro-survival roles

### 3. Functional Reclassification (Steps 1-4)
Ambiguous and unspecified genes were reclassified using:
1. **DepMap analysis**: CRISPR knockout effects on cell viability
2. **UniProt annotation**: Functional descriptions
3. **PRISM drug sensitivity**: Correlation with Bcl-2 antagonists and TRAIL

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
```

## Related Files

- `results/` - Individual source files from K-dense analysis

## Citation

If you use this gene list, please cite the underlying databases:
- Gene Ontology (GO)
- KEGG Pathway Database
- Reactome Pathway Database  
- MSigDB Hallmark Gene Sets
- MitoCarta 3.0
- DepMap/PRISM (Broad Institute)
