# Unified Apoptotic Gene Classification Analysis

## Overview

I have successfully applied the same three-source integration pipeline (DepMap CRISPR knockout, UniProt annotations, and drug sensitivity correlations) to classify the 220 genes originally labeled as "Unspecified" in the final_apoptotic_gene_list.csv file. These results have been combined with the previous analysis of 97 "Ambiguous" genes and the original annotations to create a comprehensive unified list of all 1,232 genes.

## Final Classification Results

| Classification | Count | Percentage |
|----------------|-------|------------|
| PRO-APOPTOTIC | 507 | 41.2% |
| ANTI-APOPTOTIC | 588 | 47.7% |
| AMBIGUOUS | 42 | 3.4% |
| UNCLASSIFIED | 95 | 7.7% |

## Key Findings for Unspecified Genes

From the 220 "Unspecified" genes:

- 72 classified as PRO-APOPTOTIC (including 19 high-confidence)
- 44 classified as ANTI-APOPTOTIC (including 12 high-confidence)
- 42 showed CONFLICTING evidence (both pro- and anti-death signals)
- 62 remained UNCLASSIFIED (insufficient evidence)

### High-Confidence Pro-Apoptotic Genes (Unspecified → Pro-Apoptotic)

| Gene | Evidence | Key Findings |
|------|----------|--------------|
| CASP6 | DepMap+UniProt | Essential executioner caspase; UniProt: "programmed cell death, execution of apoptosis" |
| CASP7 | DepMap+UniProt | Executioner caspase involved in pyroptosis |
| DFFB | UniProt+Drug | DNA fragmentation factor; sensitizes to Navitoclax |
| TNFRSF1A | DepMap+UniProt | TNF receptor; death-inducing function |
| STK24 | DepMap+UniProt | Kinase that "promotes apoptosis, promotes cell death" |
| PRF1 | DepMap+UniProt+Drug | Perforin; programmed cell death executor |
| BIK | DepMap+UniProt | BH3-only protein; pro-apoptotic BCL-2 family |
| GSDMD | UniProt | Gasdermin D; pyroptosis executor |

### High-Confidence Anti-Apoptotic Genes (Unspecified → Anti-Apoptotic)

| Gene | Evidence | Key Findings |
|------|----------|--------------|
| CDK2 | DepMap+Drug | Essential for survival; high expression correlates with drug resistance |
| ETF1 | DepMap+Drug | Essential gene (knockout effect: -2.21) |
| KPNB1 | DepMap+Drug | Essential gene (knockout effect: -2.51) |
| CLSPN | DepMap+Drug | DNA damage checkpoint; promotes survival |
| PSMA2/5/7, PSMB4/5/6/7 | DepMap+Drug | Proteasome subunits; essential for survival |
| DYNLL1 | DepMap+Drug | Dynein light chain; pro-survival |
| AKT3 | DepMap+UniProt | UniProt: "cell survival" function |

### Genes with Conflicting Evidence (42 genes)

Notable examples showing both pro- and anti-death characteristics:

- **Proteasome subunits (PSMC1-6, PSMD2-14):** Essential for cell survival but also required for apoptosis execution
- **PAK1:** Pro-survival role (UniProt) but positively correlated with drug sensitivity
- **MAP3K14:** Pro-survival UniProt annotation but pro-death drug sensitivity
- **TANK:** Cell survival function but conflicting drug correlations

## Methodology

### DepMap CRISPR Knockout (216/220 genes covered):

- Negative effect (<-0.5): gene supports survival → ANTI-APOPTOTIC
- Positive effect (>0): gene knockout is beneficial → PRO-APOPTOTIC

### UniProt Function Annotation (215/220 genes with text):

- Text mining for apoptosis-related terms
- 30 genes classified as pro-death
- 7 genes classified as anti-death
- 182 genes with no clear apoptosis annotation

### Drug Sensitivity Correlations (695 cell lines):

- NEGATIVE correlation with AUC = PRO-APOPTOTIC (high expression → more sensitivity)
- POSITIVE correlation with AUC = ANTI-APOPTOTIC (high expression → resistance)
- Drugs used: Navitoclax (943 cell lines), Venetoclax (742 cell lines), rTRAIL (905 cell lines)

## Output Files Generated

- `final_unified_apoptotic_gene_list_by_activity.csv`: Complete ranked list of all 1,232 genes sorted by apoptotic activity score
- `unspecified_genes_analysis.csv`: Detailed analysis of 220 Unspecified genes
- `comprehensive_apoptotic_gene_classification.csv`: Full evidence details including drug correlation coefficients
- `unified_classification_summary.png`: Visualization of classification results

## Interpretation of Scoring

- **Score +2 to +3:** High confidence PRO-APOPTOTIC (promotes cell death)
- **Score +1:** Likely PRO-APOPTOTIC
- **Score 0:** Neutral/unclear
- **Score -1:** Likely ANTI-APOPTOTIC
- **Score -2 to -3:** High confidence ANTI-APOPTOTIC (promotes cell survival)

## Limitations

- Effect sizes for drug sensitivity correlations are modest (|r| = 0.1-0.3), typical for complex phenotypes
- 4 genes (BIRC4, CHP, NGFB, TMED7-TICAM2) were not found in DepMap or expression data
- Cancer cell line data may not fully represent normal physiology
- 95 genes (30% of newly analyzed) remained unclassified due to insufficient evidence
- Proteasome genes show paradoxical behavior (essential for both survival and apoptosis execution)

## Discretionary Analytical Decisions

- **Statistical method:** Used Spearman correlation (robust to outliers) for drug sensitivity analysis
- **Significance threshold:** FDR-adjusted p-value < 0.05 AND |correlation| > 0.1 for biological relevance
- **Multiple testing correction:** Benjamini-Hochberg FDR correction applied separately for each drug
- **DepMap classification thresholds:** knockout effect < -1.0 for essential, < -0.5 for pro-survival, > 0.1 for pro-death
- **Evidence integration:** Required ≥2 concordant evidence sources for "HIGH_CONFIDENCE" designation
- **UniProt text mining patterns:** Expanded pattern matching to include terms like "programmed cell death", "pyroptosis", "executioner", "required for apoptosis"
- **Drug sensitivity metric:** Used AUC_PUBLISHED from GDSC
- **Cell line filtering:** Used only default entries (IsDefaultEntryForModel = 'Yes') to avoid duplicates
- **External datasets used:**
  - DepMap CRISPR gene effect data (CRISPRGeneEffect.csv)
  - CCLE/DepMap gene expression data (OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv, 25Q3)
  - GDSC drug sensitivity data (sanger-dose-response.csv)
  - UniProt protein function annotations (REST API, SwissProt reviewed entries)
- **Drug IDs:** Venetoclax (1909), Navitoclax (1011), rTRAIL (1261)
