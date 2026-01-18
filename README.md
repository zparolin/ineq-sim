# Policy Inequality Simulator

A tool that allows policymakers to enter plain text policy descriptions and receive comprehensive inequality impact analysis in minutes.

## Overview

This project provides a microsimulation framework for analyzing how policy interventions (child benefits, universal basic income, tax credits, etc.) affect income inequality in the United States.

**Key Features:**
- Natural language policy input
- Microsimulation on household data (simulated or CPS ASEC)
- Comprehensive inequality metrics (Gini, poverty rates, income shares)
- Distributional analysis by income quintile
- Cost estimation and cost-effectiveness analysis
- Plain-language reports

## Quick Start - Proof of Concept

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run proof of concept
python proof_of_concept.py
```

### Example Output

```
POLICY: Child Benefit ($300/month per child)

Gini Coefficient:
  Before:  0.4747
  After:   0.4510
  Change:  -0.0237 (-5.0%)

Poverty Rate:
  Before:  18.1%
  After:   12.6%
  Change:  -5.5 percentage points

Total Annual Cost: $208.12M
```

## What's Included

### 1. Proof of Concept (`proof_of_concept.py`)

A complete, self-contained demonstration that:
- Generates realistic simulated household data (50,000 households)
- Applies policy interventions to household incomes
- Calculates inequality measures (Gini, poverty, income shares)
- Estimates total costs and distributional effects
- Generates plain-language reports

**Included Policy Simulations:**
1. **Child Benefit**: $300/month per child
2. **Universal Basic Income**: $1,000/month per adult
3. **Income-Tested Transfer**: $5,000/year with income threshold

**Key Components:**
- `generate_simulated_households()` - Creates realistic household data
- `PolicySimulator` - Applies policies to households
- `calculate_gini()`, `calculate_poverty_rate()` - Inequality metrics
- `parse_policy_simple()` - Extracts policy parameters from text
- `generate_report()` - Creates formatted output

### 2. Project Documentation

- **PROJECT_VISION.md** - Detailed vision for the simplified US-focused simulator
- **ACTION_PLAN.md** - 10-week implementation plan with technical details
- **README.md** - This file

## How It Works

### 1. Data Layer
The proof of concept generates simulated household data with:
- Log-normal income distribution (mimics US inequality)
- Household composition (adults and children)
- Employment status
- Geographic location (state)
- Sampling weights

**Real Implementation**: Will use CPS ASEC or ACS microdata from Census Bureau.

### 2. Policy Simulator
Takes a policy specification and applies it to every household:
```python
policy = PolicyParameters(
    name="Child Benefit",
    policy_type="universal_benefit",
    amount=300,
    per="child",
    frequency="monthly"
)
```

### 3. Inequality Metrics

**Gini Coefficient**: Standard measure of income inequality (0 = perfect equality, 1 = perfect inequality)

**Poverty Rate**: Percentage of households below poverty threshold (adjusted for household size)

**Income Shares**: Proportion of total income going to each quintile

**Percentile Ratios**: P90/P10, P90/P50, P50/P10

### 4. Cost Analysis
- Total annual cost of program
- Number of beneficiaries
- Average benefit per beneficiary
- Cost per Gini point reduction

### 5. Distributional Effects
Shows how each income quintile is affected:
- Average income before/after
- Average benefit received
- Percentage income change
- Progressivity analysis

## Next Steps

### Phase 1: Real Data Integration (Weeks 1-2)
- [ ] Register for IPUMS CPS access
- [ ] Download CPS ASEC 2024 microdata
- [ ] Create data processing pipeline
- [ ] Validate baseline inequality measures against Census Bureau statistics

### Phase 2: Enhanced Policy Parser (Week 3)
- [ ] Integrate Claude or GPT-4 API for robust natural language parsing
- [ ] Handle complex policy specifications
- [ ] Add clarification logic for ambiguous queries
- [ ] Support more policy types (EITC, CTC, SNAP, minimum wage)

### Phase 3: Web Interface (Weeks 4-5)
- [ ] Build FastAPI backend
- [ ] Create simple web frontend (React or Svelte)
- [ ] Add interactive visualizations (Lorenz curves, distribution plots)
- [ ] Enable PDF report exports

### Phase 4: Advanced Features (Weeks 6-10)
- [ ] Add behavioral responses (labor supply elasticities)
- [ ] Implement tax code interactions
- [ ] State-level analysis capabilities
- [ ] Historical validation against known policies (e.g., 2021 CTC expansion)
- [ ] Benchmark against Tax Policy Center and other microsimulation models

## Technical Details

### Dependencies
- **Python 3.10+**
- **numpy** - Numerical computing
- **pandas** - Data manipulation

### Simulated Data Structure
Each household has:
- `household_id` - Unique identifier
- `income` - Annual household income
- `n_adults` - Number of adults (1-2)
- `n_children` - Number of children (0-4)
- `employed` - Employment status (0/1)
- `state` - State of residence
- `weight` - Sampling weight (all 1 in simulation)

### Inequality Calculation Methods

**Gini Coefficient Formula:**
```
Gini = 2 * Σ(cumulative_weight * income * weight) / (total_weight * total_income)
       - (total_weight + 1) / total_weight
```

**Poverty Threshold:**
- Base: $27,750 for family of 4 (2024 threshold)
- Adjusted for household size using equivalence scale: `base * (size/4)^0.7`

### Policy Types Supported

1. **Universal Benefit** - Everyone gets benefit (e.g., child allowance, UBI)
2. **Income-Tested** - Benefit phases out above income threshold
3. **Wage Subsidy** - Only employed households receive benefit

## Example Usage

### Running Custom Simulations

```python
from proof_of_concept import *

# Generate household data
households = generate_simulated_households(n_households=50000)

# Create simulator
simulator = PolicySimulator(households)

# Define custom policy
policy = PolicyParameters(
    name="Expanded EITC",
    policy_type="income_tested",
    amount=6000,
    per="household",
    frequency="annual",
    income_threshold=50000,
    phase_out_rate=0.15
)

# Run simulation
results = simulator.calculate_effects(policy)

# Generate report
report = generate_report(results)
print(report)
```

### Adding New Policy Types

To add a new policy type, extend the `PolicySimulator.apply_policy()` method:

```python
elif policy.policy_type == 'minimum_wage':
    # Calculate earnings increase from minimum wage hike
    # Only affects employed households with low wages
    # Implementation here...
```

## Data Sources (Future)

### CPS ASEC (Current Population Survey Annual Social and Economic Supplement)
- **Source**: IPUMS CPS (ipums.org)
- **Coverage**: ~60,000 households annually
- **Best for**: Official US income and poverty statistics
- **Free**: Yes (registration required)

### ACS (American Community Survey)
- **Source**: IPUMS USA (usa.ipums.org)
- **Coverage**: ~3.5 million households (1% sample)
- **Best for**: Geographic detail, larger sample
- **Free**: Yes (registration required)

## Validation Strategy

1. **Baseline Validation**: Verify Gini and poverty rates match Census Bureau
2. **Historical Validation**: Simulate 2021 Child Tax Credit expansion and compare to observed effects
3. **Benchmarking**: Compare results to Tax Policy Center, TRIM, and academic microsimulation models
4. **Sensitivity Analysis**: Test robustness to assumptions

## Limitations

Current implementation:
- **Static analysis**: No behavioral responses (labor supply, marriage, fertility)
- **Partial equilibrium**: No wage or price changes
- **Take-up**: Assumes 100% benefit take-up
- **Cross-sectional**: One-year snapshot, not lifetime inequality
- **Simplified tax code**: Does not model full tax interactions
- **Simulated data**: Proof of concept uses synthetic data

Future versions will address these limitations.

## Contributing

This is a research project. Contributions welcome:
- Better policy parsing algorithms
- Additional inequality metrics
- Improved visualizations
- Behavioral response models
- Validation against real-world policy changes

## References

### Data
- IPUMS CPS: https://cps.ipums.org
- IPUMS USA: https://usa.ipums.org
- Census Bureau Income and Poverty: https://www.census.gov/topics/income-poverty.html

### Microsimulation Models
- Tax Policy Center Microsimulation Model
- TRIM (Transfer Income Model)
- TAXSIM from NBER

### Research
- Piketty, T. & Saez, E. (2003). "Income Inequality in the United States"
- Chetty, R. et al. (2014). "Where is the Land of Opportunity?"
- Parolin, Z. et al. (2021). "Monthly Poverty Rates in the United States during the COVID-19 Pandemic"

## License

MIT License - See LICENSE file for details

## Contact

For questions or feedback, please open an issue on GitHub.
