import json

from fastapi import APIRouter, HTTPException

from .groq_client import chat_json
from .schemas_job_match import (
    JOB_MATCH_SYSTEM_PROMPT,
    JobMatchRequest,
    JobMatchResponse,
)

router = APIRouter(prefix="/api/ai", tags=["AI"])


@router.post("/job-match", response_model=JobMatchResponse)
def job_match(req: JobMatchRequest) -> JobMatchResponse:
    if not req.cv_text.strip():
        raise HTTPException(status_code=400, detail="cv_text is empty")
    if not req.job_description.strip():
        raise HTTPException(status_code=400, detail="job_description is empty")

    raw = chat_json(
        messages=[
            {"role": "system", "content": JOB_MATCH_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"CANDIDATE CV:\n\n{req.cv_text}\n\n"
                    f"JOB DESCRIPTION:\n\n{req.job_description}"
                ),
            },
        ]
    )

    try:
        data = json.loads(raw)
        return JobMatchResponse(**data)
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"AI returned an unexpected format: {exc}",
        ) from exc