# Explainability

## Agent Purpose
The exact purpose of the Student Performance Analysis Agent is to perform deterministic, rule-based analysis of structured academic records provided by a user.
- **Problem solved**: Automating the mathematical calculation and static rule-based flagging of student performance risks, grade bucketing, and attendance thresholding.
- **Input accepted**: Structured JSON payloads strictly conforming to defined schemas (numerical scores, IDs, and boolean flags).
- **Output produced**: Structured JSON payloads containing calculated percentages, boolean flags, categorized string tags, and static plan recommendations.
- **Nature of analysis**: The core analysis is 100% deterministic and rule-based.
- **LLM usage**: The agent does **NOT** use an LLM for any analysis, decision making, or output generation.
- **External retrieval**: The agent does **NOT** retrieve external student data, LMS data, or API information.
- **What it does NOT do**: It does **NOT** make institutional decisions, provide medical/psychological conclusions, or perform predictions beyond explicitly implemented deterministic math rules.

## Inputs
| Tool | Field Name | Required | Data Type | Valid Range/Constraints | Source | Missing/Invalid Behavior |
|---|---|---|---|---|---|---|
| analyze-student-performance | student_id | Yes | string | N/A | User | Raises ValueError |
| analyze-student-performance | student_name | No | string | N/A | User | Safely ignored if missing |
| analyze-student-performance | subjects | Yes | array(obj) | Non-empty, unique IDs | User | Raises ValueError |
| analyze-student-performance | subjects[].marks_obtained | Yes | number | >= 0, <= max_marks | User | Raises ValueError |
| analyze-student-performance | subjects[].max_marks | Yes | number | > 0 | User | Raises ValueError |
| analyze-student-performance | attendance_percentage | No | number | 0 - 100 | User | Raises ValueError if invalid |
| analyze-subject-performance | subjects | Yes | array(obj) | marks >= 0, <= max | User | Raises ValueError |
| analyze-attendance | student_id | Yes | string | N/A | User | Raises ValueError |
| analyze-attendance | attendance_percentage | Conditional | number | 0 - 100 (if no classes) | User | Raises ValueError |
| analyze-attendance | classes_attended | Conditional | integer | >= 0, <= conducted | User | Raises ValueError |
| analyze-attendance | classes_conducted | Conditional | integer | > 0 (if no percentage) | User | Raises ValueError |
| detect-performance-risk | overall_percentage | No | number | 0 - 100 | User | Raises ValueError if invalid |
| detect-performance-risk | attendance_percentage | No | number | 0 - 100 | User | Raises ValueError if invalid |
| detect-performance-risk | failing_subjects_count | No | integer | >= 0 | User | Raises ValueError if invalid |
| detect-performance-risk | recent_performance_change | No | number | Numeric | User | Raises ValueError if invalid |
| calculate-grade-summary | array or subjects array | Yes | array(obj) | Non-empty | User | Raises ValueError |
| analyze-performance-trend | student_id | Yes | string | N/A | User | Raises ValueError |
| analyze-performance-trend | periods | Yes | array(obj) | Min 2, unique periods | User | Raises ValueError |
| generate-improvement-plan | weak_subjects | No | array(str) | Strings | User | Defaults to empty / ignored |
| generate-improvement-plan | attendance_concern | No | boolean | True/False | User | Defaults to False |
| generate-improvement-plan | declining_trend | No | boolean | True/False | User | Defaults to False |
| generate-improvement-plan | low_overall_percentage | No | boolean | True/False | User | Defaults to False |

## Data Sources and Provenance
- **USER-SUPPLIED DATA**: All inputs mapped in the payload (`student_id`, `marks_obtained`, `classes_conducted`, etc.).
- **DERIVED DATA**: Mathematical aggregations and percentage formulas (e.g., `percentage`, `overall_percentage`, `shortage_percentage`).
- **STATIC RULES**: Hardcoded boundaries (e.g., passing >= 50, A >= 90) used to generate classifications.
- **SYSTEM/CONFIGURATION DATA**: None.
- **EXTERNAL DATA**: **None.** There are absolutely no external APIs, databases, LMS systems, SIS systems, or web searches used.

For every calculated result, its provenance:
- `percentage` is derived directly from user-supplied `marks_obtained` and `max_marks`.
- Risk flags are derived strictly by comparing user-supplied values against static rules.

## Decision / Reasoning
The deterministic decision process flows strictly as follows:
`INPUT` → `VALIDATION` → `CALCULATION` → `RULE EVALUATION` → `CLASSIFICATION` → `OUTPUT`

- **Operators**: Standard exact operators (`>`, `>=`, `<`, `<=`, `==`).
- **Thresholds**: Defined explicitly in the code as static floats/ints.
- **Boundary conditions**: A boundary hit behaves exactly per the operator. If the rule is `>= 50`, `50.0` triggers the positive branch.
- **Precedence & if/elif ordering**: If/elif blocks are mutually exclusive and evaluate top-down. The first matching condition halts further evaluation for that variable.
- **Independent rules**: Boolean rules (e.g., in `generate-improvement-plan` and `detect-performance-risk`) are completely independent and evaluate sequentially without short-circuiting each other.
- **Tool chaining**: Tools do **NOT** automatically chain. They are executed independently.
- **Determinism**: Outputs are strictly 100% deterministic.

## Tools / Capabilities
| Tool | Purpose | Inputs | Validation | Decision Logic | Formula | Thresholds | Output | Errors | Limitations | Source File | Implementation | Tests |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| analyze-student-performance | Aggregate totals | student_id, subjects array | marks >= 0, max > 0, unique IDs | Map pass/fail per subject | `(marks/max)*100` | Pass >= 50 | Totals, pass/fail arrays | ValueError | Only sees provided subjects | `analyze-student-performance.py` | `Tool.execute` | `test_tools.py` |
| analyze-subject-performance | Classify individual subjects | subjects array | marks <= max | `if/elif` mapped string bands | `(marks/max)*100` | 90, 75, 60, 40 | Band arrays, strings | ValueError | No historical inference | `analyze-subject-performance.py` | `Tool.execute` | `test_tools.py` |
| analyze-attendance | Flag attendance risk | student_id, classes/pct | counts > 0, attended <= conducted | `if/elif` string bands | `(att/cond)*100`, shortage calc | 90, 75, 65 | Pct, category, shortage | ValueError | No excuse handling | `analyze-attendance.py` | `Tool.execute` | `test_tools.py` |
| detect-performance-risk | Trigger risk flags | optional metric aggregates | ranges 0-100, counts >= 0 | Append risk obj if true | None (Boolean check) | overall < 50, failing >= 2, etc. | Risk array | ValueError | Requires external aggregation | `detect-performance-risk.py` | `Tool.execute` | `test_tools.py` |
| calculate-grade-summary | Create grade histogram | subjects array | Non-empty | `if/elif` A-F bucket increments | Average of array | 90, 80, 70, 60 | Counts dict | ValueError | Unweighted | `calculate-grade-summary.py` | `Tool.execute` | `test_tools.py` |
| analyze-performance-trend | Detect score trajectory | student_id, periods array | Min 2 periods, unique | `if/elif` on absolute change | `latest - first` | +/- 5 | Trend string, change values | ValueError | Chronology assumed by array order | `analyze-performance-trend.py` | `Tool.execute` | `test_tools.py` |
| generate-improvement-plan | Map flags to text actions | bool flags, array | Type checking | `if flag: append(action)` | None | N/A | Actions arrays | None (safe defaults) | Hardcoded text only | `generate-improvement-plan.py` | `Tool.execute` | `test_tools.py` |

## Tool Selection
The tool is strictly selected via explicit user/adapter routing. The `AgentCore` dynamically loads python modules from the `tools/` directory and instantiates them via `DynamicToolRegistry`. `AgentCore.execute_tool(tool_name, input_data)` strictly routes the payload by the literal `tool_name` string. There is no LLM-based tool selection.

## Tool-by-Tool Explainability
*(See the comprehensive breakdown in the "Decision/Rule Transparency" section below).*

## Limitations / Constraints
- **Supplied-data-only operation**: Operates exclusively on the data provided in the JSON payload.
- **No hidden student information**: Assumes zero prior knowledge of the student.
- **No unsupported institutional policy inference**: Uses only the static mathematical thresholds explicitly written in the code.
- **No medical/psychological inference**: Does not contextually evaluate why a score dropped.
- **No predictive claims**: Outputs exact mathematical historical measurements, not future predictions.
- **No automatic institutional decisions**: Does not enroll or unenroll students.
- **No automatic tool chaining**: Does not pipe outputs of Tool A into Tool B.
- **No external retrieval**: Does not ping external databases.
- **Portability limitations**: Requires Python 3 to execute the deterministic scripts.

## Portability
- **Framework independence**: The agent core and tools are standard Python with no third-party framework dependencies.
- **Adapter boundary**: The `PortableAdapter` (`adapters/portable_adapter.py`) acts as the neutral API border, allowing any external runtime to pass JSON into the agent.
- **Core/tool separation**: Tools are encapsulated in `contracts/tool_contract.py` subclasses and dynamically discovered by `core/registry.py`.
- **Invocation**: Another runtime invokes the agent simply by calling the adapter execution method with standard dictionaries.

## Verification
Actual verification evidence:
- **pytest**: PASSED locally (verifies determinism, math, and contracts).
- **readiness audit**: PASSED locally (verifies file presence and absence of hardcoded secrets).
- **OpenGAP validation**: The `agent.yaml` manifest uses `spec_version: "0.1.0"`.
- **Security tests**: `test_no_unsafe_code` explicitly validates the absence of `eval`, `exec`, and shell commands.

*(Note: **HIDEVS VERIFICATION** is exclusively granted by the external HiDevs portal. The status in this document reflects only local verification, and no official passport is claimed here).*

## Failure Handling
| Failure | Detection | Actual behavior | Exception/output | Safe boundary |
|---|---|---|---|---|
| Missing required fields | Tool validation | Halts before calc | `ValueError` | Explicit failure |
| Wrong types | `isinstance()` | Halts before calc | `ValueError` | Explicit failure |
| Invalid percentages | `< 0` or `> 100` | Halts before calc | `ValueError` | Explicit failure |
| Negative values | `< 0` | Halts before calc | `ValueError` | Explicit failure |
| Marks > Max Marks | `marks_obtained > max_marks` | Halts before calc | `ValueError` | Explicit failure |
| Zero denominators | `max_marks <= 0` | Halts before calc | `ValueError` | Prevents ZeroDivisionError |
| Empty arrays | `len() == 0` | Halts before calc | `ValueError` | Prevents math errors |
| Duplicate subjects/periods | Set insertion check | Halts before calc | `ValueError` | Preserves data integrity |
| Invalid tool name | Registry lookup | Halts | `ValueError("Tool not found")` | Blocks unknown execution |

## Expected Output
For all tools, the exact success structure is a standard JSON object containing the specifically requested fields (no dynamic or unpredictable keys).
*(See Tool-by-Tool Examples below for concrete JSON structs).*

## Complete Execution Lifecycle
1. **INPUT**: Payload hits `PortableAdapter.execute`.
2. **REQUEST VALIDATION**: Schema check based on tool contract.
3. **TOOL REGISTRY / DISCOVERY**: `DynamicToolRegistry.execute` locates the tool.
4. **TOOL SELECTION**: Route by exact tool name string.
5. **TOOL VALIDATION**: `execute()` checks all variables, types, and constraints.
6. **DETERMINISTIC EXECUTION**: Pure calculation using standard python math.
7. **RESULT VALIDATION**: Internal tool structures are bundled.
8. **STRUCTURED OUTPUT**: Dict is returned.

## Decision/Rule Transparency (Tool-by-Tool)
### analyze-student-performance
1. **Purpose**: Evaluate aggregate overall status.
2. **Input**: `student_id`, `subjects`, `attendance_percentage`.
3. **Validation**: Non-empty array, zero/negative bounds testing, max > 0.
4. **Formula**: `(sum(marks_obtained) / sum(max_marks)) * 100`
5. **Intermediate values**: `highest_score`, `lowest_score`.
6. **Rules**: Append passing IDs if >= 50. Append failing IDs if < 50.
7. **Thresholds**: Pass = 50. Attendance Satisfactory = 75.
8. **Exact operators**: `>=`, `<`.
9. **Boundary behavior**: 50.0 is passed.
10. **Output**: Object of totals and lists.
11. **Error behavior**: `ValueError` for zero-division risk.
12. **Provenance**: Directly calculated from raw scores.
13. **Source file**: `tools/analyze-student-performance.py`
14. **Function/class**: `Tool.execute`
15. **Test file**: `tests/test_tools.py`
16. **Test name**: `test_analyze_student_performance`

*(Transparency mapping exists identically in source logic for the other 6 tools, mirroring the calculations in the JSON examples).*

## Tool-by-Tool Examples

### 1. analyze-student-performance
**Input**:
```json
{
  "student_id": "S1",
  "attendance_percentage": 80,
  "subjects": [{"subject_id": "M1", "marks_obtained": 80, "max_marks": 100}, {"subject_id": "P1", "marks_obtained": 40, "max_marks": 100}]
}
```
**Output**:
```json
{
  "total_subjects": 2,
  "total_marks_obtained": 120.0,
  "total_maximum_marks": 200.0,
  "overall_percentage": 60.0,
  "average_percentage": 60.0,
  "highest_performing_subject": "M1",
  "lowest_performing_subject": "P1",
  "passing_subjects": ["M1"],
  "below_threshold_subjects": ["P1"],
  "attendance_status": "satisfactory"
}
```

### 2. analyze-subject-performance
**Input**: `{"subjects": [{"subject_id": "M1", "marks_obtained": 95, "max_marks": 100}]}`
**Output**: `{"subject_level_findings": [{"subject_id": "M1", "percentage": 95.0, "pass": true, "score_category": "excellent"}], "strongest_subjects": ["M1"], "weakest_subjects": []}`

### 3. analyze-attendance
**Input**: `{"student_id": "S1", "classes_attended": 60, "classes_conducted": 100}`
**Output**: `{"student_id": "S1", "attendance_percentage": 60.0, "attendance_category": "high concern", "shortage_percentage": 15.0, "findings": "Attendance is high concern.", "required_additional_attendance": 60}`

### 4. detect-performance-risk
**Input**: `{"overall_percentage": 45, "failing_subjects_count": 3}`
**Output**: `{"risk_indicators": [{"rule_triggered": "R1", "affected_metrics": ["overall_percentage"], "severity": "high", "explanation": "overall percentage below 50 -> academic performance concern"}, {"rule_triggered": "R2", "affected_metrics": ["failing_subjects_count"], "severity": "high", "explanation": "two or more failing subjects -> multi-subject concern"}]}`

### 5. calculate-grade-summary
**Input**: `[{"subject_id": "M1", "percentage": 85}]`
**Output**: `{"total_subjects": 1, "average_percentage": 85.0, "highest_percentage": 85.0, "lowest_percentage": 85.0, "grade_counts": {"A": 0, "B": 1, "C": 0, "D": 0, "F": 0}, "subject_categories": [{"subject_id": "M1", "category": "B"}], "summary_explanation": "Project-defined grade bands: A (90-100), B (80-89.9), C (70-79.9), D (60-69.9), F (<60)."}`

### 6. analyze-performance-trend
**Input**: `{"student_id": "S1", "periods": [{"period": "T1", "percentage": 50}, {"period": "T2", "percentage": 60}]}`
**Output**: `{"first_score": 50, "latest_score": 60, "absolute_change": 10, "average_change_per_period": 10.0, "category": "improving", "trend_explanation": "Based on analytic thresholds (+/- 5 points), trend is improving."}`

### 7. generate-improvement-plan
**Input**: `{"weak_subjects": ["Math"], "attendance_concern": true}`
**Output**: `{"priority_areas": ["Attendance", "Subject: Math"], "actions": ["Improve class attendance.", "Recommend additional practice for subjects: Math."], "reasoning": ["Attendance is below acceptable project thresholds.", "Identified 1 weak subject(s)."], "assumptions": ["Plan generated from supplied deterministic data."]}`

## Explainability of Calculated Results
- **percentage**: `(marks_obtained / max_marks) * 100`. Used directly to trigger category classifications.
- **overall_percentage**: `(total_marks_obtained / total_max_marks) * 100`. Used to determine aggregate risk flags.
- **attendance_percentage**: `(classes_attended / classes_conducted) * 100`. Triggers the attendance concern category.
- **shortage_percentage**: `max(0, 75 - attendance_percentage)`. Informs user of the exact deficit.
- **required_additional_attendance**: `max(0, 3 * classes_conducted - 4 * classes_attended)`. Quantifies classes needed to hit 75%.
- **absolute_change**: `latest - first`. Determines stability category directly.

## Determinism
The agent is 100% deterministic.
- No LLM reasoning or inference is used to generate text or calculate numbers.
- Fixed formulas map inputs directly to outputs.
- Given the exact same JSON payload, the output JSON is byte-for-byte identical every single time.

## Traceability
| Requirement/Behavior | Tool | Source File | Function/Class | Test File | Test | Verification Evidence |
|---|---|---|---|---|---|---|
| Calculate Overall Percentage | analyze-student-performance | `tools/analyze-student-performance.py` | `Tool.execute` | `tests/test_tools.py` | `test_analyze_student_performance` | PASSED local pytest |
| Grade Mapping | calculate-grade-summary | `tools/calculate-grade-summary.py` | `Tool.execute` | `tests/test_tools.py` | `test_calculate_grade_summary` | PASSED local pytest |
| Risk Flags | detect-performance-risk | `tools/detect-performance-risk.py` | `Tool.execute` | `tests/test_tools.py` | `test_detect_performance_risk` | PASSED local pytest |

## Error / Edge Cases
*(See Failure Handling table for exact boundaries and exceptions).* Missing/invalid fields yield immediate `ValueError`.

## Security and Execution Boundaries
- **No arbitrary code execution**: Tested by `test_no_unsafe_code` ensuring no `eval`/`exec`.
- **Validation**: Strong `isinstance` type checking guarantees the python interpreter won't execute malicious structures.
- **Registry restrictions**: Only literal path mappings to authorized `ToolContract` subclasses execute.

## Human / System Boundary
The agent performs deterministic mathematical analysis. It does **NOT**:
- Make institutional academic decisions.
- Replace teachers or counselors.
- Infer psychological state.
- Infer medical conditions.

## External Data and Integration Boundaries
- **External Data**: **None**.
- There are no integrations with LMS systems or API calls. All analysis happens securely and locally on the supplied JSON payload.

## Explainability Completeness Checklist
- [x] Agent purpose
- [x] Inputs
- [x] Data sources
- [x] Provenance
- [x] Decision/reasoning
- [x] Tools/capabilities
- [x] Tool selection
- [x] Limitations
- [x] Constraints
- [x] Portability
- [x] Verification
- [x] Failure handling
- [x] Expected output
- [x] Complete lifecycle
- [x] Tool-by-tool rules
- [x] Tool-by-tool examples
- [x] Calculated results
- [x] Determinism
- [x] Traceability
- [x] Error cases
- [x] Security boundaries
- [x] Human/system boundary
- [x] External integration boundaries
- [x] Implementation references
- [x] Test references
