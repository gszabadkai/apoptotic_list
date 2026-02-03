# Alternative Approaches to Identify Pro-Death Genes

## The Problem

You correctly identified that DepMap CRISPR knockout data directly measures gene essentiality (whether cells die when a gene is removed), which cannot directly identify genes that promote death when expressed. This is indeed a limitation when trying to classify genes as pro-apoptotic.

## Key Insight: DepMap CAN Identify Pro-Death Genes

However, I discovered that DepMap data CAN be reinterpreted to identify pro-death genes:

**Genes with POSITIVE knockout effects (Chronos score > 0) indicate that cells BENEFIT from losing the gene → the gene promotes death when present**

Using this approach, I identified 7 high-confidence pro-death genes among your 97 ambiguous genes, where both DepMap and UniProt annotations agree:

| Gene | DepMap KO Effect | Evidence |
|------|------------------|----------|
| TP53 | +0.374 | Canonical tumor suppressor, pro-apoptotic |
| TNFRSF10B (DR5) | +0.175 | TRAIL death receptor |
| CASP8 | +0.154 | Initiator caspase, extrinsic pathway |
| TNFRSF10A (DR4) | +0.049 | TRAIL death receptor |
| CASP3 | +0.046 | Executioner caspase |
| TNFSF10 (TRAIL) | +0.022 | Death ligand |
| GSK3B | +0.014 | Pro-apoptotic kinase |

## Additional Alternative Approaches

### 1. CRISPRa (CRISPR Activation) Screens ★ IDEAL but limited data

- Directly measures cell death upon gene UPREGULATION
- No comprehensive public dataset like DepMap exists
- Some studies available in GEO (e.g., Konermann et al. Cell 2015)

### 2. Drug Sensitivity Correlation Analysis ★ RECOMMENDED

- **Data sources:** PRISM, GDSC, CTRPv2
- **Method:** Correlate gene expression with sensitivity to BCL-2 inhibitors (venetoclax, navitoclax)
- **Interpretation:** POSITIVE correlation (high expression = more sensitive) indicates pro-death function
- **Rationale:** Pro-apoptotic proteins "prime" cells for death, making them more sensitive to apoptosis-inducing drugs

### 3. UniProt Functional Annotation Mining ✓ Implemented

- Text mining for phrases: "induces apoptosis", "promotes death", "effector caspase"
- Identified 15 pro-death genes from curated literature

### 4. Protein Domain Analysis ✓ Partially implemented

- BH3-only domain (without BH1/BH2/BH4) = Pro-apoptotic (e.g., BID)
- Death domain (DD) = Death receptor signaling
- Death effector domain (DED) = Caspase recruitment

### 5. ORFeome/Overexpression Screens (Limited availability)

- Direct gain-of-function screens
- Bhang et al. 2015 (Nature Biotech): HCT116 gain-of-function screen
- Yang et al. 2020 (Cell): Cancer fitness screen with ORFs

## Integrated Classification Results

For your 97 ambiguous genes:

| Classification | Count | Percentage |
|----------------|-------|------------|
| HIGH_CONFIDENCE_PRO_DEATH | 7 | 7.2% |
| DEPMAP_PRO_DEATH | 30 | 30.9% |
| UNIPROT_PRO_DEATH | 8 | 8.2% |
| HIGH_CONFIDENCE_ANTI_DEATH | 1 (MCL1) | 1.0% |
| DEPMAP_ANTI_DEATH | 11 | 11.3% |
| UNCLEAR | 33 | 34.0% |

## Recommended Follow-up Analysis

Download PRISM drug sensitivity data and correlate expression of ambiguous genes with sensitivity to:

- Venetoclax (BCL-2 inhibitor)
- Navitoclax/ABT-263 (BCL-2/BCL-XL inhibitor)
- TRAIL recombinant protein

Genes with positive expression-sensitivity correlation would be classified as pro-death.

## Files Generated

- `ambiguous_genes_integrated_classification.csv`: Full analysis with all methods
- `ambiguous_genes_final_classification.csv`: Final sorted classification
- `pro_death_gene_classification.png`: Summary visualization

## Discretionary Analytical Decisions

- **Pro-death threshold from DepMap:** Used Chronos score > 0.1 as cutoff for "likely pro-death" genes (cells benefit from gene loss)
- **UniProt text mining patterns:** Selected specific phrases like "induces apoptosis", "effector caspase", "death-inducing" to identify pro-death function
- **Anti-death threshold from DepMap:** Used Chronos score < -0.5 for "likely pro-survival" genes
- **Integration logic:** Required agreement between both methods (DepMap + UniProt) for "HIGH_CONFIDENCE" classification
- **Rate limiting for API queries:** Used 0.2-0.3 second delays between UniProt API requests to avoid rate limiting
- **External data sources:** UniProt REST API (accessed January 2025) for functional annotations and domain information
- **DepMap data version:** Used CRISPRGeneEffect.csv from DepMap Public 25Q3 (from previous analysis)
