# 🚀 Agentic Program Labs

Welcome to the Agentic Program Labs! This repository contains a series of hands-on labs designed to teach you how to build agentic applications using Large Language Models (LLMs) through Amazon Bedrock and other AWS services.

## 🏗️ Workshop Structure

The workshop consists of 5 progressive modules that build upon each other:

### Module 1: Prompt Engineering & Evaluation

- Master fundamental prompt engineering techniques
- Work with Bedrock's Converse API
- Learn chain-of-thought reasoning and few-shot examples
- Implement simple RAG systems and function calling
- Evaluate your prompts systematically

### Module 2: Common Agentic Patterns

- Explore various workflow techniques working with LLMs
- Implement parallelization strategies
- Build orchestration patterns
- Create reusable workflows
- Manage agent execution flows

### Module 3: Building Agentic Applications

- Implement an agent from scratch
- Understanding memory
- Understanding and adding tools
- Adding retrieval
- Introducing frameworks and interoperability

### Module 4: Multi-Agent Systems & MCP

- Intro to MCP and build your own MCP Server / Client
- Build systems with multiple cooperating agents
- Implement agent communication protocols
- Create systems that leverage agent specialization

### Module 5: Deployment and Infrastructure

- Observability in agentic systems
- LLM Gateway & how to manage tenancy
- Memory Gateway & and how to manage short / long term memory
- Scale your agent infrastructure

## 📋 Prerequisites

Before starting these labs, you'll need:

- An AWS account with access to Amazon Bedrock
- Python 3.12 (these labs were tested with Python 3.12)
- Basic knowledge of Python programming

## 🏁 Getting Started

### 1. Set up your environment

We recommend using [uv](https://github.com/astral-sh/uv) for managing Python dependencies as it's faster and more reliable.

```bash
# Install uv if you don't have it already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone this repository and navigate to it
git clone <repository-url>
cd agentic-program-technical-assets

# Install dependencies from pyproject.toml
uv sync

# Register the nbstripout git filter so notebook outputs don't get committed
# (one-time per clone — see "Committing notebooks" below for why)
uv run nbstripout --install
```

### 2. Configure AWS Credentials

```bash
# Use AWS CLI
aws configure

# Ensure you have the right permissions for Amazon Bedrock
# You'll need model access enabled for Claude models
```

### 3. Start the Jupyter Lab environment

```bash
# Start Jupyter Lab with uv to ensure all dependencies are available
uv run jupyter lab
```

This will automatically:

- Install all required dependencies
- Make the `agentic_platform` code importable from your lab notebooks
- Start the Jupyter Lab interface

## 📂 Repository Structure

```text
agentic-program-technical-assets/
├── src/
│   └── agentic_platform/  # Core utilities used across labs
│       ├── agent/         # Agent implementations
│       ├── tool/          # Tool utilities
│       ├── service/       # Service integrations
│       └── ...
├── labs/
│   ├── labs_common/      # Shared helpers imported by every notebook
│   │   └── model_config.py   # Canonical Claude model IDs (single source of truth)
│   ├── module1/          # Prompt Engineering & Evaluation
│   ├── module2/          # Common Agentic Patterns
│   ├── module3/          # Building Agentic Applications
│   ├── module4/          # Multi-Agent Systems
│   └── module5/          # Deployment and Infrastructure
├── pyproject.toml        # Project dependencies
└── README.md
```

## 🧩 Model IDs: single source of truth

Every notebook imports its Claude model ID from the shared `labs_common` package
instead of hardcoding the ID string. This way, when AWS Bedrock deprecates a
model (e.g. a Haiku version moves to "legacy"), the whole workshop is bumped by
editing **one** file — [`labs/labs_common/model_config.py`](labs_common/model_config.py).

### How to use it in a notebook

```python
from labs_common import HAIKU_MODEL_ID

response = bedrock.converse(
    modelId=HAIKU_MODEL_ID,
    messages=[...],
)
```

Available constants (all **US cross-region inference profile** IDs — the `us.`
prefix routes requests across `us-east-1` / `us-east-2` / `us-west-2` for
throughput and resilience):

| Constant              | Usage                                                     |
| --------------------- | --------------------------------------------------------- |
| `HAIKU_MODEL_ID`      | Bare Bedrock model ID for Claude Haiku                    |
| `SONNET_MODEL_ID`     | Bare Bedrock model ID for Claude Sonnet                   |
| `HAIKU_LITELLM_ID`    | `bedrock/<id>` prefix for LiteLLM                         |
| `SONNET_LITELLM_ID`   | `bedrock/<id>` prefix for LiteLLM                         |
| `HAIKU_STRANDS_ID`    | `bedrock:<id>` prefix for Strands Agents / pydantic-ai    |
| `SONNET_STRANDS_ID`   | `bedrock:<id>` prefix for Strands Agents / pydantic-ai    |

### How to bump to a newer Claude version

1. Edit the constants in [`labs/labs_common/model_config.py`](labs_common/model_config.py).
2. Run `uv sync` from the repo root (picks up the change in the editable install).
3. Re-run any notebook — it will use the new model ID automatically.

> **Note:** `labs_common` is registered as a `uv` workspace member and pulled in
> by the root `uv sync`, so there is **no separate install step** for students.

### Auditing notebooks for stale / hardcoded model IDs

[`scripts/migrate_model_ids.py`](../scripts/migrate_model_ids.py) does two jobs:

1. **Migrate** — walks every `labs/**/*.ipynb`, replaces known hardcoded Claude
   model-ID string literals in code cells with the matching `labs_common`
   constant, and injects the `from labs_common import ...` line at the top of
   any cell that needed it.
2. **Audit** — after migrating (or if there's nothing to migrate), scans every
   code cell for any `anthropic.claude-[34]-*` string still lurking and reports
   the offenders by file + cell index + line.

Run it from the repo root:

```bash
uv run python scripts/migrate_model_ids.py
```

Sample output when the repo is already clean:

```text
Migrated 0 cell(s) across 0 notebook(s).

Auditing for remaining legacy IDs...
  OK: no legacy IDs remain in code cells.
```

When to run it:

- **After bumping** `labs_common/model_config.py` — the audit confirms nothing
  still points at a deprecated ID directly.
- **Before submitting a PR** that touches notebooks — catch any newly-added
  hardcoded IDs before they land on main.
- **In CI** (future) — run as a drift-detection check so a deprecated ID never
  makes it into the default branch.

> The script only inspects **code cells**, not prose/markdown cells. Comments
> inside code cells are also not rewritten, so if a cell still says
> `# using Haiku 3.5` after the constant was bumped to 4.5, that's a stale
> comment to fix by hand.

## 💾 Committing notebooks

Jupyter stores every cell's output (stdout, images, execution counts, token
usage blobs) inside the `.ipynb` file itself. If we committed those, every PR
that just re-ran a cell would show a massive, noisy diff — and sometimes leak
token/cost data that wasn't meant for a public repo.

To avoid that, this repo uses [`nbstripout`](https://github.com/kynan/nbstripout)
as a **git clean filter**: outputs stay in your working copy so you can still
see them in Jupyter, but git only sees the stripped version when you stage /
commit.

### One-time setup per clone

```bash
uv run nbstripout --install
```

That writes the filter into your local `.git/config`. You only run it once per
clone. `uv sync` already pulls `nbstripout` in as a dev dependency, so there's
nothing extra to install.

### How to tell it's working

```bash
git check-attr filter <some-notebook>.ipynb
#  → <some-notebook>.ipynb: filter: nbstripout
```

When you `git diff` a notebook you've just executed, you'll only see code/markdown
changes — the output JSON is invisible to git.

### If you *want* outputs committed in a specific notebook

For a teaching notebook where students should see expected output without
running the cell, add a per-file override in `.gitattributes`:

```text
labs/module1/notebooks/1_setup_and_basics.ipynb -filter
```

## ℹ️ Additional Notes

- **Framework Interoperability**: Throughout the labs, we'll be using multiple frameworks (LangChain, LangGraph, CrewAI, etc.) to demonstrate how different tools can work together in the same application.
- **Terraform**: You don't need Terraform installed until Module 5, and it's optional for most of the labs.
- **Code Reuse**: The `agentic_platform` package in the `src/` directory is automatically available in all lab notebooks, so you can import components without copying code between modules.
- **Dependencies**: All required dependencies are specified in the `pyproject.toml` file and will be installed when you run `uv sync`.

## 🧭 Workshop Flow

1. Start with Module 1 to ensure your environment is configured correctly
2. Follow the modules in numerical order as each builds upon concepts from previous modules
3. Complete the exercises in each notebook
4. Review the example solutions provided

## 🆘 Getting Help

If you encounter issues:

1. Check your AWS credentials and permissions
2. Verify Bedrock model access (especially for Claude models)
3. Ensure all required packages are installed via `uv sync`
4. Review error messages carefully

Happy building! 🎉
