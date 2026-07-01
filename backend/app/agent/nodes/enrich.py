"""
Node: enrich_company — best-effort company website/LinkedIn lookup via Gemini.
"""

import logging
from app.agent.state import AgentState
from app.services.enrichment import enrich_company_info

logger = logging.getLogger(__name__)


def enrich_company(state: AgentState) -> dict:
    """
    Attempt to find the company's website or LinkedIn page.
    Best-effort — failure here doesn't block the flow.
    """
    contact = state.get("extracted_contact") or {}
    company = contact.get("company", "")

    if not company:
        logger.info("[enrich] No company name — skipping enrichment")
        return {"enriched_website_linkedin": ""}

    logger.info(f"[enrich] Looking up info for: {company}")

    result = enrich_company_info(
        company=company,
        name=contact.get("name", ""),
        designation=contact.get("designation", ""),
    )

    if result:
        logger.info(f"[enrich] Found: {result}")
    else:
        logger.info("[enrich] No enrichment results")

    return {"enriched_website_linkedin": result or ""}
