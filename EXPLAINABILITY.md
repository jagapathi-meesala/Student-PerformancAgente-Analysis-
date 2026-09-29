# Explainability

## Agent Purpose
The exact purpose of the Student Performance Analysis Agent is to perform deterministic, rule-based analysis of structured academic records provided by a user. Its intended use is to generate metrics, flags, and rule-based suggestions from standard numerical data. 
- **Supported analytical operations**: Grade aggregation, subject bucketing, attendance checking, risk flagging, trend analysis, and static improvement plan mapping.
- **What it does NOT do**: It does not alter university records or generate dynamic narrative feedback.
- **LLM usage**: It does **NOT** use an LLM for any core analytical operations.
- **External retrieval**: It does **NOT** retrieve external student information; all data must be supplied in the payload.
- **Institutional limits**: It does **NOT** make institutional decisions, provide medical/psychological conclusions, or perform predictive modeling beyond its deterministic bounds.

## Inputs
| Tool | Input | Required | Type | Constraints | Source |
|---|---|---|---|---|---|
| analyze-student-performance | student_id | Yes | string | N/A | User |
| analyze-student-performance | student_name | No | string | N/A | User |
| analyze-student-performance | subjects | Yes | array | Non-empty, unique subject_id | User |
| analyze-student-performance | subjects[].marks_obtained | Yes | number | >= 0, <= max_marks | User |
| analyze-student-performance | subjects[].max_marks | Yes | number | > 0 | User |
| analyze-student-performance | attendance_percentage | No | number | 0 - 100 | User |
| analyze-subject-performance | subjects | Yes | array | Requires required fields per item | User |
| analyze-attendance | student_id | Yes | string | N/A | User |
| analyze-attendance | attendance_percentage | Conditional | number | 0 - 100 | User |
| analyze-attendance | classes_attended | Conditional | integer | >= 0, <= conducted | User |
| analyze-attendance | classes_conducted | Conditional | integer | > 0 | User |
| detect-performance-risk | overall_percentage | No | number | 0 - 100 | User |
| detect-performance-risk | attendance_percentage | No | number | 0 - 100 | User |
| detect-performance-risk | failing_subjects_count | No | integer | >= 0 | User |
| detect-performance-risk | recent_performance_change | No | number | Numeric | User |
| calculate-grade-summary | array or subjects array | Yes | array | Non-empty | User |
| analyze-performance-trend | student_id | Yes | string | N/A | User |
| analyze-performance-trend | periods | Yes | array | Min 2, unique periods | User |
| generate-improvement-plan | weak_subjects | No | array(str) | Strings | User |
| generate-improvement-plan | attendance_concern | No | boolean | True/False | User |
| generate-improvement-plan | declining_trend | No | boolean | True/False | User |
| generate-improvement-plan | low_overall_percentage | No | boolean | True/False | User |

## Decision
The agent reaches classification completely deterministically through a sequential pipeline for each node:
`INPUT` ↓ `VALIDATION` ↓ `CALCULATION` ↓ `THRESHOLD/RULE` ↓ `CLASSIFICATION` ↓ `OUTPUT`

- **Operators**: Standard exact operators (`>`, `>=`, `<`, `<=`, `==`).
- **Thresholds**: Defined explicitly in the code. Hitting a boundary behaves strictly according to the mathematical operator (e.g. `>= 50` includes `50.0`).
- **Precedence**: Evaluated chronologically in code; `if/elif/else` blocks are mutually exclusive and evaluated top-down.
- **Rule Chaining**: Rules within tools are evaluated independently (e.g. failing_subjects logic is completely separate from overall_percentage logic in `detect-performance-risk`). Tools themselves are executed completely independently, meaning the user must chain outputs to inputs manually.

## Limits
- **Supplied structured data only**: Analyzes only the JSON payload it receives.
- **No hidden student information**: Assumes zero prior knowledge.
- **No external database**: Does not make network calls to LMS or SIS platforms.
- **No LLM reasoning**: Outputs are strict rule mappings, not generated text.
- **Project-defined thresholds**: Grade boundaries (A=90, B=80, etc.) are standard templates, not mapped to specific institutional rules.
- **Missing Data Limitations**: Required inputs missing will explicitly crash the tool logic (raising ValueError) to fail safely.

## Output Contract
| Tool | Output Field | Type | Meaning | Derived From |
|---|---|---|---|---|
| analyze-student-performance | total_subjects | integer | Count of subjects | subjects input |
| analyze-student-performance | total_marks_obtained | number | Sum of obtained | subjects input |
| analyze-student-performance | total_maximum_marks | number | Sum of maximums | subjects input |
| analyze-student-performance | overall_percentage | number | total_obtained / total_max * 100 | subjects input |
| analyze-student-performance | passing_subjects | array | List of passing subject IDs | subjects input |
| analyze-subject-performance | subject_level_findings | array | Detailed category breakdown | subjects input |
| analyze-attendance | shortage_percentage | number | Distance below 75% | percentage derived/input |
| analyze-attendance | required_additional_attendance| integer | Classes needed to hit 75% | classes input |
| detect-performance-risk | risk_indicators | array | Flags triggered by rules | inputs |
| calculate-grade-summary | grade_counts | object | Count of A,B,C,D,F | inputs |
| analyze-performance-trend | absolute_change | number | latest - first | periods input |
| generate-improvement-plan | actions | array | String action recommendations | boolean inputs |

## Complete Execution Lifecycle
1. **INPUT**: User supplies JSON data to the Adapter layer.
2. **TOOL DISCOVERY**: The `AgentCore` dynamically loads python modules from the `tools/` directory and instantiates them via `DynamicToolRegistry`.
3. **TOOL SELECTION**: `AgentCore.execute_tool` routes the payload by the strict `tool_name`.
4. **DETERMINISTIC EXECUTION**: The tool's `.execute(input)` method runs standard Python math/logic.
5. **RESULT VALIDATION**: Internal tool types strictly map data before returning.
6. **STRUCTURED OUTPUT**: A JSON-serializable `Dict` is wrapped in a success payload and returned.

| Lifecycle Stage | Implementation | Responsibility |
|---|---|---|
| Request Translation | `PortableAdapter.execute` (`adapters/portable_adapter.py`) | Neutral API border |
| Discovery/Routing | `DynamicToolRegistry.execute` (`core/registry.py`) | Route payload securely |
| Deterministic Execution| `Tool.execute` (`tools/*.py`) | Pure calculation and validation |

*(Note: The tools are independent. Automatic chaining does not exist in the core framework).*

## Decision/Rule Transparency (Tool-by-Tool) & Tool-by-Tool Examples

### analyze-student-performance
1. **Purpose**: Evaluate aggregate overall status.
2. **Input**: `student_id`, `subjects`, `attendance_percentage`.
3. **Validation**: Non-empty array, zero/negative bounds testing, max > 0.
4. **Formula**: `(sum(marks_obtained) / sum(max_marks)) * 100`
5. **Intermediate values**: `highest_score`, `lowest_score`.
6. **Rules**: Append passing IDs if >= 50. Append failing IDs if < 50.
7. **Thresholds**: Pass = 50. Attendance Satisfactory = 75.
8. **Exact operators**: `>= 50`, `< 50`.
9. **Boundary behavior**: 50.0 is passed.
10. **Output**: Object of totals and lists.
11. **Error behavior**: `ValueError` for zero-division risk (max_marks=0).
12. **Provenance**: Directly calculated from raw scores.
13. **Source file**: `tools/analyze-student-performance.py`
14. **Function/class**: `Tool.execute`
15. **Test file**: `tests/test_tools.py`
16. **Test name**: `test_analyze_student_performance`
17. **Concrete JSON input**: `{"student_id": "S1", "subjects": [{"subject_id": "M1", "marks_obtained": 80, "max_marks": 100}, {"subject_id": "P1", "marks_obtained": 40, "max_marks": 100}], "attendance_percentage": 80}`
18. **Concrete JSON output**: `{"total_subjects": 2, "total_marks_obtained": 120.0, "total_maximum_marks": 200.0, "overall_percentage": 60.0, "average_percentage": 60.0, "highest_performing_subject": "M1", "lowest_performing_subject": "P1", "passing_subjects": ["M1"], "below_threshold_subjects": ["P1"], "attendance_status": "satisfactory"}`

### analyze-subject-performance
1. **Purpose**: Assign descriptive bands to subject scores.
2. **Input**: `subjects` array.
3. **Validation**: `marks_obtained <= max_marks`, no missing keys.
4. **Formula**: `(marks_obtained / max_marks) * 100`
5. **Intermediate values**: Computed percentage per subject.
6. **Rules**: If-elif chain mapping percentage to word bands.
7. **Thresholds**: >= 90 (excellent), >= 75 (strong), >= 60 (satisfactory), >= 40 (needs improvement), < 40 (critical).
8. **Exact operators**: `>=`, `<`
9. **Boundary behavior**: Exactly 90 is excellent.
10. **Output**: Arrays of strongest/weakest and list of findings.
11. **Error behavior**: Missing keys raise `ValueError`.
12. **Provenance**: Derived from per-subject raw scores.
13. **Source file**: `tools/analyze-subject-performance.py`
14. **Function/class**: `Tool.execute`
15. **Test file**: `tests/test_tools.py`
16. **Test name**: `test_analyze_subject_performance`
17. **Concrete JSON input**: `{"subjects": [{"subject_id": "M1", "marks_obtained": 95, "max_marks": 100}]}`
18. **Concrete JSON output**: `{"subject_level_findings": [{"subject_id": "M1", "percentage": 95.0, "pass": true, "score_category": "excellent"}], "strongest_subjects": ["M1"], "weakest_subjects": []}`

### analyze-attendance
1. **Purpose**: Classify attendance health.
2. **Input**: `student_id`, `classes_attended`, `classes_conducted`.
3. **Validation**: `classes_conducted > 0`, `attended <= conducted`.
4. **Formula**: `(attended / conducted) * 100`. Shortage = `75 - pct`. Added = `3*conducted - 4*attended`.
5. **Intermediate values**: `attendance_percentage`
6. **Rules**: If-elif mapping.
7. **Thresholds**: >=90 (strong), >=75 (acceptable), >=65 (concern), <65 (high concern).
8. **Exact operators**: `>= 75`, etc.
9. **Boundary behavior**: Shortage is max bounded at 0.
10. **Output**: Metrics and required additional classes.
11. **Error behavior**: Zero classes conducted raises `ValueError`.
12. **Provenance**: Derived from raw class counts.
13. **Source file**: `tools/analyze-attendance.py`
14. **Function/class**: `Tool.execute`
15. **Test file**: `tests/test_tools.py`
16. **Test name**: `test_analyze_attendance`
17. **Concrete JSON input**: `{"student_id": "S1", "classes_attended": 60, "classes_conducted": 100}`
18. **Concrete JSON output**: `{"student_id": "S1", "attendance_percentage": 60.0, "attendance_category": "high concern", "shortage_percentage": 15.0, "findings": "Attendance is high concern.", "required_additional_attendance": 60}`

### detect-performance-risk
1. **Purpose**: Flag analytical risk indicators.
2. **Input**: `overall_percentage`, `attendance_percentage`, `failing_subjects_count`, `recent_performance_change`.
3. **Validation**: percentages 0-100, counts >= 0.
4. **Formula**: N/A (Boolean comparisons).
5. **Intermediate values**: Evaluated boolean expressions.
6. **Rules**: Append indicator object if threshold met.
7. **Thresholds**: overall < 50, failing >= 2, attendance < 75, change <= -10.
8. **Exact operators**: `<`, `>=`, `<=`
9. **Boundary behavior**: A drop of exactly 10 points (`-10.0`) triggers risk.
10. **Output**: Array of `risk_indicators`.
11. **Error behavior**: Invalid range (e.g. percentage=110) raises `ValueError`.
12. **Provenance**: Directly comparing aggregate inputs.
13. **Source file**: `tools/detect-performance-risk.py`
14. **Function/class**: `Tool.execute`
15. **Test file**: `tests/test_tools.py`
16. **Test name**: `test_detect_performance_risk`
17. **Concrete JSON input**: `{"overall_percentage": 45, "failing_subjects_count": 3}`
18. **Concrete JSON output**: `{"risk_indicators": [{"rule_triggered": "R1", "affected_metrics": ["overall_percentage"], "severity": "high", "explanation": "overall percentage below 50 -> academic performance concern"}, {"rule_triggered": "R2", "affected_metrics": ["failing_subjects_count"], "severity": "high", "explanation": "two or more failing subjects -> multi-subject concern"}]}`

### calculate-grade-summary
1. **Purpose**: Generate letter grade histogram.
2. **Input**: `subjects` array containing `percentage`.
3. **Validation**: percentages 0-100.
4. **Formula**: average = `sum(pct) / count`.
5. **Intermediate values**: `total`, `highest`, `lowest`.
6. **Rules**: Map pct to A,B,C,D,F keys in a dictionary.
7. **Thresholds**: A (>=90), B (>=80), C (>=70), D (>=60), F (<60).
8. **Exact operators**: `>=`
9. **Boundary behavior**: Exactly 90.0 is an A.
10. **Output**: Grade counts dictionary, averages.
11. **Error behavior**: Empty array raises `ValueError` (div by zero).
12. **Provenance**: Aggregating raw percentage inputs.
13. **Source file**: `tools/calculate-grade-summary.py`
14. **Function/class**: `Tool.execute`
15. **Test file**: `tests/test_tools.py`
16. **Test name**: `test_calculate_grade_summary`
17. **Concrete JSON input**: `[{"subject_id": "M1", "percentage": 85}]`
18. **Concrete JSON output**: `{"total_subjects": 1, "average_percentage": 85.0, "highest_percentage": 85.0, "lowest_percentage": 85.0, "grade_counts": {"A": 0, "B": 1, "C": 0, "D": 0, "F": 0}, "subject_categories": [{"subject_id": "M1", "category": "B"}], "summary_explanation": "Project-defined grade bands: A (90-100), B (80-89.9), C (70-79.9), D (60-69.9), F (<60)."}`

### analyze-performance-trend
1. **Purpose**: Track direction over periods.
2. **Input**: `student_id`, `periods` (period, percentage).
3. **Validation**: Minimum length 2, no duplicates.
4. **Formula**: `absolute_change = latest - first`, `avg_change = absolute / (len - 1)`
5. **Intermediate values**: array of extracted scores.
6. **Rules**: `improving` if change >= 5. `declining` if <= -5.
7. **Thresholds**: 5, -5.
8. **Exact operators**: `>=`, `<=`
9. **Boundary behavior**: Exactly 5.0 is improving. 4.9 is stable.
10. **Output**: Change metrics and category.
11. **Error behavior**: `< 2` periods raises `ValueError`.
12. **Provenance**: Computed chronologically from supplied array boundaries.
13. **Source file**: `tools/analyze-performance-trend.py`
14. **Function/class**: `Tool.execute`
15. **Test file**: `tests/test_tools.py`
16. **Test name**: `test_analyze_performance_trend`
17. **Concrete JSON input**: `{"student_id": "S1", "periods": [{"period": "T1", "percentage": 50}, {"period": "T2", "percentage": 60}]}`
18. **Concrete JSON output**: `{"first_score": 50, "latest_score": 60, "absolute_change": 10, "average_change_per_period": 10.0, "category": "improving", "trend_explanation": "Based on analytic thresholds (+/- 5 points), trend is improving."}`

### generate-improvement-plan
1. **Purpose**: Map boolean risk flags to string actions.
2. **Input**: `weak_subjects`, `attendance_concern`, `declining_trend`, `low_overall_percentage`.
3. **Validation**: Boolean/list typing.
4. **Formula**: None.
5. **Intermediate values**: Arrays built via `.append()`.
6. **Rules**: Append specific string if boolean is True.
7. **Thresholds**: N/A
8. **Exact operators**: `if x:`
9. **Boundary behavior**: Defaults to Maintenance plan if array remains empty.
10. **Output**: Arrays of strings.
11. **Error behavior**: Missing keys default to `False`.
12. **Provenance**: Hardcoded text mapped to user boolean flags.
13. **Source file**: `tools/generate-improvement-plan.py`
14. **Function/class**: `Tool.execute`
15. **Test file**: `tests/test_tools.py`
16. **Test name**: `test_generate_improvement_plan`
17. **Concrete JSON input**: `{"weak_subjects": ["Math"], "attendance_concern": true}`
18. **Concrete JSON output**: `{"priority_areas": ["Attendance", "Subject: Math"], "actions": ["Improve class attendance.", "Recommend additional practice for subjects: Math."], "reasoning": ["Attendance is below acceptable project thresholds.", "Identified 1 weak subject(s)."], "assumptions": ["Plan generated from supplied deterministic data."]}`

## Explainability of Calculated Results
- **Percentage**: `(marks_obtained / max_marks) * 100`. Defines passing threshold and category mapping.
- **Overall Percentage**: `(total_marks_obtained / total_max_marks) * 100`. Used to trigger `R1` overall academic risk.
- **Attendance Percentage**: `(classes_attended / classes_conducted) * 100`. Triggers attendance concern category.
- **Shortage Percentage**: `max(0, 75 - attendance_percentage)`. Informs user how far below minimum threshold they are.
- **Required Additional Attendance**: `max(0, 3 * classes_conducted - 4 * classes_attended)`. Quantifies exactly how many classes are needed to hit a 75% mathematical average.
- **Absolute Trend Change**: `latest - first`. Determines stability category directly.

## Provenance
### User-Supplied Data
`marks_obtained`, `max_marks`, `classes_conducted`, `classes_attended`, `overall_percentage` (for risk detection input).
### Derived Data
`percentage`, `shortage_percentage`, string categories, and string arrays for actions.
### Static Rules
Grade Boundaries (A=90), Risk Thresholds (R1=50%), Trend thresholds (+/-5 points).
### External Data
External data: None.

## Determinism
The agent is entirely deterministic.
- **No LLM reasoning**: Logic uses standard Python operators.
- **No random sampling**: No stochastic modeling or variable seeds.
- **Fixed formulas/thresholds**: 90 is always an A.
- **Fixed outputs**: Identical inputs yield byte-for-byte identical output JSONs every single time. There are no exceptions in the codebase.

## Traceability
| Requirement/Behavior | Tool | Source File | Function/Class | Test File | Test |
|---|---|---|---|---|---|
| Calculate Overall Percentage | analyze-student-performance | `tools/analyze-student-performance.py` | `Tool.execute` | `tests/test_tools.py` | `test_analyze_student_performance` |
| Grade Mapping | calculate-grade-summary | `tools/calculate-grade-summary.py` | `Tool.execute` | `tests/test_tools.py` | `test_calculate_grade_summary` |
| Risk Flags | detect-performance-risk | `tools/detect-performance-risk.py` | `Tool.execute` | `tests/test_tools.py` | `test_detect_performance_risk` |
| Trend Thresholding | analyze-performance-trend | `tools/analyze-performance-trend.py` | `Tool.execute` | `tests/test_tools.py` | `test_analyze_performance_trend` |

## Error/Edge Cases
| Case | Tool | Actual Behavior | Error Type/Output |
|---|---|---|---|
| Missing required fields | All tools | Validates and halts before calculation | Raises `ValueError` |
| Duplicate subjects/periods | analyze-student-performance, analyze-performance-trend | Set checking catches duplicates | Raises `ValueError` |
| Zero denominators | analyze-student-performance, analyze-attendance | Checks `max_marks > 0` and `conducted > 0` | Raises `ValueError` |
| Empty arrays | calculate-grade-summary | Checked explicitly | Raises `ValueError` |
| Negative values | All tools | Range bounding | Raises `ValueError` |
| Marks > Max | analyze-student-performance | Bounds check `marks <= max_marks` | Raises `ValueError` |

## Security and Execution Boundaries
- **Validation**: Strict type checks (`isinstance`) guard against object injection.
- **No `eval`/`exec`**: Tests specifically verify the complete absence of unsafe parsers (`test_no_unsafe_code`).
- **No Arbitrary Shell/Code Execution**: Fully sandboxed.
- **Configuration Boundaries**: Adapter registry intercepts payloads dynamically; tools never touch the OS filesystem or environment directly.

## Human/System Boundary
The agent performs deterministic mathematical analysis. It does **NOT**:
- Make institutional academic decisions.
- Replace teachers or counselors.
- Infer psychological state.
- Infer medical conditions.
- Access hidden student records.
- Claim official academic policy.

The boundary is strict: **INPUT DATA → AGENT ANALYSIS → STRUCTURED RESULT**.

## Verification Evidence
- **pytest result**: PASSED (Local unit tests validating deterministic execution and security).
- **readiness audit result**: PASSED (Local file and secret scan).
- **OpenGAP validation result**: Validation passed (0 warnings) (Manifest strictly tested against OpenGAP schema).

## Explainability Completeness Checklist
- [x] Agent purpose documented
- [x] Inputs documented
- [x] Decisions documented
- [x] Limits documented
- [x] Output contract documented
- [x] Complete execution lifecycle documented
- [x] All seven tools documented
- [x] Tool-by-tool rules documented
- [x] Tool-by-tool JSON examples documented
- [x] Calculated results explained
- [x] Provenance documented
- [x] Determinism documented
- [x] Traceability documented
- [x] Error/edge cases documented
- [x] Security boundaries documented
- [x] Human/system boundary documented
- [x] Verification evidence documented
- [x] Implementation references documented
- [x] Test references documented
- [x] No unsupported behavior claimed
