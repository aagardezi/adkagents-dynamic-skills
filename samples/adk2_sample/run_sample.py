import os
import pathlib
import shutil

# Setup local skill directory for discovery
local_skills_dir = pathlib.Path(".agents/skills")
local_skills_dir.mkdir(parents=True, exist_ok=True)

# Copy mock skill to .agents/skills/weather-skill
mock_skill_src = pathlib.Path("samples/mock_skills/weather-skill")
mock_skill_dest = local_skills_dir / "weather-skill"
if mock_skill_dest.exists():
    shutil.rmtree(mock_skill_dest)
shutil.copytree(mock_skill_src, mock_skill_dest)

try:
    # 1. Import adk_progressive_skills to trigger monkeypatch
    import adk_progressive_skills

    # 2. Import ADK 2.0 style LlmAgent class
    from google.adk.agents.llm_agent import LlmAgent

    # 3. Instantiate LlmAgent
    print("Instantiating ADK 2.0 LlmAgent...")
    agent = LlmAgent(
        name="weather_reporter_v2",
        instruction="Tell user about weather in ADK 2.0.",
        model="gemini-3.5-flash",
        tools=[],
    )

    # 4. Verify that SkillToolset was automatically added
    print("Agent tools:", agent.tools)
    assert len(agent.tools) == 1, f"Expected 1 tool, got {len(agent.tools)}"
    
    toolset = agent.tools[0]
    assert type(toolset).__name__ == "SkillToolset", f"Expected SkillToolset, got {type(toolset).__name__}"
    
    skill_names = [s.name for s in toolset.skills]
    print("Loaded skills in toolset:", skill_names)
    assert "weather-skill" in skill_names, f"weather-skill not found in {skill_names}"

    print("ADK 2.0 Sample Verification PASSED!")

finally:
    # Cleanup
    if mock_skill_dest.exists():
        shutil.rmtree(mock_skill_dest)
