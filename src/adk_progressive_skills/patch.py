import logging
import warnings

from adk_progressive_skills.discovery import discover_skills

try:
    from google.adk.tools import SkillToolset
except ImportError:
    from google.adk.tools.skill_toolset import SkillToolset

try:
    from google.adk.agents.llm_agent import LlmAgent
except ImportError:
    try:
        from google.adk.agents import Agent as LlmAgent
    except ImportError:
        LlmAgent = None

logger = logging.getLogger(__name__)

def apply_patch():
    if LlmAgent is None:
        warnings.warn(
            "google-adk LlmAgent class not found. Skipping patching.",
            category=UserWarning
        )
        return

    if getattr(LlmAgent, "_skills_patched", False):
        return

    original_init = LlmAgent.__init__

    def patched_init(self, *args, **kwargs):
        discovered_skills = discover_skills()
        if discovered_skills:
            tools = kwargs.setdefault("tools", [])
            if not isinstance(tools, list):
                tools = list(tools)
                kwargs["tools"] = tools

            # Ensure we do not add a duplicate SkillToolset
            if not any(isinstance(t, SkillToolset) for t in tools):
                try:
                    skill_toolset = SkillToolset(skills=discovered_skills)
                    tools.append(skill_toolset)
                except Exception as e:
                    warnings.warn(
                        f"Failed to create or append SkillToolset: {e}",
                        category=UserWarning
                    )

        original_init(self, *args, **kwargs)

    LlmAgent.__init__ = patched_init
    LlmAgent._skills_patched = True
    logger.info("Successfully patched LlmAgent for progressive skill discovery.")
