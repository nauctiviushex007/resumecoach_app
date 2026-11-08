
"""Optional AI layer. Every function degrades gracefully when no API key is set."""

import requests
from .analysis import WEAK, NUM, new_numbers, analyze


RULES = (
    "Use ONLY facts present in the original text. NEVER add numbers, "
    "tools, employers, titles or achievements that are not in it. "
    "If a metric would help, write [ADD METRIC] as a placeholder "
    "instead of inventing one."
)


class Asker:
    """Calls the LLM API with a per-session call cap."""

    def __init__(
        self,
        api_key="",
        model="claude-sonnet-4-6",
        max_calls=30
    ):
        self.api_key = api_key
        self.model = model
        self.max_calls = max_calls
        self.calls = 0

    @property
    def enabled(self):
        return bool(self.api_key)

    def __call__(self, system, user):
        if not self.enabled or self.calls >= self.max_calls:
            return None

        self.calls += 1

        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                timeout=60,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": self.model,
                    "max_tokens": 800,
                    "system": system,
                    "messages": [
                        {
                            "role": "user",
                            "content": user
                        }
                    ]
                }
            )

            response.raise_for_status()

            return response.json()["content"][0]["text"].strip()

        except Exception:
            return None


def rewrite_bullet(ask, bullet, job, missing):

    out = ask(
        "You improve resume bullets. Start with a strong action verb, "
        "be concise, one line. " + RULES +
        " Reply with the rewritten bullet only.",

        f"Job description:\n{job[:1500]}\n\n"
        f"Skills the job wants (mention one only if the original supports it): "
        f"{', '.join(missing[:8])}\n\n"
        f"Original bullet:\n{bullet}"
    )

    if out is None:

        hint = "Start with an action verb (Built, Led, Reduced…)"

        hint += (
            " and replace the weak opener."
            if any(w in bullet.lower() for w in WEAK)
            else "."
        )

        if not NUM.search(bullet):
            hint += " Add a measurable result (%, time saved, users, size)."

        return {
            "text": None,
            "hint": hint,
            "warn": []
        }

    out = out.strip("-•* \n")

    return {
        "text": out,
        "hint": None,
        "warn": [
            f"'{n}' is not in your original bullet - keep it only if it is true."
            for n in new_numbers(bullet, out)
        ]
    }


def write_cover_letter(ask, resume, job, name, company):

    out = ask(
        "You write concise, honest cover letters (under 250 words). "
        + RULES +
        " Plain text; use [Hiring Manager] if the name is unknown.",

        f"Candidate: {name or '[Your Name]'}\n"
        f"Company: {company or '[Company]'}\n\n"
        f"Resume:\n{resume[:4000]}\n\n"
        f"Job:\n{job[:2500]}"
    )

    if out:
        return out

    skills = (
        ", ".join(analyze(resume, job)["matched"][:5])
        or "the skills in the posting"
    )

    return (
        f"Dear [Hiring Manager],\n\n"
        f"I am writing to apply for the role at {company or '[Company]'}. "
        f"My background includes experience with {skills}, "
        f"which matches several of your requirements.\n\n"
        "[Add 2-3 sentences about your strongest, specific achievement.]\n\n"
        "I would welcome the chance to discuss how I can contribute.\n\n"
        f"Sincerely,\n{name or '[Your Name]'}\n\n"
        "(Template mode - add an API key in secrets for a tailored draft.)"
    )
