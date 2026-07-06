# ADK Progressive Skills Samples

This directory contains functional code samples demonstrating the automatic progressive skill discovery feature for both ADK 1.x and ADK 2.0.

## Mock Skill Structure

A mock skill is set up under `mock_skills/weather-skill/`. It consists of:
- `SKILL.md`: Contains a frontmatter with `name: weather-skill` (valid lowercase kebab-case) and `description`, followed by instructions for the agent.

## Verification Samples

1. **ADK 1.x Style Sample (`adk1_sample/run_sample.py`)**:
   - Programmatically sets up a local `.agents/skills/weather-skill` directory containing the mock skill.
   - Imports `adk_progressive_skills` to trigger monkeypatching.
   - Imports `Agent` from `google.adk.agents`.
   - Instantiates the agent and asserts that `SkillToolset` containing `weather-skill` is automatically loaded into the agent tools.

2. **ADK 2.0 Style Sample (`adk2_sample/run_sample.py`)**:
   - Performs the same dynamic discovery verification using the ADK 2.0 `LlmAgent` class (`google.adk.agents.llm_agent.LlmAgent`).

## Running the Samples

You can run the samples using `uv` (the default runner configured for this workspace):

```bash
# Run ADK 1.x Sample
uv run python samples/adk1_sample/run_sample.py

# Run ADK 2.0 Sample
uv run python samples/adk2_sample/run_sample.py
```
