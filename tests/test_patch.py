import pathlib
import unittest.mock as mock
import pytest

import adk_progressive_skills.discovery as discovery
import adk_progressive_skills.patch as patch

# Create a Dummy Skill class
class DummySkill:
    def __init__(self, name, description=""):
        self.name = name
        self.description = description

@pytest.fixture
def mock_adk_skills(monkeypatch):
    # Mock load_skill_from_dir
    mock_load = mock.Mock()
    # When load_skill_from_dir is called, return a Skill named after the directory base name
    def side_effect(skill_dir):
        path = pathlib.Path(skill_dir)
        return DummySkill(name=path.name, description=str(path.resolve()))
    mock_load.side_effect = side_effect
    monkeypatch.setattr(discovery, "load_skill_from_dir", mock_load)
    return mock_load

def test_discover_skills_precedence(tmp_path, mock_adk_skills, monkeypatch):
    # Setup mock folders
    global_dir = tmp_path / "global"
    local_dir = tmp_path / "local"

    global_dir.mkdir()
    local_dir.mkdir()

    # global has skill_a
    global_skill_a = global_dir / "skill_a"
    global_skill_a.mkdir()
    (global_skill_a / "SKILL.md").touch()

    # local has skill_a and skill_b
    local_skill_a = local_dir / "skill_a"
    local_skill_a.mkdir()
    (local_skill_a / "SKILL.md").touch()

    local_skill_b = local_dir / "skill_b"
    local_skill_b.mkdir()
    (local_skill_b / "SKILL.md").touch()

    # Mock BASE_PATHS to search [global_dir, local_dir]
    monkeypatch.setattr(discovery, "BASE_PATHS", [global_dir, local_dir])

    skills = discovery.discover_skills()

    # We expect skill_a and skill_b
    assert len(skills) == 2
    skills_dict = {s.name: s for s in skills}
    assert "skill_a" in skills_dict
    assert "skill_b" in skills_dict

    # Check precedence: skill_a must come from local_dir (highest precedence)
    assert skills_dict["skill_a"].description == str(local_skill_a.resolve())

def test_discover_skills_error_handling(tmp_path, monkeypatch):
    global_dir = tmp_path / "global"
    global_dir.mkdir()
    skill_a = global_dir / "skill_a"
    skill_a.mkdir()
    (skill_a / "SKILL.md").touch()

    # load_skill_from_dir raises exception
    mock_load = mock.Mock(side_effect=Exception("Failed to read SKILL.md"))
    monkeypatch.setattr(discovery, "load_skill_from_dir", mock_load)
    monkeypatch.setattr(discovery, "BASE_PATHS", [global_dir])

    # Should not raise exception, but issue warning
    with pytest.warns(UserWarning, match="Failed to load skill from"):
        skills = discovery.discover_skills()
    
    assert len(skills) == 0

def test_apply_patch(monkeypatch):
    # Setup mock Agent/LlmAgent
    class MockLlmAgent:
        def __init__(self, **kwargs):
            self.tools = kwargs.get("tools", [])

    # Mock SkillToolset class
    class MockSkillToolset:
        def __init__(self, skills):
            self.skills = skills

    # Patch modules in patch.py
    monkeypatch.setattr(patch, "LlmAgent", MockLlmAgent)
    monkeypatch.setattr(patch, "SkillToolset", MockSkillToolset)

    # Mock discover_skills
    dummy_skills = [DummySkill(name="discovered_skill")]
    monkeypatch.setattr(patch, "discover_skills", lambda: dummy_skills)

    # Reset patched state if any
    if hasattr(MockLlmAgent, "_skills_patched"):
        delattr(MockLlmAgent, "_skills_patched")

    # Apply patch
    patch.apply_patch()

    # Instantiate MockLlmAgent
    agent = MockLlmAgent()

    # Verify SkillToolset was added
    assert len(agent.tools) == 1
    assert isinstance(agent.tools[0], MockSkillToolset)
    assert agent.tools[0].skills == dummy_skills

    # Instantiate MockLlmAgent again, but with an existing tool list including SkillToolset
    existing_toolset = MockSkillToolset(skills=[])
    agent2 = MockLlmAgent(tools=[existing_toolset])

    # Verify no duplicate was added
    assert len(agent2.tools) == 1
    assert agent2.tools[0] is existing_toolset
