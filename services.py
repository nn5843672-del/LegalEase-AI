import re

import httpx

from .config import settings
from .schemas import DocumentRequest


def _demo_draft(data: DocumentRequest) -> str:
    terms = [line.strip(" -•\t") for line in re.split(r"[;\n]+", data.terms) if line.strip()]
    clauses = "\n".join(f"{index}. {term}" for index, term in enumerate(terms, start=1))
    if not clauses:
        clauses = "1. The parties will perform their respective obligations in good faith."
    return f"""{data.document_type.upper()}

This draft is made on {data.effective_date.isoformat()} and is intended to take effect on that date.

PARTIES
This agreement is between {data.first_party} (the “First Party”) and {data.second_party} (the “Second Party”).

PURPOSE
The parties wish to record the terms of their arrangement in writing. The details below are based only on information supplied by the user.

TERMS AND CONDITIONS
{clauses}

TERM AND CHANGES
This agreement begins on the effective date above. Any change should be recorded in writing and accepted by both parties.

GOVERNING LAW
The parties have selected {data.jurisdiction} as the jurisdiction for this draft. The parties should confirm that the selected law and any required formalities apply to their situation.

SIGNATURES

First Party: {data.first_party}                 Date: ____________________
Signature: ______________________________

Second Party: {data.second_party}               Date: ____________________
Signature: ______________________________

DRAFT FOR REVIEW
This AI-assisted template is for educational and drafting purposes. It is not legal advice and may not be enforceable as written. Have a qualified legal professional review it before signing or relying on it."""


async def generate_document(data: DocumentRequest) -> tuple[str, bool]:
    if not settings.gemini_api_key:
        return _demo_draft(data), True

    prompt = f"""Draft a clear, balanced, editable {data.document_type} in {data.language}.
This is a general drafting aid, not legal advice. Do not invent facts or claim enforceability.
Use plain language, numbered clauses, definitions where needed, and signature blocks.
Flag missing or jurisdiction-dependent provisions as [REVIEW REQUIRED]. Include a short
notice that a qualified lawyer should review the draft before use.

First party: {data.first_party}
Second party: {data.second_party}
Effective date: {data.effective_date.isoformat()}
Jurisdiction: {data.jurisdiction}
User-provided terms: {data.terms}

Return only the document text, with a title and clear section headings."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent"
    try:
        async with httpx.AsyncClient(timeout=75) as client:
            response = await client.post(
                url,
                headers={"x-goog-api-key": settings.gemini_api_key},
                json={"contents": [{"parts": [{"text": prompt}]}],
                      "generationConfig": {"temperature": 0.35, "maxOutputTokens": 6000}},
            )
        response.raise_for_status()
        payload = response.json()
        text = "".join(part.get("text", "") for part in payload["candidates"][0]["content"]["parts"])
        if not text.strip():
            raise ValueError("The AI returned an empty draft.")
        return text.strip(), False
    except httpx.HTTPStatusError as exc:
        detail = "Gemini API rejected the request. Check the API key and model name."
        if exc.response.status_code == 429:
            detail = "Gemini API quota or rate limit reached. Please try again later."
        raise RuntimeError(detail) from exc
    except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
        raise RuntimeError("Could not generate the document. Check your connection and Gemini settings.") from exc
