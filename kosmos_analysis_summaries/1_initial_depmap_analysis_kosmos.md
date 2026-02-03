# DepMap Analysis: Do Apoptotic Genes Promote or Reduce Cancer Cell Survival?

## Summary Answer

Based on DepMap CRISPR gene effect data (Chronos scores) from 1,186 cancer cell lines across 1,201 of your apoptotic genes (97.5% coverage), I can provide functional classification for whether these genes promote survival or not.

**For the 97 "Ambiguous" genes (annotated as BOTH pro- and anti-apoptotic in GO):**

| Classification | Count | Percentage | Interpretation |
|----------------|-------|------------|----------------|
| Knockouts REDUCE survival | 60 | 61.9% | Gene promotes survival |
| Knockouts do NOT reduce survival | 37 | 38.1% | Gene is dispensable |

### Key Statistics:
- Mean Chronos score for ambiguous genes: -0.240 (significantly different from 0, t-test p=0.0001)
- This negative mean indicates ambiguous genes are overall biased toward being pro-survival

## Detailed Functional Classification of Ambiguous Genes

### Essential/Pro-survival (14 genes, 14.4%) - Knockouts kill cancer cells:
PRELID1 (-3.07), MYC (-1.98), HSPD1 (-1.94), RPS27A (-1.86), SOD1 (-1.73), SFPQ (-1.61), UBA52 (-1.43), BCL2L1 (-1.18), SOD2 (-1.01), DDX3X (-0.92), CFLAR (-0.75), MCL1 (-0.75), YWHAZ (-0.66), BARD1 (-0.58)

### Likely Pro-survival (29 genes, 29.9%) - Knockouts reduce viability:
Examples: DNAJA1, YWHAE, HTRA2, FADD, ITGB1, UBC, PSEN1, TGFBR1, PSEN2, FAS

### Neutral/Unclear (44 genes, 45.4%) - No clear survival effect:
Examples: BCL2 (-0.01), CASP3 (+0.05), BID (+0.05), RIPK1 (+0.06), TNF (-0.07)

### Dispensable/Anti-survival (10 genes, 10.3%) - Knockouts don't reduce viability:
TP53 (+0.37), CASP2 (+0.25), ADAM8 (+0.19), TNFRSF10B (+0.18), MAPK8 (+0.16), BNIP3L (+0.16), CASP8 (+0.15), MALT1 (+0.11), ZNF268 (+0.11), ANXA1 (+0.10)

## Key Biological Insights

1. **Anti-apoptotic BCL-2 family members are essential:** BCL2L1 (BCL-XL) and MCL1 show strong negative scores, confirming their pro-survival role. Interestingly, BCL2 itself shows a neutral score (-0.01), possibly due to functional redundancy.

2. **Caspases are largely dispensable:** CASP8, CASP2, and CASP3 show positive or neutral scores, suggesting cancer cells can survive without these death executors.

3. **TP53 knockouts increase survival:** The most positive score (+0.37) confirms p53's tumor suppressor role - its loss benefits cancer cell survival.

4. **MYC is highly essential:** Despite being classified as "ambiguous" for apoptosis, MYC is one of the most essential genes in the dataset (-1.98), reflecting its critical role in cell proliferation.

## Important Caveats

1. **Context-dependence:** DepMap data represents average effects across diverse cancer cell lines. Individual genes may have context-specific roles in different cancer types or genetic backgrounds.

2. **GO category does NOT predict function:** There was no significant difference in Chronos scores between GO-annotated Pro-apoptotic, Anti-apoptotic, and Ambiguous categories (Kruskal-Wallis p=0.21), suggesting GO annotations do not reliably predict functional essentiality in cancer cells.

3. **Cancer cell context:** These findings apply to cancer cell survival and may not reflect normal physiological apoptosis regulation.

## Files Generated

- `all_apoptotic_genes_depmap_classified.csv`: Complete classification of all 1,201 genes
- `ambiguous_genes_depmap_classified.csv`: Focused analysis of 97 ambiguous genes
- `depmap_apoptosis_analysis.png`: Summary visualization

## Discretionary Analytical Decisions

- **Data source:** Used DepMap Public 25Q3 (September 2025) CRISPR gene effect data
- **Essentiality threshold:** Applied commonly-used threshold of Chronos score < -0.5 for "essential" genes
- **Classification thresholds:** Used score < -0.5 (essential), -0.5 to -0.1 (likely pro-survival), -0.1 to +0.1 (neutral), >+0.1 (likely dispensable)
- **Statistical tests:** Used Kruskal-Wallis test for comparing categories due to non-normal distribution of scores
- **Gene symbol mapping:** Matched gene symbols from input file to DepMap column names (format: "SYMBOL (entrez_id)")
- **Summary metric:** Used mean Chronos score across all cell lines as the primary measure of essentiality (median scores showed similar patterns)
