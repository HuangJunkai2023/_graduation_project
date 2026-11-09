Source: v4-sections native SWJTU template deck.
Prepare: python source/prepare_5min.py
Native workspace: ../workspace (ppt-master roundtrip).
Export: ppt-master/scripts/svg_to_pptx.py <workspace> --roundtrip
Render: source/render_and_validate.ps1 -Candidate <exported.pptx> -OutputDir <this output directory>
Verify: python source/verify_5min.py
Use the isolated runtime C:/Users/44282/.codex/skill-runtimes/ppt-master/.venv/Scripts/python.exe.
