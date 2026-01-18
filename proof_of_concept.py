#!/usr/bin/env python3
"""
Policy Inequality Simulator - Proof of Concept

A simplified demonstration using simulated household data that shows:
1. Generating realistic household income distribution
2. Applying policy interventions (e.g., child benefits, tax credits)
3. Calculating inequality measures (Gini, poverty rates, income shares)
4. Estimating costs and distributional effects
5. Natural language policy parsing (with LLM integration ready)

Usage:
    python proof_of_concept.py
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Optional
import json


# =============================================================================
# DATA GENERATION - Simulate CPS ASEC-like household data
# =============================================================================

def generate_simulated_households(n_households: int = 50000, seed: int = 42) -> pd.DataFrame:
    """
    Generate simulated household data resembling CPS ASEC structure.

    Creates realistic income distribution with household characteristics:
    - Income following log-normal distribution (mimics US income inequality)
    - Household size and composition
    - Number of children
    - Employment status
    """
    np.random.seed(seed)

    # Generate household income (log-normal distribution)
    # Parameters calibrated to approximate US income distribution
    # Mean log income: 10.8 (corresponds to ~$49k median)
    # Std log income: 0.9 (creates realistic inequality)
    log_income = np.random.normal(10.8, 0.9, n_households)
    income = np.exp(log_income)

    # Generate household characteristics
    # Number of adults (1-2, weighted toward 2)
    n_adults = np.random.choice([1, 2], size=n_households, p=[0.3, 0.7])

    # Number of children (0-4, weighted toward 0-2)
    n_children = np.random.choice([0, 1, 2, 3, 4], size=n_households,
                                  p=[0.40, 0.25, 0.20, 0.10, 0.05])

    # Employment status (0=unemployed, 1=employed)
    # Higher income correlates with employment
    employment_prob = np.clip(0.3 + (log_income - 10) * 0.1, 0.1, 0.95)
    employed = np.random.binomial(1, employment_prob)

    # State (simplified: just CA, TX, NY, FL, Other)
    states = np.random.choice(['CA', 'TX', 'NY', 'FL', 'Other'],
                             size=n_households,
                             p=[0.12, 0.09, 0.06, 0.06, 0.67])

    # Household weights (all 1 for simplicity, would be sampling weights in real CPS)
    weights = np.ones(n_households)

    df = pd.DataFrame({
        'household_id': range(n_households),
        'income': income,
        'n_adults': n_adults,
        'n_children': n_children,
        'employed': employed,
        'state': states,
        'weight': weights
    })

    return df


# =============================================================================
# INEQUALITY METRICS
# =============================================================================

def calculate_gini(incomes: np.ndarray, weights: Optional[np.ndarray] = None) -> float:
    """
    Calculate Gini coefficient.

    Gini coefficient measures inequality on 0-1 scale:
    - 0: Perfect equality (everyone has same income)
    - 1: Perfect inequality (one person has all income)

    US Gini is typically ~0.48
    """
    # Convert to numpy arrays if needed
    incomes = np.asarray(incomes)
    if weights is None:
        weights = np.ones(len(incomes))
    else:
        weights = np.asarray(weights)

    # Sort by income
    sorted_indices = np.argsort(incomes)
    sorted_incomes = incomes[sorted_indices]
    sorted_weights = weights[sorted_indices]

    # Calculate Gini
    cumulative_weights = np.cumsum(sorted_weights)
    cumulative_income = np.cumsum(sorted_incomes * sorted_weights)

    total_weight = cumulative_weights[-1]
    total_income = cumulative_income[-1]

    # Gini formula
    gini = (2 * np.sum(cumulative_weights * sorted_incomes * sorted_weights) /
            (total_weight * total_income) -
            (total_weight + 1) / total_weight)

    return gini


def calculate_poverty_rate(incomes: np.ndarray,
                          household_sizes: np.ndarray,
                          weights: Optional[np.ndarray] = None,
                          poverty_threshold: float = 27750) -> float:
    """
    Calculate poverty rate using simplified poverty threshold.

    Uses 2024 US poverty threshold for family of 4: $27,750
    (Adjusted proportionally for household size)
    """
    # Convert to numpy arrays if needed
    incomes = np.asarray(incomes)
    household_sizes = np.asarray(household_sizes)
    if weights is None:
        weights = np.ones(len(incomes))
    else:
        weights = np.asarray(weights)

    # Adjust threshold by household size (simplified)
    thresholds = poverty_threshold * (household_sizes / 4) ** 0.7

    # Calculate poverty rate
    in_poverty = incomes < thresholds
    poverty_rate = np.sum(weights[in_poverty]) / np.sum(weights)

    return poverty_rate


def calculate_income_shares(incomes: np.ndarray,
                           weights: Optional[np.ndarray] = None,
                           n_quantiles: int = 5) -> Dict[str, float]:
    """
    Calculate income share by quantile (quintiles by default).

    Returns dict with share of total income going to each quantile.
    """
    # Convert to numpy arrays if needed
    incomes = np.asarray(incomes)
    if weights is None:
        weights = np.ones(len(incomes))
    else:
        weights = np.asarray(weights)

    # Calculate quantiles
    quantile_edges = np.linspace(0, 100, n_quantiles + 1)
    quantile_labels = [f'Q{i+1}' for i in range(n_quantiles)]

    # Assign households to quantiles based on income
    quantiles = pd.qcut(incomes, q=n_quantiles, labels=quantile_labels, duplicates='drop')

    # Calculate income share for each quantile
    shares = {}
    total_income = np.sum(incomes * weights)

    for label in quantile_labels:
        mask = (quantiles == label)
        if mask.sum() > 0:
            share = np.sum(incomes[mask] * weights[mask]) / total_income
            shares[label] = share
        else:
            shares[label] = 0.0

    return shares


def calculate_percentile_ratios(incomes: np.ndarray,
                                weights: Optional[np.ndarray] = None) -> Dict[str, float]:
    """Calculate key percentile ratios (P90/P10, P90/P50, P50/P10)."""
    # Convert to numpy arrays if needed
    incomes = np.asarray(incomes)
    if weights is None:
        weights = np.ones(len(incomes))
    else:
        weights = np.asarray(weights)

    # Calculate weighted percentiles
    p10 = np.percentile(incomes, 10)
    p50 = np.percentile(incomes, 50)
    p90 = np.percentile(incomes, 90)

    return {
        'P90_P10': p90 / p10 if p10 > 0 else np.inf,
        'P90_P50': p90 / p50 if p50 > 0 else np.inf,
        'P50_P10': p50 / p10 if p10 > 0 else np.inf,
        'P10': p10,
        'P50': p50,
        'P90': p90
    }


# =============================================================================
# POLICY SIMULATOR
# =============================================================================

@dataclass
class PolicyParameters:
    """Structured representation of a policy intervention."""
    name: str
    policy_type: str  # 'universal_benefit', 'income_tested', 'tax_credit', 'wage_subsidy'
    amount: float
    per: str  # 'child', 'adult', 'household'
    frequency: str  # 'monthly', 'annual'
    income_threshold: Optional[float] = None  # For income-tested benefits
    phase_out_rate: Optional[float] = None  # How fast benefit phases out above threshold

    def to_annual_amount(self) -> float:
        """Convert to annual amount."""
        if self.frequency == 'monthly':
            return self.amount * 12
        return self.amount


class PolicySimulator:
    """Apply policy interventions to household data and calculate effects."""

    def __init__(self, households: pd.DataFrame):
        self.households = households.copy()
        self.original_income = households['income'].copy()

    def apply_policy(self, policy: PolicyParameters) -> pd.DataFrame:
        """
        Apply policy to households and return modified data.

        Returns new DataFrame with 'new_income' and 'benefit_received' columns.
        """
        df = self.households.copy()
        df['new_income'] = df['income'].copy()
        df['benefit_received'] = 0.0

        annual_amount = policy.to_annual_amount()

        if policy.policy_type == 'universal_benefit':
            # Everyone gets benefit based on household composition
            if policy.per == 'child':
                benefit = df['n_children'] * annual_amount
            elif policy.per == 'household':
                benefit = annual_amount
            elif policy.per == 'adult':
                benefit = df['n_adults'] * annual_amount
            else:
                raise ValueError(f"Unknown 'per' value: {policy.per}")

            df['benefit_received'] = benefit
            df['new_income'] = df['income'] + benefit

        elif policy.policy_type == 'income_tested':
            # Benefit phases out with income
            if policy.per == 'child':
                base_benefit = df['n_children'] * annual_amount
            elif policy.per == 'household':
                base_benefit = annual_amount
            else:
                base_benefit = df['n_adults'] * annual_amount

            # Apply income test with phase-out
            if policy.income_threshold and policy.phase_out_rate:
                excess_income = np.maximum(0, df['income'] - policy.income_threshold)
                reduction = excess_income * policy.phase_out_rate
                benefit = np.maximum(0, base_benefit - reduction)
            elif policy.income_threshold:
                # Simple cutoff (no phase-out)
                benefit = np.where(df['income'] <= policy.income_threshold, base_benefit, 0)
            else:
                benefit = base_benefit

            df['benefit_received'] = benefit
            df['new_income'] = df['income'] + benefit

        elif policy.policy_type == 'wage_subsidy':
            # Only for employed households
            benefit = np.where(df['employed'] == 1, annual_amount, 0)
            df['benefit_received'] = benefit
            df['new_income'] = df['income'] + benefit

        else:
            raise ValueError(f"Unknown policy type: {policy.policy_type}")

        return df

    def calculate_effects(self, policy: PolicyParameters) -> Dict:
        """
        Apply policy and calculate all effects on inequality and costs.

        Returns comprehensive dictionary with inequality metrics, costs, and distribution.
        """
        # Apply policy
        df = self.apply_policy(policy)

        # Calculate baseline metrics
        baseline_gini = calculate_gini(df['income'], df['weight'])
        baseline_poverty = calculate_poverty_rate(
            df['income'],
            df['n_adults'] + df['n_children'],
            df['weight']
        )
        baseline_shares = calculate_income_shares(df['income'], df['weight'])
        baseline_percentiles = calculate_percentile_ratios(df['income'], df['weight'])

        # Calculate post-policy metrics
        new_gini = calculate_gini(df['new_income'], df['weight'])
        new_poverty = calculate_poverty_rate(
            df['new_income'],
            df['n_adults'] + df['n_children'],
            df['weight']
        )
        new_shares = calculate_income_shares(df['new_income'], df['weight'])
        new_percentiles = calculate_percentile_ratios(df['new_income'], df['weight'])

        # Calculate costs
        total_cost = np.sum(df['benefit_received'] * df['weight'])
        n_beneficiaries = np.sum((df['benefit_received'] > 0) * df['weight'])
        avg_benefit = total_cost / n_beneficiaries if n_beneficiaries > 0 else 0

        # Calculate distributional effects by quintile
        df['quintile'] = pd.qcut(df['income'], q=5, labels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'],
                                duplicates='drop')

        distribution_by_quintile = {}
        for q in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']:
            mask = df['quintile'] == q
            if mask.sum() > 0:
                avg_income_before = np.average(df.loc[mask, 'income'], weights=df.loc[mask, 'weight'])
                avg_income_after = np.average(df.loc[mask, 'new_income'], weights=df.loc[mask, 'weight'])
                avg_benefit_q = np.average(df.loc[mask, 'benefit_received'], weights=df.loc[mask, 'weight'])
                pct_change = ((avg_income_after - avg_income_before) / avg_income_before * 100) if avg_income_before > 0 else 0

                distribution_by_quintile[q] = {
                    'avg_income_before': avg_income_before,
                    'avg_income_after': avg_income_after,
                    'avg_benefit': avg_benefit_q,
                    'pct_income_change': pct_change
                }

        # Compile results
        results = {
            'policy': {
                'name': policy.name,
                'type': policy.policy_type,
                'amount': policy.amount,
                'frequency': policy.frequency,
                'per': policy.per
            },
            'inequality': {
                'gini_before': baseline_gini,
                'gini_after': new_gini,
                'gini_change': new_gini - baseline_gini,
                'gini_pct_change': (new_gini - baseline_gini) / baseline_gini * 100,
                'poverty_rate_before': baseline_poverty * 100,
                'poverty_rate_after': new_poverty * 100,
                'poverty_change': (new_poverty - baseline_poverty) * 100
            },
            'income_shares': {
                'before': baseline_shares,
                'after': new_shares
            },
            'percentiles': {
                'before': baseline_percentiles,
                'after': new_percentiles
            },
            'costs': {
                'total_annual_cost': total_cost,
                'n_beneficiaries': n_beneficiaries,
                'avg_benefit_per_beneficiary': avg_benefit,
                'cost_per_gini_point': abs(total_cost / ((new_gini - baseline_gini) * 100)) if new_gini != baseline_gini else np.inf
            },
            'distribution': distribution_by_quintile
        }

        return results


# =============================================================================
# POLICY PARSER (LLM-ready)
# =============================================================================

def parse_policy_simple(description: str) -> PolicyParameters:
    """
    Simple rule-based policy parser (can be replaced with LLM).

    For demo purposes, uses keyword matching.
    In production, would use Claude/GPT-4 to extract structured parameters.
    """
    description = description.lower()

    # Detect policy type
    if 'child benefit' in description or 'child allowance' in description:
        policy_type = 'universal_benefit'
        per = 'child'
        name = 'Child Benefit'
    elif 'eitc' in description or 'earned income' in description:
        policy_type = 'income_tested'
        per = 'household'
        name = 'EITC Expansion'
    elif 'universal basic income' in description or 'ubi' in description:
        policy_type = 'universal_benefit'
        per = 'adult'
        name = 'Universal Basic Income'
    else:
        policy_type = 'universal_benefit'
        per = 'household'
        name = 'Transfer Policy'

    # Extract amount
    import re

    # Look for dollar amounts like "$300" or "300"
    amount_match = re.search(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', description)
    if amount_match:
        amount = float(amount_match.group(1).replace(',', ''))
    else:
        amount = 1000  # Default

    # Detect frequency
    if 'month' in description:
        frequency = 'monthly'
    elif 'year' in description or 'annual' in description:
        frequency = 'annual'
    else:
        frequency = 'monthly'  # Default assumption

    # Detect income testing
    income_threshold = None
    phase_out_rate = None

    if 'income test' in description or 'phase out' in description or 'means test' in description:
        policy_type = 'income_tested'
        # Look for threshold
        threshold_match = re.search(r'threshold\s+\$?(\d+(?:,\d{3})*)', description)
        if threshold_match:
            income_threshold = float(threshold_match.group(1).replace(',', ''))
        else:
            income_threshold = 50000  # Default

        phase_out_rate = 0.1  # 10% default phase-out

    return PolicyParameters(
        name=name,
        policy_type=policy_type,
        amount=amount,
        per=per,
        frequency=frequency,
        income_threshold=income_threshold,
        phase_out_rate=phase_out_rate
    )


# =============================================================================
# OUTPUT GENERATION
# =============================================================================

def format_currency(amount: float) -> str:
    """Format number as currency."""
    if amount >= 1e12:
        return f"${amount/1e12:.2f}T"
    elif amount >= 1e9:
        return f"${amount/1e9:.2f}B"
    elif amount >= 1e6:
        return f"${amount/1e6:.2f}M"
    else:
        return f"${amount:,.0f}"


def generate_report(results: Dict) -> str:
    """Generate plain-language report from simulation results."""

    policy = results['policy']
    ineq = results['inequality']
    costs = results['costs']
    dist = results['distribution']

    report = f"""
{'='*80}
POLICY IMPACT ANALYSIS
{'='*80}

POLICY: {policy['name']}
Description: {format_currency(policy['amount'])}/{policy['frequency']} {policy['per']}

{'='*80}
INEQUALITY IMPACT
{'='*80}

Gini Coefficient:
  Before:  {ineq['gini_before']:.4f}
  After:   {ineq['gini_after']:.4f}
  Change:  {ineq['gini_change']:+.4f} ({ineq['gini_pct_change']:+.1f}%)

Poverty Rate:
  Before:  {ineq['poverty_rate_before']:.1f}%
  After:   {ineq['poverty_rate_after']:.1f}%
  Change:  {ineq['poverty_change']:+.1f} percentage points

{'='*80}
COST ANALYSIS
{'='*80}

Total Annual Cost:        {format_currency(costs['total_annual_cost'])}
Number of Beneficiaries:  {costs['n_beneficiaries']:,.0f}
Average Benefit:          {format_currency(costs['avg_benefit_per_beneficiary'])}
Cost per Gini Point:      {format_currency(costs['cost_per_gini_point'])}

{'='*80}
DISTRIBUTIONAL EFFECTS (by income quintile)
{'='*80}

"""

    for q in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']:
        if q in dist:
            d = dist[q]
            quintile_name = {
                'Q1': 'Bottom 20%',
                'Q2': 'Second 20%',
                'Q3': 'Middle 20%',
                'Q4': 'Fourth 20%',
                'Q5': 'Top 20%'
            }[q]

            report += f"{quintile_name}:\n"
            report += f"  Avg Income Before: {format_currency(d['avg_income_before'])}\n"
            report += f"  Avg Income After:  {format_currency(d['avg_income_after'])}\n"
            report += f"  Avg Benefit:       {format_currency(d['avg_benefit'])}\n"
            report += f"  Income Change:     {d['pct_income_change']:+.1f}%\n\n"

    # Generate interpretation
    report += f"{'='*80}\n"
    report += "KEY FINDINGS\n"
    report += f"{'='*80}\n\n"

    if ineq['gini_change'] < 0:
        report += f"This policy would REDUCE income inequality by {abs(ineq['gini_pct_change']):.1f}%.\n"
    else:
        report += f"This policy would INCREASE income inequality by {ineq['gini_pct_change']:.1f}%.\n"

    if ineq['poverty_change'] < 0:
        report += f"Poverty would fall by {abs(ineq['poverty_change']):.1f} percentage points.\n"
    else:
        report += f"Poverty would rise by {ineq['poverty_change']:.1f} percentage points.\n"

    # Progressivity analysis
    if 'Q1' in dist and 'Q5' in dist:
        bottom_pct = dist['Q1']['pct_income_change']
        top_pct = dist['Q5']['pct_income_change']

        if bottom_pct > top_pct:
            report += f"\nThe policy is PROGRESSIVE (benefits lower-income households more).\n"
            report += f"Bottom quintile gains {bottom_pct:.1f}% vs top quintile {top_pct:.1f}%.\n"
        else:
            report += f"\nThe policy is REGRESSIVE (benefits higher-income households more).\n"
            report += f"Top quintile gains {top_pct:.1f}% vs bottom quintile {bottom_pct:.1f}%.\n"

    report += f"\n{'='*80}\n"

    return report


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Run proof of concept demonstration."""

    print("="*80)
    print("POLICY INEQUALITY SIMULATOR - PROOF OF CONCEPT")
    print("="*80)
    print()

    # Step 1: Generate simulated data
    print("Step 1: Generating simulated household data (n=50,000)...")
    households = generate_simulated_households(n_households=50000)
    print(f"✓ Created {len(households):,} households")
    print(f"  Median income: ${households['income'].median():,.0f}")
    print(f"  Mean income: ${households['income'].mean():,.0f}")
    print(f"  Households with children: {(households['n_children'] > 0).sum():,} ({(households['n_children'] > 0).mean()*100:.1f}%)")
    print()

    # Step 2: Calculate baseline inequality
    print("Step 2: Calculating baseline inequality metrics...")
    baseline_gini = calculate_gini(households['income'], households['weight'])
    baseline_poverty = calculate_poverty_rate(
        households['income'],
        households['n_adults'] + households['n_children'],
        households['weight']
    ) * 100
    print(f"✓ Baseline Gini coefficient: {baseline_gini:.4f}")
    print(f"✓ Baseline poverty rate: {baseline_poverty:.1f}%")
    print()

    # Step 3: Define example policies
    print("Step 3: Testing policy simulations...")
    print()

    policies_to_test = [
        "How would a $300/month child benefit affect inequality?",
        "What if we gave $1000/month universal basic income to all adults?",
        "Impact of $5000/year income-tested benefit with $50000 threshold"
    ]

    simulator = PolicySimulator(households)

    for i, policy_description in enumerate(policies_to_test, 1):
        print(f"\n{'#'*80}")
        print(f"SIMULATION {i}: {policy_description}")
        print(f"{'#'*80}\n")

        # Parse policy
        policy = parse_policy_simple(policy_description)
        print(f"Parsed policy: {policy.name}")
        print(f"  Type: {policy.policy_type}")
        print(f"  Amount: ${policy.amount:,.0f}/{policy.frequency} per {policy.per}")
        if policy.income_threshold:
            print(f"  Income threshold: ${policy.income_threshold:,.0f}")
        print()

        # Run simulation
        print("Running simulation...")
        results = simulator.calculate_effects(policy)

        # Generate and print report
        report = generate_report(results)
        print(report)

        # Add separator
        if i < len(policies_to_test):
            print("\n" + "="*80)
            print("Press Enter to continue to next simulation...")
            # input()  # Uncomment for interactive mode

    print("\n" + "="*80)
    print("PROOF OF CONCEPT COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("  1. Replace simulated data with real CPS ASEC microdata")
    print("  2. Integrate LLM for robust policy parsing")
    print("  3. Add more policy types (EITC, SNAP, tax policies)")
    print("  4. Create web interface for interactive use")
    print("  5. Add visualizations (Lorenz curves, distribution plots)")
    print("  6. Implement behavioral responses (labor supply effects)")
    print()


if __name__ == "__main__":
    main()
