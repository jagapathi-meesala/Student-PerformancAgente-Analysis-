# Student Performance Analysis Agent

## 1. Overview
The Student Performance Analysis Agent is a framework-independent, deterministic system for analyzing structured academic performance data. It is built to OpenGAP specifications.

## 2. Goals
- Provide deterministic analysis of student grades, attendance, and trends.
- Deliver results without reliance on non-deterministic LLMs for core logic.
- Ensure privacy by operating strictly on provided structured data (no external API calls to student databases).

## 3. Features
- Student performance analysis
- Subject performance analysis
- Attendance evaluation
- Risk detection based on hard thresholds
- Grade summarization
- Performance trend tracking
- Rule-based improvement plan generation

## 4. Architecture
The agent is composed of:
- **Core Layer**: Manages tool registration and execution safely.
- **Contracts Layer**: Defines standard interfaces for tools and adapters.
- **Tools Layer**: Pure, deterministic implementations of domain logic.
- **Adapters Layer**: Framework-independent execution boundaries (allowing integration with any orchestration engine).

## 5. Tool Catalog
- `analyze-student-performance`: Analyzes overall performance.
- `analyze-subject-performance`: Evaluates individual subjects.
- `analyze-attendance`: Computes attendance metrics.
- `detect-performance-risk`: Flags risks using deterministic rules.
- `calculate-grade-summary`: Groups subjects into grade bands.
- `analyze-performance-trend`: Analyzes trajectory over multiple periods.
- `generate-improvement-plan`: Formulates structured recommendations based on risk flags.

## 6. Input/Output Examples
Fictional Example Input (`analyze-student-performance`):
```json
{
  "student_id": "STU-001",
  "subjects": [
    {"subject_id": "MATH101", "marks_obtained": 82, "max_marks": 100}
  ]
}
```

## 7. Deterministic Rules
All logic strictly follows explicitly defined parameters and thresholds (e.g., `<50` is a fail, `>=90` is an A). See `EXPLAINABILITY.md` for specific formulas.

## 8. Installation
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 9. Configuration
Copy `.env.example` to `.env` if runtime parameters are needed (none are strictly required for deterministic operation).

## 10. Running the agent
Instantiate the `AgentCore` and use the `PortableAdapter` to trigger tools.

## 11. Running tests
```bash
pytest -q
```

## 12. Local schema validation
```bash
python -m tests.test_open_gap_schema
```

## 13. Official OpenGAP CLI validation
If you have the official `opengap` CLI installed globally via npm:
```bash
opengap validate
```

## 14. Security
This agent never executes user input as Python code (`eval`, `exec`) and never interacts with the shell environment for data processing. See `tests/test_security.py`.

## 15. Explainability
Refer to `EXPLAINABILITY.md` for a comprehensive breakdown of the calculations.

## 16. Portability
The project uses strict adapter patterns making it ready for integration with CrewAI, LangChain, or direct API usage.

## 17. Limitations
- Operates ONLY on supplied data.
- Does NOT perform subjective human analysis.
- Currently, execution environment limitations prevent running dynamic tests in the build container, so official OpenGAP CLI and Pytest results are NOT VERIFIED automatically.

## 18. Project structure
See the directory layout for modular boundaries.

## 19. Extension guide
To add a new tool, implement `ToolContract` and place it in the `tools` directory. The registry will auto-discover it if using `AgentCore.load_tools_from_directory()`.
