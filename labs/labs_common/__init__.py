"""Shared helpers for the Agentic Program labs."""

from labs_common.model_config import (
    HAIKU_MODEL_ID,
    SONNET_MODEL_ID,
    HAIKU_LITELLM_ID,
    SONNET_LITELLM_ID,
    HAIKU_STRANDS_ID,
    SONNET_STRANDS_ID,
)
from labs_common.prompt import LabsBasePrompt

__all__ = [
    "HAIKU_MODEL_ID",
    "SONNET_MODEL_ID",
    "HAIKU_LITELLM_ID",
    "SONNET_LITELLM_ID",
    "HAIKU_STRANDS_ID",
    "SONNET_STRANDS_ID",
    "LabsBasePrompt",
]
