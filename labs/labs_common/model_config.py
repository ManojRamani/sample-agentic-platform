"""Canonical Claude model IDs for all lab notebooks.

All IDs are AWS Bedrock **US cross-region (geo) inference profiles** — the
`us.` prefix routes requests across us-east-1 / us-east-2 / us-west-2 for
throughput and resilience. Requires `bedrock:InvokeModel` permission on every
destination Region; see:
https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html

Bump these constants when AWS Bedrock deprecates a model or a newer one is
available — every notebook imports from here, so one edit updates the whole
workshop.
"""

# Verified against Bedrock docs on 2026-05-06.
HAIKU_MODEL_ID: str = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
SONNET_MODEL_ID: str = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

# LiteLLM-style "bedrock/<id>" prefix
HAIKU_LITELLM_ID: str = f"bedrock/{HAIKU_MODEL_ID}"
SONNET_LITELLM_ID: str = f"bedrock/{SONNET_MODEL_ID}"

# Strands / pydantic-ai-style "bedrock:<id>" prefix
HAIKU_STRANDS_ID: str = f"bedrock:{HAIKU_MODEL_ID}"
SONNET_STRANDS_ID: str = f"bedrock:{SONNET_MODEL_ID}"
