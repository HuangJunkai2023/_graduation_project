Edit Native PPTX revision, based on v4-sections.
Source SVGs and page plan: ../workspace
Prepare: python source/prepare_revision.py (after importing a fresh v4 workspace).
Export: ppt-master svg_to_pptx.py <workspace> --roundtrip --primary-language en-US
Render with source/render_and_validate.ps1 and verify with source/verify_5min.py.
Use C:/Users/44282/.codex/skill-runtimes/ppt-master/.venv/Scripts/python.exe.
