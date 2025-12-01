```shell
(.venv) PS D:\Desktop\null.checked-3\backend> python test_cli.py --prompt "Build a simple 3d maze inspired by Doom, where you can walk and rotate camera using WASD. Use pygame, and main.py for execution." --output ./generated_projects

[START] Initializing pipeline (max retries: 5)...

[NOTE] Processing prompt: Build a simple 3d maze inspired by Doom, where you can walk and rotate camera using WASD. Use pygame, and main.py for execution.

======================================================================
[ARCH] Architect-Based Multi-Agent Pipeline - Starting
======================================================================

[PLAN] Step 1: Architect Agent - Analyzing and Planning...

  Project: doom_style_3d_maze
  Agents to create: 5
  Tests to perform: 6
  Success criteria: 4
    Agent 1: core_data_models - Define map data structures and player model with movement and collision
    Agent 2: engine_raycast - Implement raycasting math to detect walls and distances
    Agent 3: engine_renderer - Render the 3D view (and optional minimap) using pygame
    Agent 4: app_main - Set up pygame app, wire components, and run the game loop with WASD controls
    Agent 5: test_writer - Generate unit tests and ensure syntax validity

[AGENT] Step 2: Initializing 5 Worker Agents...

  Agent 1/5: core_data_models
    Role: Define map data structures and player model with movement and collision
    Files to generate: core/map_data.py, core/player.py
    Attempt 1/5...
    [PASS] Success after 1 attempt(s)

  Agent 2/5: engine_raycast
    Role: Implement raycasting math to detect walls and distances
    Files to generate: engine/raycast.py
    Attempt 1/5...
    [PASS] Success after 1 attempt(s)

  Agent 3/5: engine_renderer
    Role: Render the 3D view (and optional minimap) using pygame
    Files to generate: engine/renderer.py
    Attempt 1/5...
    [PASS] Success after 1 attempt(s)

  Agent 4/5: app_main
    Role: Set up pygame app, wire components, and run the game loop with WASD controls
    Files to generate: main.py
    Attempt 1/5...
    [PASS] Success after 1 attempt(s)

  Agent 5/5: test_writer
    Role: Generate unit tests and ensure syntax validity
    Files to generate: tests/test_raycast.py
    Attempt 1/5...
    [PASS] Success after 1 attempt(s)

[SAVE] Step 3: Writing 9 files to disk...
[OK] Written: core/map_data.py
[OK] Written: core/player.py
[OK] Written: engine/raycast.py
[OK] Written: engine/renderer.py
[OK] Written: main.py
[OK] Written: tests/test_raycast.py
[OK] Written: README.md
[OK] Written: requirements.txt
[OK] Written: .gitignore
  [PASS] Project written to: generated_projects\doom_style_3d_maze

[TEST] Step 4: Running 6 tests...

  Running test: syntax_check_main (syntax)
  Description: Verify Python syntax is valid for main.py
  Command: python -m py_compile main.py

  --- Test Output ---
  [OK] syntax_check_main PASSED (exit code: 0)

  STDOUT:
    Syntax check passed for 6 files
  --- End Test Output ---


  Running test: syntax_check_core_map_data (syntax)
  Description: Verify Python syntax is valid for core/map_data.py
  Command: python -m py_compile core/map_data.py

  --- Test Output ---
  [OK] syntax_check_core_map_data PASSED (exit code: 0)

  STDOUT:
    Syntax check passed for 6 files
  --- End Test Output ---


  Running test: syntax_check_core_player (syntax)
  Description: Verify Python syntax is valid for core/player.py
  Command: python -m py_compile core/player.py

  --- Test Output ---
  [OK] syntax_check_core_player PASSED (exit code: 0)

  STDOUT:
    Syntax check passed for 6 files
  --- End Test Output ---


  Running test: syntax_check_engine_raycast (syntax)
  Description: Verify Python syntax is valid for engine/raycast.py
  Command: python -m py_compile engine/raycast.py

  --- Test Output ---
  [OK] syntax_check_engine_raycast PASSED (exit code: 0)

  STDOUT:
    Syntax check passed for 6 files
  --- End Test Output ---


  Running test: syntax_check_engine_renderer (syntax)
  Description: Verify Python syntax is valid for engine/renderer.py
  Command: python -m py_compile engine/renderer.py

  --- Test Output ---
  [OK] syntax_check_engine_renderer PASSED (exit code: 0)

  STDOUT:
    Syntax check passed for 6 files
  --- End Test Output ---


  Running test: unit_tests (unit)
  Description: Run unit tests for raycasting and map logic using unittest
  Command: python -m unittest discover -s tests -p 'test_*.py'

  --- Test Output ---
  [OK] unit_tests PASSED (exit code: 0)

  STDERR:
    ----------------------------------------------------------------------
    Ran 0 tests in 0.000s

    OK
  --- End Test Output ---


  Tests run: 6
  Tests passed: 6
  Tests failed: 0

[OK] Step 5: Verifying 4 success criteria...
  [FAIL] runs_without_errors: Application starts and the main loop runs without crashing
  [PASS] wasd_controls_work: W/S move player forward/back relative to view; A/D rotate the camera left/right
  [PASS] maze_renders_with_walls: Walls are rendered as vertical slices with basic shading and floor/ceiling colors
  [FAIL] raycasting_math_correctness: Raycasting returns expected distances in controlled scenarios

======================================================================
[WARN]  Pipeline completed with some issues
======================================================================

======================================================================
[DATA] RESULTS SUMMARY
======================================================================

[FOLDER] Project: doom_style_3d_maze
[LOC] Location: generated_projects\doom_style_3d_maze
[FILE] Files Generated: 9

[AGENT] Agents Executed: 5
  [OK] core_data_models: 2 files (1 attempts)
  [OK] engine_raycast: 1 files (1 attempts)
  [OK] engine_renderer: 1 files (1 attempts)
  [OK] app_main: 1 files (1 attempts)
  [OK] test_writer: 1 files (1 attempts)

[TEST] Tests:
  Total: 6
  Passed: 6
  Failed: 0

[OK] Success Criteria:
  [ERR] runs_without_errors
  [OK] wasd_controls_work
  [OK] maze_renders_with_walls
  [ERR] raycasting_math_correctness

[TARGET] Overall Status: [WARN]  COMPLETED WITH ISSUES

======================================================================
[DONE] Done! Your project is ready at: generated_projects\doom_style_3d_maze
======================================================================
```