```shell
(.venv) PS D:\Desktop\null.checked-3\backend> python test_cli.py --prompt "Build a simple physics simulation with falling grains of sand falling on the ground. The simulation will be stopped after pressing ESC. Use PyGame. It must be executed via main.py." --output ./generated_projects

[START] Initializing pipeline (max retries: 5)...

[NOTE] Processing prompt: Build a simple physics simulation with falling grains of sand falling on the ground. The simulation will be stopped after pressing ESC. Use PyGame. It must be executed via main.py.

======================================================================
[ARCH] Architect-Based Multi-Agent Pipeline - Starting
======================================================================

[PLAN] Step 1: Architect Agent - Analyzing and Planning...

  Project: sand_simulation
  Agents to create: 5
  Tests to perform: 2
  Success criteria: 3
    Agent 1: simulation_models - Data layer: defines particle and world grid data structures and their API
    Agent 2: physics_engine - Business logic: simulation rules (gravity), particle spawning and advancing the simulation step
    Agent 3: renderer_ui - UI layer: PyGame renderer and rendering helper that draws grid particles and handles input events (ESC to exit).
    Agent 4: main_cli - Application entry point: create simulation and renderer, run main loop. Responsible for program startup and clean shutdown.
    Agent 5: test_writer - Generate comprehensive tests for the simulation modules (unit + syntax).

[AGENT] Step 2: Initializing 5 Worker Agents...

  Agent 1/5: simulation_models
    Role: Data layer: defines particle and world grid data structures and their API
    Files to generate: sand_sim/__init__.py, sand_sim/models.py
    Attempt 1/5...
    [PASS] Success after 1 attempt(s)

  Agent 2/5: physics_engine
    Role: Business logic: simulation rules (gravity), particle spawning and advancing the simulation step
    Files to generate: sand_sim/engine.py
    Attempt 1/5...
    [PASS] Success after 1 attempt(s)

  Agent 3/5: renderer_ui
    Role: UI layer: PyGame renderer and rendering helper that draws grid particles and handles input events (ESC to exit).
    Files to generate: sand_sim/renderer.py
    Attempt 1/5...
    [PASS] Success after 1 attempt(s)

  Agent 4/5: main_cli
    Role: Application entry point: create simulation and renderer, run main loop. Responsible for program startup and clean shutdown.
    Files to generate: main.py
    Attempt 1/5...
    [PASS] Success after 1 attempt(s)

  Agent 5/5: test_writer
    Role: Generate comprehensive tests for the simulation modules (unit + syntax).
    Files to generate: tests/test_syntax.py, tests/test_engine.py
    Attempt 1/5...
    [PASS] Success after 1 attempt(s)

[SAVE] Step 3: Writing 10 files to disk...
[OK] Written: sand_sim/__init__.py
[OK] Written: sand_sim/models.py
[OK] Written: sand_sim/engine.py
[OK] Written: sand_sim/renderer.py
[OK] Written: main.py
[OK] Written: tests/test_syntax.py
[OK] Written: tests/test_engine.py
[OK] Written: README.md
[OK] Written: requirements.txt
[OK] Written: .gitignore
  [PASS] Project written to: generated_projects\sand_simulation

[TEST] Step 4: Running 2 tests...

  Running test: syntax_check_main (syntax)
  Description: Verify main.py Python syntax is valid
  Command: python -m py_compile main.py

  --- Test Output ---
  [OK] syntax_check_main PASSED (exit code: 0)

  STDOUT:
    Syntax check passed for 7 files
  --- End Test Output ---


  Running test: pytest_unit_tests (integration)
  Description: Run pytest to execute unit tests for engine and syntax checks
  Command: pytest -q

  --- Test Output ---
  [ERR] pytest_unit_tests FAILED (exit code: 2)

  STDOUT:
    =================================== ERRORS ====================================
    __ ERROR collecting generated_projects/sand_simulation/tests/test_engine.py ___
    ImportError while importing test module 'D:\Desktop\null.checked-3\backend\generated_projects\sand_simulation\tests\test_engine.py'.
    Hint: make sure your test modules/packages have valid Python names.
    Traceback:
    C:\Users\mimis\AppData\Local\Programs\Python\Python310\lib\importlib\__init__.py:126: in import_module
        return _bootstrap._gcd_import(name[level:], package, level)
    tests\test_engine.py:1: in <module>
        from sand_sim.engine import Simulation
    E   ModuleNotFoundError: No module named 'sand_sim'
    =========================== short test summary info ===========================
    ERROR tests\test_engine.py
    !!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
    1 error in 0.25s
  --- End Test Output ---


  Tests run: 2
  Tests passed: 1
  Tests failed: 1

[OK] Step 5: Verifying 3 success criteria...
  [FAIL] runs_without_errors: Application starts, opens a PyGame window, runs main loop, and exits cleanly when ESC is pressed or window closed.
  [FAIL] particles_fall_and_stack: Particles added to the top fall down following gravity rules and stack on the ground or on top of other particles.
  [PASS] code_syntax_valid: All generated Python files compile (no syntax errors).

======================================================================
[WARN]  Pipeline completed with some issues
======================================================================

======================================================================
[DATA] RESULTS SUMMARY
======================================================================

[FOLDER] Project: sand_simulation
[LOC] Location: generated_projects\sand_simulation
[FILE] Files Generated: 10

[AGENT] Agents Executed: 5
  [OK] simulation_models: 2 files (1 attempts)
  [OK] physics_engine: 1 files (1 attempts)
  [OK] renderer_ui: 1 files (1 attempts)
  [OK] main_cli: 1 files (1 attempts)
  [OK] test_writer: 2 files (1 attempts)

[TEST] Tests:
  Total: 2
  Passed: 1
  Failed: 1

[OK] Success Criteria:
  [ERR] runs_without_errors
  [ERR] particles_fall_and_stack
  [OK] code_syntax_valid

[TARGET] Overall Status: [WARN]  COMPLETED WITH ISSUES

======================================================================
[DONE] Done! Your project is ready at: generated_projects\sand_simulation
======================================================================
```