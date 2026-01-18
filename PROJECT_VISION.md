# Policy Inequality Simulator - Simplified Vision

## Overview

A tool that allows policymakers to enter a plain text prompt (e.g., "how would a child benefit affect inequality") and receive a comprehensive cost-benefit analysis showing how the policy would affect current inequality measures in the United States.

## Key Simplifications from Original Vision

- **Geographic Focus**: United States (not UK)
- **Data Source**: CPS ASEC (Current Population Survey Annual Social and Economic Supplement) or ACS (American Community Survey)
- **No Synthetic Data**: Use actual microdata from Census Bureau
- **Current Outcomes**: Focus on inequality of current income/outcomes rather than future mobility projections
- **Faster Timeline**: Achievable in months rather than years

## Core Functionality

### Input
Policymaker enters natural language policy description:
- "How would a $300/month child benefit affect inequality?"
- "What would expanding EITC by 20% do to income inequality?"
- "Impact of universal child care on household income distribution"

### Processing
1. **Parse policy** from natural language into structured parameters
2. **Load microdata** (CPS ASEC or ACS household-level data)
3. **Apply policy** to relevant households based on eligibility rules
4. **Calculate effects** on household income
5. **Measure inequality** (Gini coefficient, income percentiles, poverty rates, etc.)
6. **Estimate costs** (number of beneficiaries × benefit amount)

### Output (delivered in minutes)
- Before/after inequality measures
- Cost estimate (total program cost)
- Cost-benefit ratio
- Distribution of benefits across income deciles
- Visualizations (Lorenz curves, income distribution changes)
- Plain-language summary

## Technical Architecture

### Data Layer
- **Primary Data**: CPS ASEC microdata (60,000+ households annually)
  - Individual and household income
  - Demographics (age, family composition, geography)
  - Employment and earnings
  - Transfer program participation
- **Alternative**: ACS microdata (larger sample, ~3.5M households)
- **Storage**: Parquet files for fast querying
- **Update Cycle**: Annual refresh with new data releases

### Policy Engine
- **Semantic Parser**: LLM (Claude/GPT-4) converts text to structured policy parameters
  - Policy type (child benefit, tax credit, wage subsidy, etc.)
  - Amount and structure (flat, percentage, phased)
  - Eligibility criteria (income thresholds, family composition, employment status)
- **Microsimulation**: Apply policy rules to each household in dataset
  - Calculate benefit eligibility
  - Compute new household income
  - Account for tax implications and benefit interactions

### Analysis Module
- **Inequality Metrics**:
  - Gini coefficient
  - P90/P10, P90/P50, P50/P10 ratios
  - Top 10%/Bottom 50% income shares
  - Poverty rates (SPM and official)
  - Income percentile thresholds
- **Distributional Analysis**:
  - Winners/losers by income decile
  - Average benefit by demographic group
  - Geographic variation (state/region)
- **Cost Estimation**:
  - Total program cost
  - Cost per beneficiary
  - Cost per point of Gini reduction
  - Budget impact

### Output Generation
- **LLM-Generated Report**: Plain language summary of findings
- **Visualizations**:
  - Lorenz curves (before/after)
  - Income distribution histograms
  - Benefit incidence by decile
  - Cost-effectiveness charts
- **Transparency**: Document assumptions and limitations

### User Interface
- **Web Application**: Simple form for policy queries
- **Results Dashboard**: Interactive exploration of results
- **Export**: PDF reports, CSV data downloads

## Example Use Case

**Input**: "How would a $300/month child benefit affect inequality?"

**Processing** (< 2 minutes):
1. Parse: Universal child benefit, $300/month, per child under 18
2. Load: CPS ASEC 2024 data (latest available)
3. Apply: Identify 73M children under 18, calculate $300/month benefit for each household
4. Calculate: New household income = old income + (number_of_children × $3,600/year)
5. Measure: Compare Gini before (0.486) vs after (0.463)

**Output**:
```
Policy Impact Summary
=====================

Policy: $300/month universal child benefit

Inequality Impact:
- Gini coefficient: 0.486 → 0.463 (-4.7%)
- Poverty rate: 11.5% → 8.2% (-3.3 points)
- Bottom 20% income share: 3.1% → 4.2% (+1.1 points)

Cost Analysis:
- Annual cost: $263 billion
- Beneficiaries: 73 million children in 45 million households
- Cost per household: $5,844/year
- Cost per Gini point reduction: $11.5 billion

Distribution:
- Bottom quintile: +$2,400/year avg (+15% income)
- Second quintile: +$3,200/year avg (+8% income)
- Middle quintile: +$3,600/year avg (+5% income)
- Fourth quintile: +$4,000/year avg (+4% income)
- Top quintile: +$4,200/year avg (+1.5% income)

Key Findings:
This policy would significantly reduce income inequality and child poverty.
The benefit is progressive in percentage terms (larger income gain for
lower-income families) while being universal in coverage. Total cost
represents approximately 1% of GDP.
```

## Data Requirements

### CPS ASEC
- **Source**: Census Bureau / IPUMS CPS
- **Coverage**: ~60,000 households, nationally representative
- **Variables Needed**:
  - `HHINCOME`: Total household income
  - `NUMKIDS`: Number of children
  - `AGE`: Age of household members
  - `POVERTY`: Poverty status
  - `HHWEIGHT`: Household sampling weight
  - `STATE`: Geographic location
- **Advantages**: Official source for US poverty/income statistics
- **Limitations**: Smaller sample size

### ACS
- **Source**: Census Bureau / IPUMS USA
- **Coverage**: ~3.5M households (1% sample)
- **Variables**: Similar to CPS ASEC
- **Advantages**: Larger sample, better geographic detail
- **Limitations**: Less detail on income sources

## Evidence Base for Causal Effects

For policies where behavioral responses matter (e.g., labor supply effects of taxes):
- Maintain database of effect sizes from:
  - Randomized controlled trials (RCTs)
  - Quasi-experimental studies
  - Meta-analyses from economics literature
- Apply elasticities to simulate behavioral responses
- Start with mechanical effects only (no behavioral response) for MVP

## Validation Strategy

- **Historical Validation**: Simulate past policies (e.g., 2021 Child Tax Credit expansion) and compare to observed outcomes
- **Benchmark**: Check against existing microsimulation models (Tax Policy Center, TRIM, USCB models)
- **Sensitivity Analysis**: Test robustness to assumptions
- **Expert Review**: Have results reviewed by inequality researchers

## Limitations & Caveats

1. **Static Analysis**: No behavioral responses in initial version (people don't change work/marriage/fertility)
2. **Partial Equilibrium**: No general equilibrium effects (wage changes, price changes)
3. **One-Year Snapshot**: Cross-sectional data, not lifetime inequality
4. **Take-Up**: Assumes 100% benefit take-up (may overstate impact)
5. **Data Lag**: Most recent CPS ASEC is typically 1-2 years old
6. **No Tax Interactions**: Initial version may not model full tax code interactions

## Success Metrics

- **Speed**: Results delivered in < 5 minutes
- **Accuracy**: Inequality measures within 5% of benchmarks for known policies
- **Usability**: Non-technical users can successfully run simulations
- **Coverage**: Handle 80% of common cash transfer and tax policies
- **Transparency**: Users understand assumptions and limitations

## Future Extensions

- Add behavioral responses (labor supply, marriage, fertility)
- Include in-kind benefits (SNAP, Medicaid, housing)
- Model tax code interactions
- Multi-year projections
- State-level analysis
- Integrate with policy cost estimators (CBO, JCT)
- Compare multiple policies side-by-side
- Optimize policies to achieve inequality targets
