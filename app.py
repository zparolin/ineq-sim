#!/usr/bin/env python3
"""
Policy Inequality Simulator - Web Application
FastAPI backend for the inequality simulator
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import os

# Import simulation components
from proof_of_concept import (
    generate_simulated_households,
    PolicySimulator,
    PolicyParameters,
    parse_policy_simple,
    format_currency
)
from llm_policy_parser import parse_policy_with_llm

# Initialize FastAPI app
app = FastAPI(
    title="Policy Inequality Simulator",
    description="Analyze how policy interventions affect income inequality",
    version="0.1.0"
)

# Global cache for household data (load once, reuse)
_households_cache = None


def get_households():
    """Get or generate household data (cached)."""
    global _households_cache
    if _households_cache is None:
        print("Generating household data (this may take a moment)...")
        _households_cache = generate_simulated_households(n_households=50000, seed=42)
        print(f"✓ Loaded {len(_households_cache):,} households")
    return _households_cache


# =============================================================================
# API Models
# =============================================================================

class PolicyQuery(BaseModel):
    """Request model for policy simulation."""
    policy_description: str
    use_llm: Optional[bool] = False  # Future: use LLM for parsing


class SimulationResponse(BaseModel):
    """Response model for simulation results."""
    success: bool
    policy: Dict[str, Any]
    inequality: Dict[str, float]
    costs: Dict[str, float]
    distribution: Dict[str, Dict[str, float]]
    summary: str
    error: Optional[str] = None


# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/")
async def root():
    """Serve the main application page."""
    return FileResponse("static/index.html")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


@app.post("/api/simulate", response_model=SimulationResponse)
async def simulate_policy(query: PolicyQuery):
    """
    Simulate a policy intervention and return inequality impacts.

    Args:
        query: PolicyQuery with policy_description

    Returns:
        SimulationResponse with inequality metrics, costs, and distribution
    """
    try:
        # Load household data
        households = get_households()

        # Parse policy from description
        if query.use_llm:
            # Use LLM (Claude API) for parsing
            try:
                policy = parse_policy_with_llm(query.policy_description)
            except Exception as llm_error:
                # Fallback to simple parser if LLM fails
                print(f"LLM parsing failed, using simple parser: {llm_error}")
                policy = parse_policy_simple(query.policy_description)
        else:
            policy = parse_policy_simple(query.policy_description)

        # Create simulator and run
        simulator = PolicySimulator(households)
        results = simulator.calculate_effects(policy)

        # Generate summary text
        summary = generate_summary(results)

        # Return results
        return SimulationResponse(
            success=True,
            policy=results['policy'],
            inequality=results['inequality'],
            costs=results['costs'],
            distribution=results['distribution'],
            summary=summary,
            error=None
        )

    except Exception as e:
        # Return error response
        return SimulationResponse(
            success=False,
            policy={},
            inequality={},
            costs={},
            distribution={},
            summary="",
            error=str(e)
        )


@app.get("/api/examples")
async def get_examples():
    """Get example policy queries."""
    return {
        "examples": [
            {
                "title": "Child Benefit",
                "description": "How would a $300/month child benefit affect inequality?",
                "category": "Family Support"
            },
            {
                "title": "Universal Basic Income",
                "description": "What if we gave $1000/month universal basic income to all adults?",
                "category": "Cash Transfer"
            },
            {
                "title": "Income-Tested Benefit",
                "description": "Impact of $5000/year income-tested benefit with $50000 threshold",
                "category": "Targeted Transfer"
            },
            {
                "title": "Larger Child Benefit",
                "description": "$500/month per child benefit",
                "category": "Family Support"
            },
            {
                "title": "Smaller UBI",
                "description": "$500/month universal basic income per adult",
                "category": "Cash Transfer"
            }
        ]
    }


# =============================================================================
# Helper Functions
# =============================================================================

def generate_summary(results: Dict) -> str:
    """Generate plain-language summary of results."""
    policy = results['policy']
    ineq = results['inequality']
    costs = results['costs']
    dist = results['distribution']

    # Format policy description
    policy_desc = f"{format_currency(policy['amount'])}/{policy['frequency']} per {policy['per']}"

    # Direction of inequality change
    if ineq['gini_change'] < 0:
        gini_direction = "reduce"
        gini_verb = "falls"
    else:
        gini_direction = "increase"
        gini_verb = "rises"

    # Poverty change
    if ineq['poverty_change'] < 0:
        poverty_verb = "fall"
    else:
        poverty_verb = "rise"

    # Progressivity
    if 'Q1' in dist and 'Q5' in dist:
        bottom_pct = dist['Q1']['pct_income_change']
        top_pct = dist['Q5']['pct_income_change']

        if bottom_pct > top_pct:
            progressivity = "progressive (benefits lower-income households more)"
        else:
            progressivity = "regressive (benefits higher-income households more)"
    else:
        progressivity = "neutral"

    # Generate summary
    summary = f"""This {policy_desc} policy would {gini_direction} income inequality by {abs(ineq['gini_pct_change']):.1f}%. """
    summary += f"""The Gini coefficient {gini_verb} from {ineq['gini_before']:.3f} to {ineq['gini_after']:.3f}. """
    summary += f"""Poverty rates would {poverty_verb} by {abs(ineq['poverty_change']):.1f} percentage points, """
    summary += f"""from {ineq['poverty_rate_before']:.1f}% to {ineq['poverty_rate_after']:.1f}%. """
    summary += f"""The policy is {progressivity}. """
    summary += f"""Total annual cost would be {format_currency(costs['total_annual_cost'])}, """
    summary += f"""benefiting {costs['n_beneficiaries']:,.0f} individuals or households. """

    return summary


# =============================================================================
# Startup
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Pre-load household data on startup."""
    print("="*80)
    print("Policy Inequality Simulator - Starting...")
    print("="*80)
    get_households()  # Pre-load data
    print("✓ Server ready!")
    print("="*80)


# Mount static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    # Create static directory if it doesn't exist
    os.makedirs("static", exist_ok=True)

    print("\n" + "="*80)
    print("Starting Policy Inequality Simulator Web Application")
    print("="*80)
    print("\nServer will start at: http://localhost:8000")
    print("API documentation: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server")
    print("="*80 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
