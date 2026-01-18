"""
LLM-based Policy Parser
Uses Claude API to extract structured policy parameters from natural language
"""

import os
import json
from typing import Optional
from anthropic import Anthropic
from proof_of_concept import PolicyParameters


# System prompt for policy parsing
POLICY_PARSER_PROMPT = """You are an expert policy analyst. Your job is to extract structured policy parameters from natural language descriptions.

Given a policy description, extract the following information:

1. **name**: A short descriptive name for the policy (e.g., "Child Benefit", "Universal Basic Income")
2. **policy_type**: One of: "universal_benefit", "income_tested", "tax_credit", "wage_subsidy"
3. **amount**: The dollar amount (numeric only, e.g., 300 for $300)
4. **per**: Who receives the benefit: "child", "adult", "household"
5. **frequency**: "monthly" or "annual"
6. **income_threshold**: (Optional) Income threshold for income-tested benefits (numeric)
7. **phase_out_rate**: (Optional) Phase-out rate as decimal (e.g., 0.1 for 10%)

Return ONLY a valid JSON object with these fields. Do not include any explanatory text.

Examples:

Input: "How would a $300/month child benefit affect inequality?"
Output: {
  "name": "Child Benefit",
  "policy_type": "universal_benefit",
  "amount": 300,
  "per": "child",
  "frequency": "monthly",
  "income_threshold": null,
  "phase_out_rate": null
}

Input: "What if we gave $1000/month universal basic income to all adults?"
Output: {
  "name": "Universal Basic Income",
  "policy_type": "universal_benefit",
  "amount": 1000,
  "per": "adult",
  "frequency": "monthly",
  "income_threshold": null,
  "phase_out_rate": null
}

Input: "Impact of $5000/year income-tested benefit with $50000 threshold"
Output: {
  "name": "Income-Tested Transfer",
  "policy_type": "income_tested",
  "amount": 5000,
  "per": "household",
  "frequency": "annual",
  "income_threshold": 50000,
  "phase_out_rate": 0.1
}

Input: "Expand EITC by giving $6000/year to working households earning under $60000"
Output: {
  "name": "EITC Expansion",
  "policy_type": "income_tested",
  "amount": 6000,
  "per": "household",
  "frequency": "annual",
  "income_threshold": 60000,
  "phase_out_rate": 0.15
}

Now parse the following policy description:"""


class LLMPolicyParser:
    """Parse policy descriptions using Claude API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM parser.

        Args:
            api_key: Anthropic API key (if None, reads from ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError(
                "Anthropic API key not found. "
                "Set ANTHROPIC_API_KEY environment variable or pass api_key parameter."
            )

        self.client = Anthropic(api_key=self.api_key)

    def parse(self, policy_description: str) -> PolicyParameters:
        """
        Parse a natural language policy description into structured parameters.

        Args:
            policy_description: Natural language description of the policy

        Returns:
            PolicyParameters object

        Raises:
            ValueError: If parsing fails or API returns invalid response
        """
        try:
            # Call Claude API
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                temperature=0,
                messages=[
                    {
                        "role": "user",
                        "content": f"{POLICY_PARSER_PROMPT}\n\n{policy_description}"
                    }
                ]
            )

            # Extract JSON from response
            response_text = message.content[0].text.strip()

            # Try to parse JSON
            # Sometimes Claude wraps JSON in markdown code blocks
            if response_text.startswith('```'):
                # Extract JSON from code block
                lines = response_text.split('\n')
                json_lines = [l for l in lines if not l.startswith('```')]
                response_text = '\n'.join(json_lines).strip()

            policy_dict = json.loads(response_text)

            # Validate required fields
            required_fields = ['name', 'policy_type', 'amount', 'per', 'frequency']
            for field in required_fields:
                if field not in policy_dict:
                    raise ValueError(f"Missing required field: {field}")

            # Create PolicyParameters object
            policy = PolicyParameters(
                name=policy_dict['name'],
                policy_type=policy_dict['policy_type'],
                amount=float(policy_dict['amount']),
                per=policy_dict['per'],
                frequency=policy_dict['frequency'],
                income_threshold=float(policy_dict['income_threshold'])
                    if policy_dict.get('income_threshold') else None,
                phase_out_rate=float(policy_dict['phase_out_rate'])
                    if policy_dict.get('phase_out_rate') else None
            )

            return policy

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse Claude response as JSON: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing policy with Claude: {e}")


def parse_policy_with_llm(policy_description: str, api_key: Optional[str] = None) -> PolicyParameters:
    """
    Convenience function to parse policy using LLM.

    Args:
        policy_description: Natural language description
        api_key: Optional Anthropic API key

    Returns:
        PolicyParameters object
    """
    parser = LLMPolicyParser(api_key=api_key)
    return parser.parse(policy_description)


# Example usage
if __name__ == "__main__":
    import sys

    # Test the parser
    test_descriptions = [
        "How would a $300/month child benefit affect inequality?",
        "What if we gave $1000/month universal basic income to all adults?",
        "Impact of $5000/year income-tested benefit with $50000 threshold",
        "Give $400 per month to each child in families earning under $75000"
    ]

    print("Testing LLM Policy Parser")
    print("=" * 80)

    # Check for API key
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("\nError: ANTHROPIC_API_KEY environment variable not set")
        print("Set it with: export ANTHROPIC_API_KEY='your-api-key'")
        sys.exit(1)

    parser = LLMPolicyParser()

    for i, description in enumerate(test_descriptions, 1):
        print(f"\nTest {i}: {description}")
        print("-" * 80)

        try:
            policy = parser.parse(description)
            print(f"✓ Parsed successfully:")
            print(f"  Name: {policy.name}")
            print(f"  Type: {policy.policy_type}")
            print(f"  Amount: ${policy.amount:,.0f}/{policy.frequency}")
            print(f"  Per: {policy.per}")
            if policy.income_threshold:
                print(f"  Income threshold: ${policy.income_threshold:,.0f}")
            if policy.phase_out_rate:
                print(f"  Phase-out rate: {policy.phase_out_rate:.1%}")
        except Exception as e:
            print(f"✗ Error: {e}")

    print("\n" + "=" * 80)
