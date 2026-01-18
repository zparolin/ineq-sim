# Action Plan: Policy Inequality Simulator

## Phase 1: MVP Foundation (Weeks 1-4)

### Week 1: Data Infrastructure
- [ ] **Download CPS ASEC microdata**
  - Register for IPUMS CPS access
  - Extract 2024 ASEC data with required variables
  - Convert to Parquet format for fast loading
  - Document data structure and variable definitions

- [ ] **Create data processing pipeline**
  - Script to load and clean CPS ASEC data
  - Calculate sampling weights
  - Generate baseline inequality measures
  - Save processed data for quick access

- [ ] **Validate baseline measures**
  - Compare Gini coefficient to Census Bureau official statistics
  - Verify poverty rates match published figures
  - Check income percentiles against benchmarks

### Week 2: Core Simulation Engine
- [ ] **Build policy application module**
  - Create `PolicySimulator` class
  - Implement universal benefit calculator
  - Add income-tested benefit logic
  - Handle household vs individual benefits

- [ ] **Implement inequality calculators**
  - Gini coefficient function
  - Income percentile ratios
  - Poverty rate calculations
  - Lorenz curve data generation
  - Income share by decile

- [ ] **Create cost estimation module**
  - Count eligible households/individuals
  - Calculate total program cost
  - Compute per-beneficiary costs
  - Generate distributional tables

### Week 3: Policy Parser
- [ ] **Design structured policy representation**
  - Define policy schema (JSON format)
  - Document policy types and parameters
  - Create validation rules

- [ ] **Build LLM-based semantic parser**
  - Create prompts for policy extraction
  - Test with Claude/GPT-4 API
  - Handle common policy types:
    - Universal child benefits
    - Income-tested transfers
    - Tax credits (EITC, CTC)
    - Minimum wage increases
  - Add clarification logic for ambiguous queries

- [ ] **Test parser with examples**
  - "How would a $300/month child benefit affect inequality?"
  - "What if we doubled the EITC?"
  - "Impact of $15 minimum wage on income distribution"

### Week 4: Output Generation & Testing
- [ ] **Build report generator**
  - Create report template (markdown/HTML)
  - LLM-generated plain language summary
  - Format inequality metrics table
  - Generate distributional analysis

- [ ] **Create visualizations**
  - Lorenz curves (matplotlib/plotly)
  - Income distribution histograms
  - Benefit incidence bar charts
  - Before/after comparison plots

- [ ] **End-to-end testing**
  - Test complete pipeline with 5-10 policy scenarios
  - Validate against known policies (e.g., 2021 CTC)
  - Document accuracy and limitations
  - Optimize for speed (target < 2 minutes)

## Phase 2: User Interface (Weeks 5-6)

### Week 5: Backend API
- [ ] **Build REST API**
  - FastAPI or Flask framework
  - Endpoint: POST /simulate_policy
  - Input: Natural language policy description
  - Output: JSON with results and visualizations

- [ ] **Add caching layer**
  - Cache common queries (Redis)
  - Store past simulations
  - Enable quick retrieval of similar policies

### Week 6: Frontend Application
- [ ] **Build web interface**
  - Simple form for policy input
  - Submit button to run simulation
  - Loading indicator (simulation in progress)

- [ ] **Create results dashboard**
  - Display inequality metrics
  - Show visualizations
  - Present cost analysis
  - Plain language summary

- [ ] **Add export functionality**
  - Download PDF report
  - Export data as CSV
  - Share link to results

## Phase 3: Enhancement & Validation (Weeks 7-8)

### Week 7: Expand Policy Coverage
- [ ] **Add more policy types**
  - Earned Income Tax Credit modifications
  - Child Tax Credit changes
  - SNAP benefit adjustments
  - Housing subsidies
  - Student loan forgiveness

- [ ] **Implement eligibility rules**
  - Income thresholds and phase-outs
  - Age restrictions
  - Employment requirements
  - Family structure criteria

- [ ] **Add behavioral responses (optional)**
  - Labor supply elasticities
  - Simple literature-based adjustments
  - Document assumptions clearly

### Week 8: Validation & Documentation
- [ ] **Historical validation**
  - Simulate 2021 Child Tax Credit expansion
  - Compare to observed inequality changes
  - Calculate prediction accuracy

- [ ] **Benchmark against existing models**
  - Compare to Tax Policy Center estimates
  - Check against academic microsimulation results
  - Document discrepancies and reasons

- [ ] **Create documentation**
  - User guide (how to use the tool)
  - Technical documentation (methodology)
  - Limitations and caveats
  - Example use cases
  - API documentation

## Phase 4: Deployment & Iteration (Weeks 9-10)

### Week 9: Deployment
- [ ] **Set up production environment**
  - Cloud hosting (AWS/Azure/GCP or local server)
  - Containerization (Docker)
  - Environment configuration

- [ ] **Security & privacy**
  - Ensure no PII exposure
  - Rate limiting on API
  - Authentication if needed

- [ ] **Monitoring**
  - Log all queries and results
  - Track performance metrics
  - Error monitoring and alerts

### Week 10: User Testing & Iteration
- [ ] **Conduct user testing**
  - Recruit 3-5 policy researchers or practitioners
  - Observe them using the tool
  - Collect feedback on usability

- [ ] **Iterate based on feedback**
  - Fix bugs and usability issues
  - Improve report clarity
  - Add requested features

- [ ] **Create example gallery**
  - Run 20-30 common policy scenarios
  - Publish results as reference library
  - Enable comparison across policies

## Technical Stack

### Data & Analytics
- **Python 3.10+**: Core language
- **pandas**: Data manipulation
- **numpy**: Numerical computing
- **pyarrow**: Parquet file handling
- **scipy/scikit-learn**: Statistical calculations

### Simulation & Modeling
- **Custom microsimulation engine**: Apply policies to microdata
- **Tax calculation library**: Consider using `taxcalc` or build custom

### AI/ML
- **LLM API**: OpenAI GPT-4 or Anthropic Claude
- **Prompt engineering**: For semantic parsing and report generation

### Visualization
- **matplotlib/seaborn**: Static charts
- **plotly**: Interactive visualizations
- **Alternative**: Observable Plot, D3.js

### Backend
- **FastAPI**: REST API framework
- **Redis**: Caching layer
- **PostgreSQL** (optional): Store simulation history

### Frontend
- **React** or **Svelte**: Web framework
- **Tailwind CSS**: Styling
- **Chart.js** or **Recharts**: Client-side charting

### Deployment
- **Docker**: Containerization
- **Nginx**: Reverse proxy
- **Cloud platform**: AWS/GCP/Azure or self-hosted

## Immediate Next Steps

1. **Set up development environment**
   - Create Python virtual environment
   - Install core dependencies
   - Set up git repository structure

2. **Obtain data access**
   - Register for IPUMS CPS
   - Download 2024 ASEC data
   - Familiarize with data structure

3. **Build minimal prototype**
   - Load CPS ASEC data
   - Implement one simple policy (universal child benefit)
   - Calculate before/after Gini coefficient
   - Print results to console

4. **Validate prototype**
   - Compare baseline Gini to official statistics
   - Test policy application logic
   - Verify results are sensible

## Success Criteria for MVP

- [ ] Can simulate 5+ common policy types
- [ ] Returns results in < 3 minutes
- [ ] Baseline inequality measures match Census Bureau within 2%
- [ ] Historical validation (2021 CTC) within 10% of observed effects
- [ ] Plain language reports are clear and accurate
- [ ] Web interface is functional and user-friendly
- [ ] Documentation covers methodology and limitations

## Resources Needed

- **Data**: Free (IPUMS CPS registration)
- **Compute**: Laptop/desktop sufficient for MVP
- **LLM API**: ~$50-200/month depending on usage
- **Hosting**: $20-100/month for basic cloud hosting
- **Time**: ~100-120 hours over 10 weeks

## Risk Mitigation

- **Data access delays**: Start IPUMS registration immediately
- **LLM costs**: Use caching aggressively, consider open-source models
- **Accuracy concerns**: Focus on transparency and documenting limitations
- **Complexity creep**: Stick to MVP scope, defer advanced features
- **Performance**: Profile code early, optimize data loading
