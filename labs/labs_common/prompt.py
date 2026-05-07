"""A `BasePrompt` subclass that pins `model_id` to the labs' canonical Haiku ID.

The platform's `agentic_platform.core.models.prompt_models.BasePrompt` defaults
its `model_id` to a Claude 3 Haiku ID that is now marked "legacy" by AWS
Bedrock, causing notebooks to fail with `ResourceNotFoundException: This Model
is marked by provider as Legacy...`

Lab notebooks should import `LabsBasePrompt` from `labs_common` instead of
pulling `BasePrompt` directly from `agentic_platform`. That way the whole
workshop moves in lockstep with `labs_common/model_config.py` when a new
Claude ships — without touching any `src/` code.
"""

from agentic_platform.core.models.prompt_models import BasePrompt

from labs_common.model_config import HAIKU_MODEL_ID


class LabsBasePrompt(BasePrompt):
    """Lab-side `BasePrompt` with `model_id` defaulted to the current Haiku ID."""

    model_id: str = HAIKU_MODEL_ID
