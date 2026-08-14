from fastapi import APIRouter, HTTPException

from .groq_client import chat
from .schemas import (
    ACTION_PROMPTS,
    SYSTEM_PROMPT,
    AssistRequest,
    AssistResponse,
)


router = APIRouter(
    prefix="/api/ai",
    tags=["AI"],
)


@router.post(
    "/assist",
    response_model=AssistResponse,
)
def assist(req: AssistRequest) -> AssistResponse:

    # Make sure input isn't empty
    if not req.input.strip():
        raise HTTPException(
            status_code=400,
            detail="Input cannot be empty.",
        )

    # ---------------------------------------------------------
    # QUICK ACTION
    # ---------------------------------------------------------

    if req.action:

        prompt_template = ACTION_PROMPTS.get(req.action)

        if not prompt_template:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported action: {req.action}",
            )

        user_prompt = prompt_template.format(
            input=req.input
        )

    # ---------------------------------------------------------
    # FREE-FORM CV ASSISTANT
    # ---------------------------------------------------------

    else:

        user_prompt = f"""
Here is the user's CV information for context:

{req.context}

User's request:

{req.input}
""".strip()

    # ---------------------------------------------------------
    # CALL GROQ
    # ---------------------------------------------------------

    result = chat(
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0.7,
        max_tokens=800,
    )

    return AssistResponse(
        result=result.strip()
    )