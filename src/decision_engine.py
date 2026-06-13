from __future__ import annotations
import json
import anthropic
from src.models import Signal, Decision, Action

SYSTEM_PROMPT = """You are a crypto trading analyst for a prop-firm-style agent on BSC.

Strategy: Spot mean reversion on liquid tokens.
- BUY when: 5%+ price drop AND Fear & Greed < 30 AND no bad news
- SELL when: price bounces back to mean (recovers most of the drop)
- HOLD otherwise

Rules:
- Max 1-2 trades per day
- Conservative — when in doubt, HOLD
- Never chase pumps

Respond with ONLY a JSON object:
{"action": "BUY" | "SELL" | "HOLD", "reason": "short explanation", "confidence": 0.0-1.0}
"""


class DecisionEngine:
    def __init__(self, api_key: str):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)

    async def decide(self, signal: Signal) -> Decision:
        prompt = (
            f"Token: {signal.token}\n"
            f"Current price: ${signal.current_price:.4f}\n"
            f"24h change: {signal.price_change_pct:+.2f}%\n"
            f"Fear & Greed Index: {signal.fear_greed_index}/100\n"
            f"Sentiment: {signal.sentiment}\n\n"
            f"What is your decision?"
        )

        try:
            response = await self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=200,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.content[0].text
            data = json.loads(raw)
            return Decision(
                action=Action(data["action"]),
                token=signal.token,
                reason=data["reason"],
                confidence=data["confidence"],
            )
        except (json.JSONDecodeError, KeyError, ValueError):
            return Decision(
                action=Action.HOLD,
                token=signal.token,
                reason="Failed to parse LLM response — defaulting to HOLD",
                confidence=0.0,
            )
