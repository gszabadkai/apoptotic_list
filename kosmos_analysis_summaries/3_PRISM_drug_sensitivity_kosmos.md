# Drug Sensitivity Correlation Analysis: Identifying Pro-Death Genes

## Analysis Summary

I performed the recommended follow-up analysis by correlating gene expression with sensitivity to BCL-2 inhibitors (Venetoclax, Navitoclax) and TRAIL across 707 cancer cell lines.

**Key Interpretation:** NEGATIVE correlation with drug sensitivity (AUC) indicates a pro-death gene because high expression of the gene leads to increased sensitivity (lower AUC = more cell death).

## Key Findings

### HIGH CONFIDENCE PRO-DEATH GENES (Drug Sensitivity in ≥2 drugs)

| Gene | Navitoclax (r) | Venetoclax (r) | TRAIL (r) | Interpretation |
|------|----------------|----------------|-----------|----------------|
| BCL2 | -0.261 | -0.205 | +0.085 | BCL-2 dependent cells are most sensitive to BCL-2 inhibitors |
| CASP2 | -0.252 | -0.145 | +0.072 | PIDDosome component, activates apoptosis |
| PIDD1 | -0.226 | -0.192 | +0.128 | PIDDosome component, death-inducing |
| TP53 | -0.123 | -0.111 | +0.038 | Canonical tumor suppressor |
| PAK2 | -0.140 | -0.101 | +0.109 | Pro-apoptotic kinase (unexpected) |

### TRAIL-SPECIFIC PRO-DEATH GENES (Death Receptor Pathway)

| Gene | TRAIL (r) | Function |
|------|-----------|----------|
| CASP8 | -0.253 | Initiator caspase (strongest signal) |
| TNFRSF10B (DR5) | -0.207 | TRAIL death receptor |
| TNFRSF10A (DR4) | -0.166 | TRAIL death receptor |
| SQSTM1 | -0.180 | Autophagy receptor |
| TRADD | -0.118 | Death domain adapter |

### BCL-2 INHIBITOR-SPECIFIC PRO-DEATH GENES

| Gene | Navitoclax (r) | Function |
|------|----------------|----------|
| LILRB1 | -0.207 | Immune receptor (unexpected) |
| CCAR2 | -0.184 | Cell cycle regulator |
| TRAF6 | -0.161 | TNF receptor signaling |
| MAPK8 (JNK1) | -0.150 | Stress-activated kinase |
| HTRA2 | -0.133 | Mitochondrial serine protease |
| BCL2L1 (BCL-XL) | -0.106 | Navitoclax target |
| BID | -0.112 | BH3-only protein |

### HIGH CONFIDENCE ANTI-DEATH GENES

| Gene | Navitoclax (r) | Venetoclax (r) | Evidence |
|------|----------------|----------------|----------|
| MCL1 | +0.261 | +0.144 | Alternative survival factor - high expression = resistance |
| SQSTM1 | +0.261 | +0.116 | Autophagy protects from BCL-2 inhibitors |
| PRELID1 | +0.137 | +0.083 | Mitochondrial lipid transfer |

## Integrated Classification Results (All 3 Methods)

Combining DepMap knockout, UniProt annotation, and drug sensitivity data:

| Classification | Count | Percentage |
|----------------|-------|------------|
| HIGH_CONFIDENCE_PRO_DEATH | 13 | 13.4% |
| LIKELY_PRO_DEATH | 21 | 21.6% |
| CONFLICTING_EVIDENCE | 15 | 15.5% |
| UNCLEAR | 16 | 16.5% |
| LIKELY_ANTI_DEATH | 28 | 28.9% |
| HIGH_CONFIDENCE_ANTI_DEATH | 4 | 4.1% |

## Biological Insights

1. **BCL2 paradox explained:** High BCL2 expression correlates with increased sensitivity to BCL-2 inhibitors because these cells are "BCL-2 addicted" - dependent on BCL-2 for survival.

2. **PIDDosome validation:** PIDD1 and CASP2 showed strong pro-death signals, validating the PIDDosome as a death-inducing complex.

3. **TRAIL pathway validated:** CASP8, TNFRSF10A/B (DR4/DR5) showed expected pro-death signals specifically with TRAIL treatment.

4. **MCL1 confers resistance:** High MCL1 expression provides alternative survival, making cells resistant to BCL-2 inhibitors.

## Limitations

- Effect sizes are modest (|r| = 0.1-0.3), typical for complex phenotypes
- SOD2 was not available in the expression dataset
- Cancer cell lines may not represent normal physiology
- Correlations reflect basal expression, not induced responses

## Output Files

- `ambiguous_genes_drug_sensitivity_analysis.csv` - Complete results
- `drug_sensitivity_correlations.png` - Correlation heatmap
- `drug_sensitivity_analysis_summary.png` - Summary figures

## Discretionary Analytical Decisions

- **Statistical method:** Used Spearman correlation (robust to outliers) rather than Pearson correlation
- **Significance threshold:** Set FDR-adjusted p-value < 0.05 AND |correlation| > 0.1 for biological relevance
- **Multiple testing correction:** Applied Benjamini-Hochberg FDR correction separately for each drug
- **Drug sensitivity metric:** Used AUC_PUBLISHED from GDSC; averaged values when cell lines had data from both GDSC1 and GDSC2
- **Cell line filtering:** Included only cell lines with both expression and drug sensitivity data (707 of 963)
- **Expression data:** Used default entries only (IsDefaultEntryForModel = 'Yes') to avoid duplicate cell lines
- **Classification integration:** Required ≥2 concordant evidence sources for "HIGH_CONFIDENCE" designation
- **External datasets used:**
  - GDSC drug sensitivity data (Sanger dose-response, via DepMap portal)
  - CCLE/DepMap gene expression data (OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv, 25Q3)
  - DepMap Model metadata (Model.csv, 25Q3)
- **Drug identification:** Matched drugs by GDSC drug IDs (Venetoclax: 412/1909, Navitoclax: 1011, TRAIL/rTRAIL: 1261)
