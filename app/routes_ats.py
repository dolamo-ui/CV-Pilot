import json

from fastapi import APIRouter, HTTPException

from .groq_client import chat_json
from .schemas_ats import ATS_SYSTEM_PROMPT, AtsAnalyzeRequest, AtsAnalyzeResponse

router = APIRouter(prefix="/api/ai", tags=["AI"])


@router.post("/ats-analyze", response_model=AtsAnalyzeResponse)
def ats_analyze(req: AtsAnalyzeRequest) -> AtsAnalyzeResponse:
    if not req.cv_text.strip():
        raise HTTPException(status_code=400, detail="cv_text is empty")

    raw = chat_json(
        messages=[
            {"role": "system", "content": ATS_SYSTEM_PROMPT},
            {"role": "user", "content": f"Analyze this CV:\n\n{req.cv_text}"},
        ]
    )

    try:
        data = json.loads(raw)
        return AtsAnalyzeResponse(**data)
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"AI returned an unexpected format: {exc}",
        ) from exc