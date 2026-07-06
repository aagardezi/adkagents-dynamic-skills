import os
import pathlib
import warnings

try:
    from google.adk.skills import load_skill_from_dir, models
except ImportError:
    from google.adk.skills._utils import _load_skill_from_dir as load_skill_from_dir
    from google.adk.skills import models

BASE_PATHS = [
    pathlib.Path("~/.gemini/config/skills"),
    pathlib.Path("~/.agents/skills"),
    pathlib.Path(".agents/skills"),
]

def discover_skills() -> list:
    # Base directories in order of increasing precedence (lowest precedence first)
    base_paths = [
        p.expanduser() if str(p).startswith("~") else p.resolve()
        for p in BASE_PATHS
    ]

    skills_by_name = {}

    for base_path in base_paths:
        if not base_path.is_dir():
            continue

        try:
            for entry in base_path.iterdir():
                if entry.is_dir():
                    skill_md_path = entry / "SKILL.md"
                    if skill_md_path.is_file():
                        try:
                            # load_skill_from_dir expects str or Path
                            skill = load_skill_from_dir(entry)
                            if skill and hasattr(skill, "name") and skill.name:
                                skills_by_name[skill.name] = skill
                        except Exception as e:
                            warnings.warn(
                                f"Failed to load skill from {entry}: {e}",
                                category=UserWarning
                            )
        except Exception as e:
            warnings.warn(
                f"Error scanning directory {base_path}: {e}",
                category=UserWarning
            )

    return list(skills_by_name.values())
