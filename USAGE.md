# Usage Guide

## Getting Started

### 1. Installation

```bash
# Clone the repository (if not already done)
cd ineq-sim

# Install dependencies
pip install -r requirements.txt
```

### 2. Start the Web Server

```bash
python app.py
```

You should see:
```
================================================================================
Policy Inequality Simulator - Starting...
================================================================================
Generating household data (this may take a moment)...
✓ Loaded 50,000 households
✓ Server ready!
================================================================================
```

### 3. Open in Browser

Navigate to: **http://localhost:8000**

## Using the Web Interface

### Basic Usage (No API Key Required)

1. **Enter a policy description** in the text area:
   - "How would a $300/month child benefit affect inequality?"
   - "$1000/month universal basic income to all adults"
   - "$5000/year benefit for households earning under $50000"

2. **Click "Simulate Policy"**

3. **View results** (appears in ~2-5 seconds):
   - Summary of policy impact
   - Gini coefficient and poverty rate changes
   - Total cost and beneficiaries
   - Distribution of benefits by income quintile
   - Bar chart visualization

### Advanced: AI-Powered Parsing

For more flexible natural language understanding:

1. **Get an Anthropic API key**: https://console.anthropic.com/

2. **Set environment variable**:
   ```bash
   export ANTHROPIC_API_KEY='sk-ant-...'
   ```

3. **Restart the server**:
   ```bash
   python app.py
   ```

4. **Check the box**: "Use AI-powered parsing" in the web interface

5. **Try more complex queries**:
   - "Give each family $400 monthly for every kid under 18"
   - "Provide working households earning under $75k with $5000 annual support"
   - "Universal income of $500 per month to everyone over 18"

## Example Policies

Click any example chip to auto-fill the input:

- **Child Benefit**: $300/month per child
- **Universal Basic Income**: $1000/month per adult
- **Income-Tested Benefit**: $5000/year with threshold
- **Smaller UBI**: $500/month per adult
- **Larger Child Benefit**: $500/month per child

## Understanding the Results

### Inequality Metrics

**Gini Coefficient** (0-1 scale)
- 0 = Perfect equality (everyone has same income)
- 1 = Perfect inequality (one person has everything)
- US baseline: ~0.47
- Lower is better

**Poverty Rate** (%)
- Percentage of households below poverty threshold
- US baseline: ~18% (simulated data)
- Threshold adjusted for household size

### Cost Analysis

- **Total Annual Cost**: Total program cost per year
- **Beneficiaries**: Number of households/individuals receiving benefits
- **Avg Benefit**: Average benefit per beneficiary
- **Cost per Gini Point**: Efficiency metric (lower is more cost-effective)

### Distributional Effects

Shows impact on each income quintile:
- **Bottom 20%**: Lowest income households
- **Second 20%**: Lower-middle income
- **Middle 20%**: Middle income
- **Fourth 20%**: Upper-middle income
- **Top 20%**: Highest income households

**Progressive Policy**: Benefits lower-income households more (in % terms)
**Regressive Policy**: Benefits higher-income households more (in % terms)

## API Usage

### REST API

The simulator provides a REST API for programmatic access.

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Simulate Policy:**
```bash
curl -X POST http://localhost:8000/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "policy_description": "How would a $300/month child benefit affect inequality?",
    "use_llm": false
  }'
```

**Get Examples:**
```bash
curl http://localhost:8000/api/examples
```

### API Documentation

Interactive API docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Command Line Usage

For quick tests without the web interface:

```bash
python proof_of_concept.py
```

This runs three pre-defined simulations and prints results to console.

## Python API

Use the simulator programmatically:

```python
from proof_of_concept import (
    generate_simulated_households,
    PolicySimulator,
    PolicyParameters
)

# Load data
households = generate_simulated_households(n_households=50000)

# Define policy
policy = PolicyParameters(
    name="Child Benefit",
    policy_type="universal_benefit",
    amount=300,
    per="child",
    frequency="monthly"
)

# Run simulation
simulator = PolicySimulator(households)
results = simulator.calculate_effects(policy)

# Access results
print(f"Gini change: {results['inequality']['gini_change']:.4f}")
print(f"Total cost: ${results['costs']['total_annual_cost']:,.0f}")
```

## Tips

1. **Start with examples**: Click example chips to see how to phrase queries

2. **Be specific**: Include amount, frequency, and recipient type
   - Good: "$300/month per child"
   - Less good: "child benefit"

3. **Try variations**: The parser is flexible
   - "$300 per month per child"
   - "$300/month for each kid"
   - "300 dollars monthly for children"

4. **Use LLM for complex policies**: Enable AI parsing for:
   - Multiple conditions
   - Complex eligibility rules
   - Varied phrasing

5. **Check the summary**: The plain-language summary helps verify the policy was parsed correctly

## Troubleshooting

**Server won't start:**
- Check if port 8000 is in use: `lsof -i :8000`
- Try a different port: Edit `app.py` line with `port=8000`

**Dependencies missing:**
- Run: `pip install -r requirements.txt`

**LLM parsing not working:**
- Verify API key is set: `echo $ANTHROPIC_API_KEY`
- Check for typos in API key
- Fallback to simple parser (uncheck the box)

**Simulation taking too long:**
- First simulation loads data (~3-5 seconds)
- Subsequent simulations are faster (~1-2 seconds)
- Data is cached in memory

**Results seem wrong:**
- Remember: Using **simulated data** for demonstration
- Replace with real CPS ASEC data for actual policy analysis
- Baseline Gini and poverty rates are approximations

## Next Steps

1. **Replace simulated data** with real CPS ASEC microdata from Census Bureau
2. **Add more policy types**: SNAP, Medicaid, housing subsidies
3. **Implement behavioral responses**: Labor supply effects
4. **Add state-level analysis**: Geographic variation
5. **Historical validation**: Test against known policy impacts
6. **Export features**: PDF reports, CSV downloads

## Support

For issues or questions:
- Check the README.md for detailed documentation
- Review PROJECT_VISION.md for background
- See ACTION_PLAN.md for development roadmap

## Example Session

```
Terminal 1:
$ python app.py
[Server starts and loads data]

Browser:
1. Navigate to http://localhost:8000
2. Enter: "$500/month universal basic income per adult"
3. Click "Simulate Policy"
4. Results appear showing:
   - Gini: 0.475 → 0.406 (-14.5%)
   - Poverty: 18.1% → 4.2% (-13.9pp)
   - Cost: $510M annually
   - Progressive: Bottom quintile gains +68%
5. Try another policy immediately (uses cached data, faster)
```

Enjoy analyzing policy impacts! 🎉
