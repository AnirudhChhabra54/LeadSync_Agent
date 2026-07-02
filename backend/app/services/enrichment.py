"""
Company enrichment service — best-effort website/LinkedIn lookup using Gemini LLM.
No additional API keys required beyond the existing Gemini key.
"""

import logging

from google import genai

from app.config import get_settings

logger = logging.getLogger(__name__)


ENRICHMENT_PROMPT = """Given the following company name and optionally a person's name and designation, 
provide the most likely company website URL and/or LinkedIn profile URL.

Company: {company}
Person: {name}
Designation: {designation}

Rules:
- Only provide URLs you are reasonably confident about
- For well-known companies, provide the official website
- For LinkedIn, provide the company page URL if you know it
- Combine into a single string, separated by " | " if both are available
- If you're not confident about either, return just the company name with ".com" appended as a guess
- Return ONLY the URL string(s), nothing else — no explanation, no markdown
"""


def enrich_company_info(
    company: str,
    name: str = "",
    designation: str = "",
) -> str:
    """
    Attempt to find the company's website or LinkedIn page using Gemini.
    This is best-effort — returns whatever the LLM can infer.

    Args:
        company: Company name from the visiting card.
        name: Person's name (optional, for LinkedIn guess).
        designation: Job title (optional context).

    Returns:
        A string with website/LinkedIn URL(s), or empty string if nothing found.
    """
    if not company.strip():
        return ""

    settings = get_settings()

    if not settings.GEMINI_API_KEY:
        logger.info("[STUB] Gemini not configured — returning mock enrichment")
        return f"https://www.{company.lower().replace(' ', '')}.com"

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        prompt = ENRICHMENT_PROMPT.format(
            company=company,
            name=name,
            designation=designation,
        )

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )

        result = response.text.strip()

        # Basic validation — should look like a URL
        if "." in result and len(result) < 500:
            logger.info(f"Enriched company info for '{company}': {result}")
            return result
        else:
            logger.warning(f"Enrichment result didn't look like a URL: {result[:100]}")
            return ""

    except Exception as e:
        logger.error(f"Company enrichment failed: {e}")
        return ""
