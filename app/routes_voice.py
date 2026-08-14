import json

from fastapi import APIRouter, HTTPException

from .groq_client import chat_json
from .schemas_voice import VOICE_CV_SYSTEM_PROMPT, VoiceCvRequest, VoiceCvResponse

router = APIRouter(prefix="/api/ai", tags=["AI"])


@router.post("/voice-to-cv", response_model=VoiceCvResponse)
def voice_to_cv(req: VoiceCvRequest) -> VoiceCvResponse:
    if not req.transcript.strip():
        raise HTTPException(status_code=400, detail="transcript is empty")

    raw = chat_json(
        messages=[
            {"role": "system", "content": VOICE_CV_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Here is the transcript of what the user said:\n\n{req.transcript}",
            },
        ],
        # Lower temperature: we want faithful extraction, not creative writing.
        temperature=0.3,
        max_tokens=1000,
    )

    try:
        data = json.loads(raw)
        return VoiceCvResponse(**data)
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"AI returned an unexpected format: {exc}",
        ) from exc