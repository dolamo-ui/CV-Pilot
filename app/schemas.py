from typing import Literal, Optional

from pydantic import BaseModel, Field


ActionKey = Literal[
    "improve",
    "professional",
    "grammar",
    "ats",
    "expand",
    "shorten",
]


SYSTEM_PROMPT = """
You are CVPilot, an expert CV and resume writing assistant.

Your job is to help users improve their CVs while keeping their information
truthful and professional.

Rules:

1. Never invent employers.
2. Never invent job titles.
3. Never invent dates.
4. Never invent qualifications.
5. Never invent certifications.
6. Never invent salaries.
7. Never invent achievements.
8. Never invent percentages or statistics.
9. Never invent technologies the user did not mention.
10. Preserve the user's real experience and facts.
11. Improve clarity, grammar, professionalism, and impact.
12. Use strong action verbs where appropriate.
13. Keep responses concise and suitable for a CV.
14. Do not include explanations unless explicitly requested.
15. Do not use markdown fences.
16. Do not wrap the answer in quotation marks.

Return only the improved CV text.
""".strip()


ACTION_PROMPTS: dict[ActionKey, str] = {
    "improve": """
Improve the following CV section.

Make it:
- clearer
- stronger
- more professional
- achievement-oriented

Keep all original facts.

CV SECTION:

{input}
""".strip(),

    "professional": """
Rewrite the following CV section using professional business language.

Use strong action verbs and concise wording.

Do not change or invent facts.

CV SECTION:

{input}
""".strip(),

    "grammar": """
Correct the grammar, spelling, punctuation, and sentence structure
of the following CV section.

Do not change the meaning.

CV SECTION:

{input}
""".strip(),

    "ats": """
Rewrite the following CV section so it is ATS-friendly.

Use:
- standard professional terminology
- relevant keywords already supported by the text
- simple formatting
- concise sentences
- strong action verbs

Do not invent skills or experience.

CV SECTION:

{input}
""".strip(),

    "expand": """
Improve and expand the following CV section.

Add useful detail only when it is supported by the information provided.

You may improve descriptions of:
- responsibilities
- technologies
- processes
- contributions
- outcomes

Do NOT invent:
- percentages
- statistics
- team sizes
- dates
- employers
- job titles
- achievements
- qualifications

CV SECTION:

{input}
""".strip(),

    "shorten": """
Shorten the following CV section.

Keep only the most important information.

Make it concise, professional, and high-impact.

Do not remove important facts.

CV SECTION:

{input}
""".strip(),
}


class AssistRequest(BaseModel):
    input: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="The user's CV text or question.",
    )

    context: str = Field(
        default="",
        max_length=30000,
        description="Optional CV context.",
    )

    action: Optional[ActionKey] = Field(
        default=None,
        description="Optional CV improvement action.",
    )


class AssistResponse(BaseModel):
    result: str