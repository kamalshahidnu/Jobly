"""Offer evaluation agent for analyzing job offers."""

from typing import Any, Dict
from .base import BaseAgent


class OfferEvalAgent(BaseAgent):
    """Agent responsible for evaluating job offers."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="OfferEvalAgent", config=config)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate and compare job offers.

        Args:
            input_data: Offer details and user preferences

        Returns:
            Offer analysis and recommendations
        """
        preferences = input_data.get("preferences", {}) if isinstance(input_data, dict) else {}
        raw_offers = input_data.get("offers") if isinstance(input_data, dict) else input_data
        offers = raw_offers if isinstance(raw_offers, list) else [raw_offers]

        def _to_number(value: Any) -> float:
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                cleaned = value.replace(",", "").replace("$", "").strip()
                try:
                    return float(cleaned)
                except ValueError:
                    return 0.0
            return 0.0

        def _score_comp(offer: Dict[str, Any]) -> float:
            base = _to_number(offer.get("base_salary") or offer.get("base"))
            bonus = _to_number(offer.get("bonus") or offer.get("annual_bonus"))
            equity = _to_number(offer.get("equity_value") or offer.get("equity"))
            total = base + bonus + equity

            target = _to_number(preferences.get("target_total_comp")) or _to_number(
                preferences.get("min_total_comp")
            )
            baseline = target or 150000.0  # Simple fallback so scoring remains stable
            return min(70.0, (total / max(baseline, 1.0)) * 70.0)

        def _score_location(offer: Dict[str, Any]) -> float:
            pref_location = str(preferences.get("location") or "").lower()
            remote_pref = str(preferences.get("remote_preference") or "").lower()
            offer_location = str(offer.get("location") or "").lower()

            if "remote" in offer_location:
                return 15.0 if remote_pref in {"remote", "either", "hybrid", ""} else 10.0
            if pref_location and pref_location == offer_location:
                return 12.0
            return 6.0 if not pref_location else 0.0

        def _score_benefits(offer: Dict[str, Any]) -> float:
            benefits = offer.get("benefits") or {}
            pto_days = _to_number(offer.get("pto_days") or benefits.get("pto_days"))
            retirement = benefits.get("retirement_match") or offer.get("retirement_match")
            healthcare = benefits.get("healthcare") or offer.get("healthcare")
            stipend = benefits.get("learning") or offer.get("learning_stipend")

            score = 0.0
            score += 4.0 if retirement else 0.0
            score += 4.0 if healthcare else 0.0
            score += 3.0 if stipend else 0.0
            score += min(4.0, pto_days / 5.0)  # Reward reasonable PTO without over-weighting
            return min(score, 15.0)

        def _score_growth(offer: Dict[str, Any]) -> float:
            preferred_stage = str(preferences.get("company_stage") or "").lower()
            stage = str(offer.get("company_stage") or "").lower()
            if preferred_stage and stage == preferred_stage:
                return 10.0
            if stage in {"series a", "series b", "growth"}:
                return 8.0
            if stage:
                return 6.0
            return 4.0

        evaluated_offers = []

        for raw_offer in offers:
            offer = raw_offer if isinstance(raw_offer, dict) else {"offer": raw_offer}

            comp_score = _score_comp(offer)
            location_score = _score_location(offer)
            benefits_score = _score_benefits(offer)
            growth_score = _score_growth(offer)

            total_score = round(min(comp_score + location_score + benefits_score + growth_score, 100.0), 2)
            if total_score >= 75:
                recommendation = "accept"
            elif total_score >= 55:
                recommendation = "consider"
            else:
                recommendation = "decline"

            evaluated_offers.append(
                {
                    **offer,
                    "total_comp": round(
                        _to_number(offer.get("base_salary") or offer.get("base"))
                        + _to_number(offer.get("bonus") or offer.get("annual_bonus"))
                        + _to_number(offer.get("equity_value") or offer.get("equity")),
                        2,
                    ),
                    "score": total_score,
                    "recommendation": recommendation,
                    "component_scores": {
                        "compensation": round(comp_score, 2),
                        "location": round(location_score, 2),
                        "benefits": round(benefits_score, 2),
                        "growth": round(growth_score, 2),
                    },
                }
            )

        evaluated_offers.sort(key=lambda item: item.get("score", 0), reverse=True)
        best_offer = evaluated_offers[0] if evaluated_offers else {}

        return {"status": "success", "evaluation": {"offers": evaluated_offers, "best_offer": best_offer}}
