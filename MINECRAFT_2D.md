```shell
(.venv) PS D:\Desktop\null.checked-3\backend> python test_cli.py --prompt "Build a really simple minecraft clone with a possibility to place and break blocks. It must be executed via main.py." --output ./generated_projects

[START] Initializing pipeline (max retries: 5)...

[NOTE] Processing prompt: Build a really simple minecraft clone with a possibility to place and break blocks. It must be executed via main.py.

======================================================================
[ARCH] Architect-Based Multi-Agent Pipeline - Starting
======================================================================

[PLAN] Step 1: Architect Agent - Analyzing and Planning...

  Project: simple_minecraft_clone
  Agents to create: 5
  Tests to perform: 5
  Success criteria: 3
    Agent 1: world_models - Data models and persistent world state
    Agent 2: renderer - 2D rendering of the block grid and coordinate transformations (pygame based)
    Agent 3: game_engine - Game loop, input handling, block placement and breaking logic
    Agent 4: main - Application entry point and argument parsing
    Agent 5: test_writer - Generate pytest unit and functional tests

[AGENT] Step 2: Initializing 5 Worker Agents...

  Agent 1/5: world_models
    Role: Data models and persistent world state
    Files to generate: world/models.py
    Attempt 1/5...
    [PASS] Success after 1 attempt(s)

  Agent 2/5: renderer
    Role: 2D rendering of the block grid and coordinate transformations (pygame based)
    Files to generate: renderer/renderer.py
    Attempt 1/5...
    [PASS] Success after 1 attempt(s)

  Agent 3/5: game_engine
    Role: Game loop, input handling, block placement and breaking logic
    Files to generate: engine/game_engine.py
    Attempt 1/5...
    [PASS] Success after 1 attempt(s)

  Agent 4/5: main
    Role: Application entry point and argument parsing
    Files to generate: main.py
    Attempt 1/5...
    [PASS] Success after 1 attempt(s)

  Agent 5/5: test_writer
    Role: Generate pytest unit and functional tests
    Files to generate: tests/test_world.py, tests/test_main.py
    Attempt 1/5...
    [PASS] Success after 1 attempt(s)

[SAVE] Step 3: Writing 9 files to disk...
[OK] Written: world/models.py
[OK] Written: renderer/renderer.py
[OK] Written: engine/game_engine.py
[OK] Written: main.py
[OK] Written: tests/test_world.py
[OK] Written: tests/test_main.py
[OK] Written: README.md
[OK] Written: requirements.txt
[OK] Written: .gitignore
  [PASS] Project written to: generated_projects\simple_minecraft_clone

[TEST] Step 4: Running 5 tests...

  Running test: syntax_main (syntax)
  Description: Verify Python syntax of main.py is valid
  Command: python -m py_compile main.py

  --- Test Output ---
  [OK] syntax_main PASSED (exit code: 0)

  STDOUT:
    Syntax check passed for 6 files
  --- End Test Output ---


  Running test: syntax_world_models (syntax)
  Description: Verify Python syntax of world/models.py is valid
  Command: python -m py_compile world/models.py

  --- Test Output ---
  [OK] syntax_world_models PASSED (exit code: 0)

  STDOUT:
    Syntax check passed for 6 files
  --- End Test Output ---


  Running test: syntax_renderer (syntax)
  Description: Verify Python syntax of renderer/renderer.py is valid
  Command: python -m py_compile renderer/renderer.py

  --- Test Output ---
  [OK] syntax_renderer PASSED (exit code: 0)

  STDOUT:
    Syntax check passed for 6 files
  --- End Test Output ---


  Running test: syntax_game_engine (syntax)
  Description: Verify Python syntax of engine/game_engine.py is valid
  Command: python -m py_compile engine/game_engine.py

  --- Test Output ---
  [OK] syntax_game_engine PASSED (exit code: 0)

  STDOUT:
    Syntax check passed for 6 files
  --- End Test Output ---


  Running test: unit_pytest (integration)
  Description: Run pytest to execute unit and functional tests
  Command: python -m pytest -q

  --- Test Output ---
  [OK] unit_pytest PASSED (exit code: 0)

  STDOUT:
    ...                                                                      [100%]
    3 passed in 0.63s
  --- End Test Output ---


  Tests run: 5
  Tests passed: 5
  Tests failed: 0

[OK] Step 5: Verifying 3 success criteria...
  [FAIL] runs_without_errors: The application starts and runs without crashing in test mode and returns exit code 0.
  [FAIL] place_and_break_blocks: Player can left-click to place the selected block type and right-click to remove blocks. World state updates accordingly.
  [PASS] syntax_valid_python: All generated Python files pass a syntax check.

======================================================================
[WARN]  Pipeline completed with some issues
======================================================================

======================================================================
[DATA] RESULTS SUMMARY
======================================================================

[FOLDER] Project: simple_minecraft_clone
[LOC] Location: generated_projects\simple_minecraft_clone
[FILE] Files Generated: 9

[AGENT] Agents Executed: 5
  [OK] world_models: 1 files (1 attempts)
  [OK] renderer: 1 files (1 attempts)
  [OK] game_engine: 1 files (1 attempts)
  [OK] main: 1 files (1 attempts)
  [OK] test_writer: 2 files (1 attempts)

[TEST] Tests:
  Total: 5
  Passed: 5
  Failed: 0

[OK] Success Criteria:
  [ERR] runs_without_errors
  [ERR] place_and_break_blocks
  [OK] syntax_valid_python

[TARGET] Overall Status: [WARN]  COMPLETED WITH ISSUES

======================================================================
[DONE] Done! Your project is ready at: generated_projects\simple_minecraft_clone
======================================================================
```