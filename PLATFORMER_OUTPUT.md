```bash
(.venv) PS D:\Desktop\null.checked-3\backend> python test_cli.py --prompt "Build a simple platformer game where you collect keys to pass through the door. It must be executed via main.py." --output ./generated_projects

[START] Initializing pipeline (max retries: 5)...

[NOTE] Processing prompt: Build a simple platformer game where you collect keys to pass through the door. It must be executed via main.py.

======================================================================
[ARCH] Architect-Based Multi-Agent Pipeline - Starting
======================================================================

[PLAN] Step 1: Architect Agent - Analyzing and Planning...

  Project: platformer_keys
  Agents to create: 5
  Tests to perform: 4
  Success criteria: 4
    Agent 1: assets_manager - Load and provide image/sound assets with fallbacks so game can run without external asset files.
    Agent 2: game_models - Define all game entity classes and Level container used by the game loop.
    Agent 3: game_engine - Implement the Game class that runs the main loop, handles events, updates, and draws using pygame and the models/assets classes.
    Agent 4: main_cli - Provide the program entry point main.py to initialize and run the Game; support a --test flag to run a single iteration for automated testing.
    Agent 5: test_writer - Generate pytest tests that validate syntax, basic model behavior, assets manager, and a short integration run via main.py --test.

[AGENT] Step 2: Initializing 5 Worker Agents...

  Agent 1/5: assets_manager
    Role: Load and provide image/sound assets with fallbacks so game can run without external asset files.
    Files to generate: src/assets.py, src/__init__.py
    Attempt 1/5...
    [PASS] Success after 1 attempt(s)

  Agent 2/5: game_models
    Role: Define all game entity classes and Level container used by the game loop.
    Files to generate: src/models.py
    Attempt 1/5...
    [PASS] Success after 1 attempt(s)

  Agent 3/5: game_engine
    Role: Implement the Game class that runs the main loop, handles events, updates, and draws using pygame and the models/assets classes.
    Files to generate: src/game.py
    Attempt 1/5...
    [PASS] Success after 1 attempt(s)

  Agent 4/5: main_cli
    Role: Provide the program entry point main.py to initialize and run the Game; support a --test flag to run a single iteration for automated testing.
    Files to generate: main.py
    Attempt 1/5...
    [PASS] Success after 1 attempt(s)

  Agent 5/5: test_writer
    Role: Generate pytest tests that validate syntax, basic model behavior, assets manager, and a short integration run via main.py --test.
    Files to generate: tests/test_syntax.py, tests/test_assets.py, tests/test_models.py, tests/test_integration_main.py
    Attempt 1/5...
    [PASS] Success after 1 attempt(s)

[SAVE] Step 3: Writing 12 files to disk...
[OK] Written: src/assets.py
[OK] Written: src/__init__.py
[OK] Written: src/models.py
[OK] Written: src/game.py
[OK] Written: main.py
[OK] Written: tests/test_syntax.py
[OK] Written: tests/test_assets.py
[OK] Written: tests/test_models.py
[OK] Written: tests/test_integration_main.py
[OK] Written: README.md
[OK] Written: requirements.txt
[OK] Written: .gitignore
  [PASS] Project written to: generated_projects\platformer_keys

[TEST] Step 4: Running 4 tests...

  Running test: syntax_check_main (syntax)
  Description: Verify main.py has valid Python syntax
  Command: python -m py_compile main.py

  --- Test Output ---
  [OK] syntax_check_main PASSED (exit code: 0)

  STDOUT:
    Syntax check passed for 9 files
  --- End Test Output ---


  Running test: syntax_check_src (syntax)
  Description: Verify all src modules have valid Python syntax
  Command: python -m py_compile src/assets.py src/models.py src/game.py

  --- Test Output ---
  [OK] syntax_check_src PASSED (exit code: 0)

  STDOUT:
    Syntax check passed for 9 files
  --- End Test Output ---


  Running test: pytest_suite (integration)
  Description: Run pytest suite to execute unit and integration tests
  Command: python -m pytest -q

  --- Test Output ---
  [OK] pytest_suite PASSED (exit code: 0)

  STDOUT:
    .....                                                                    [100%]
    5 passed in 0.67s
  --- End Test Output ---


  Running test: functional_run_testmode (functional)
  Description: Run the main entry in test mode (single frame) to ensure start-up works headlessly
  Command: python main.py --test

  --- Test Output ---
  [OK] functional_run_testmode PASSED (exit code: 0)

  STDOUT:
    pygame 2.6.1 (SDL 2.28.4, Python 3.10.0)
    Hello from the pygame community. https://www.pygame.org/contribute.html
  --- End Test Output ---


  Tests run: 4
  Tests passed: 4
  Tests failed: 0

[OK] Step 5: Verifying 4 success criteria...
  [PASS] files_compiled: All Python files in the project compile without syntax errors
  [FAIL] unit_tests_pass: All pytest unit tests pass validating assets manager and model behaviors
  [FAIL] functional_start: The game can start in headless test mode and exit cleanly
  [FAIL] run_without_assets: The game runs and uses placeholder assets when image/sound files are missing

======================================================================
[WARN]  Pipeline completed with some issues
======================================================================

======================================================================
[DATA] RESULTS SUMMARY
======================================================================

[FOLDER] Project: platformer_keys
[LOC] Location: generated_projects\platformer_keys
[FILE] Files Generated: 12

[AGENT] Agents Executed: 5
  [OK] assets_manager: 2 files (1 attempts)
  [OK] game_models: 1 files (1 attempts)
  [OK] game_engine: 1 files (1 attempts)
  [OK] main_cli: 1 files (1 attempts)
  [OK] test_writer: 4 files (1 attempts)

[TEST] Tests:
  Total: 4
  Passed: 4
  Failed: 0

[OK] Success Criteria:
  [OK] files_compiled
  [ERR] unit_tests_pass
  [ERR] functional_start
  [ERR] run_without_assets

[TARGET] Overall Status: [WARN]  COMPLETED WITH ISSUES
```