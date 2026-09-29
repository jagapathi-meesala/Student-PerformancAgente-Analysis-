# Explainability

## 1. PURPOSE AND EXPLAINABILITY SCOPE

This document provides a rigorous, evaluator-facing explanation of the logic, data handling, and decision-making parameters of the Student Performance Analysis Agent. 

### Scope and Operating Principles
- **Deterministic Operation**: The agent operates completely deterministically. 
- **No LLM Reasoning**: No LLM-generated reasoning, probabilistic evaluation, or free-text inference is used within the seven analytical tools. 
- **Data Dependency**: All outputs are strictly derived from supplied structured JSON inputs combined with static, deterministic mathematical formulas and hardcoded threshold rules.
- **Analytical Parameters**: The thresholds (e.g., passing grades, risk boundaries) are project-defined analytical parameters and do **not** represent official institutional policy.
- **Agent Limitations**:
  - The agent does **NOT** know real-world student identities.
  - The agent does **NOT** infer subjective context, medical histories, or psychological conditions.
  - The agent does **NOT** extrapolate missing data; if required data is absent, the tool will safely fail.
  - The agent does **NOT** fetch or retrieve external data. Unless explicitly implemented as an integration, all calculations are performed exclusively on the provided input payload.

### Data Distinction
A. **User-Supplied Data**: The raw numerical marks, attendance counts, subject IDs, and boolean flags provided directly in the input payload.
B. **Deterministically Derived Values**: Percentages, sums, averages, and string classifications computed strictly via mathematical formulas or threshold conditions.
C. **Static Analytical Rules/Thresholds**: Hardcoded logic blocks specifying the exact cut-offs for grade bands, risk flags, and improvement categories.
D. **External Data**: **None**. The current implementation strictly operates without external data retrieval.

---

## 2. DATA PROVENANCE MAP

| Data Element | Origin | User Supplied? | Derived? | Transformation | Used By | Output |
| --- | --- | --- | --- | --- | --- | --- |
| `student_id` | Input payload | Yes | No | None | All tools | Passed through to output |
| `marks_obtained` | Input payload | Yes | No | None | analyze-student-performance, analyze-subject-performance | Math operations |
| `max_marks` | Input payload | Yes | No | None | analyze-student-performance, analyze-subject-performance | Math operations |
| `classes_attended` / `classes_conducted` | Input payload | Yes | No | None | analyze-attendance | Converted to percentage |
| `percentage` | Formula | No | Yes | `(marks / max) * 100` | calculate-grade-summary | Output metric |
| `overall_percentage` | Formula | No | Yes | `(total_marks / total_max) * 100` | detect-performance-risk | Output metric |
| `score_category` / `attendance_category` | Static Rule | No | Yes | `if >= Threshold -> Category` | analyze-subject-performance, analyze-attendance | Output category |
| `risk_indicators` | Static Rule | No | Yes | Boolean match against conditions | detect-performance-risk | Array of risk objects |
| `actions` / `priority_areas` | Static Rule | No | Yes | Map true/false flags to static text | generate-improvement-plan | Array of strings |
| **External API Data** | N/A | No | No | N/A | N/A | **None** |

---

## 3. TOOL-BY-TOOL EXPLAINABILITY

### 1. analyze-student-performance
**A. Purpose**: Analyze a student's overall academic performance and find aggregate metrics.
**B. Input Schema**: Object requiring `student_id` (str) and `subjects` (array of objects with `subject_id`, `marks_obtained`, `max_marks`). Optional: `attendance_percentage` (num).
**C. Output Schema**: Object containing `total_subjects`, `total_marks_obtained`, `total_maximum_marks`, `overall_percentage`, `average_percentage`, `highest_performing_subject`, `lowest_performing_subject`, `passing_subjects`, `below_threshold_subjects`, and optionally `attendance_status`.
**D. Validation Rules**: Subjects must be a list. Marks must be numeric. `marks_obtained` >= 0. `max_marks` > 0. `marks_obtained` <= `max_marks`. Duplicate `subject_id` is rejected.
**E. Calculation/Formula**: 
- `percentage` = `(marks_obtained / max_marks) * 100`
- `overall_percentage` = `(total_marks_obtained / total_max_marks) * 100`
**F. Decision Rules**: Subjects are categorized as passing or below threshold based on individual percentage.
**G. Thresholds**: 
- Pass: `percentage >= 50`
- Attendance Satisfactory: `attendance_percentage >= 75`
**H. Boundary Conditions**: `total_max_marks = 0` handled to prevent division by zero. Empty subjects list results in zero values.
**I. Missing/Invalid Input Behavior**: Raises `ValueError` for missing required fields, non-numeric marks, or out-of-bounds percentages.
**J. Data Provenance**: Derived strictly from user-supplied `subjects` array.
**K. Traceability Path**: `Tool.execute` in `analyze-student-performance.py`.
**N. Source-code reference**: `tools/analyze-student-performance.py`
**O. Test reference**: `test_analyze_student_performance` in `tests/test_tools.py`

### 2. analyze-subject-performance
**A. Purpose**: Evaluate individual subject scores and assign categories.
**B. Input Schema**: Object requiring `subjects` (array of objects with `subject_id`, `marks_obtained`, `max_marks`).
**C. Output Schema**: Object containing `subject_level_findings`, `strongest_subjects`, and `weakest_subjects`.
**D. Validation Rules**: Required fields must exist per subject. Marks must be numeric, `>= 0`, and `obtained <= max`.
**E. Calculation/Formula**: `percentage` = `(marks_obtained / max_marks) * 100`
**F. Decision Rules**: Assigns categories and strong/weak lists.
**G. Thresholds**: 
- `excellent`: >= 90
- `strong`: >= 75
- `satisfactory`: >= 60
- `needs improvement`: >= 40
- `critical improvement`: < 40
- `pass`: >= 40
- `strongest_subjects` list: >= 75
- `weakest_subjects` list: < 60
**H. Boundary Conditions**: Exactly hitting the boundary includes it in the higher bracket (e.g. 75.0 is `strong`).
**I. Missing/Invalid Input Behavior**: Raises `ValueError` for invalid ranges or missing data.
**J. Data Provenance**: Derived strictly from user-supplied `subjects` input.
**K. Traceability Path**: `Tool.execute` in `analyze-subject-performance.py`.
**N. Source-code reference**: `tools/analyze-subject-performance.py`
**O. Test reference**: `test_analyze_subject_performance` in `tests/test_tools.py`

### 3. analyze-attendance
**A. Purpose**: Compute attendance metrics and required classes to meet thresholds.
**B. Input Schema**: Object requiring `student_id`. Requires either `attendance_percentage` OR both `classes_attended` and `classes_conducted`.
**C. Output Schema**: Object containing `student_id`, `attendance_percentage`, `attendance_category`, `shortage_percentage`, `findings`, and `required_additional_attendance` (if applicable).
**D. Validation Rules**: Counts must be numeric, `>= 0`, conducted > 0, attended <= conducted. Percentage must be 0-100.
**E. Calculation/Formula**: 
- `attendance_percentage` = `(attended / conducted) * 100`
- `shortage_percentage` = `max(0, 75 - percentage)`
- `required_additional` = `max(0, 3 * conducted - 4 * attended)`
**F. Decision Rules**: Maps attendance percentage to severity categories.
**G. Thresholds**:
- `strong attendance`: >= 90
- `acceptable`: >= 75
- `attendance concern`: >= 65
- `high concern`: < 65
**H. Boundary Conditions**: If shortage is calculated but attendance is above 75%, shortage is 0.
**I. Missing/Invalid Input Behavior**: Raises `ValueError` if neither percentage nor class counts are provided, or if counts are invalid.
**J. Data Provenance**: Derived from user-supplied attendance inputs.
**K. Traceability Path**: `Tool.execute` in `analyze-attendance.py`.
**N. Source-code reference**: `tools/analyze-attendance.py`
**O. Test reference**: `test_analyze_attendance` in `tests/test_tools.py`

### 4. detect-performance-risk
**A. Purpose**: Flag specific risk conditions based on hardcoded rules.
**B. Input Schema**: Object containing optional `overall_percentage`, `attendance_percentage`, `failing_subjects_count`, `recent_performance_change`.
**C. Output Schema**: Object containing `risk_indicators` (array).
**D. Validation Rules**: Numeric type checking, percentages bounded 0-100, counts >= 0.
**E. Calculation/Formula**: None (purely boolean/threshold evaluations).
**F. Decision Rules**: If a metric hits a threshold, a static risk object is appended to the array.
**G. Thresholds**:
- R1: `overall_percentage < 50`
- R2: `failing_subjects_count >= 2`
- R3: `attendance_percentage < 75`
- R4: `recent_performance_change <= -10`
**H. Boundary Conditions**: Values exactly matching the boundary (e.g., `< 50`) behave explicitly as defined (50 is not flagged).
**I. Missing/Invalid Input Behavior**: Optional inputs are safely skipped if absent. Invalid types raise `ValueError`.
**J. Data Provenance**: Derived from user-supplied summary metrics.
**K. Traceability Path**: `Tool.execute` in `detect-performance-risk.py`.
**N. Source-code reference**: `tools/detect-performance-risk.py`
**O. Test reference**: `test_detect_performance_risk` in `tests/test_tools.py`

### 5. calculate-grade-summary
**A. Purpose**: Group subject percentages into letter grade distributions.
**B. Input Schema**: Array of objects with `subject_id`, `percentage` (or dict wrapping this array).
**C. Output Schema**: Object containing `total_subjects`, `average_percentage`, `highest_percentage`, `lowest_percentage`, `grade_counts`, `subject_categories`.
**D. Validation Rules**: List cannot be empty. Percentages must be numeric, 0-100.
**E. Calculation/Formula**: Math averages derived from iterating the provided list.
**F. Decision Rules**: Maps percentages to grade buckets.
**G. Thresholds**:
- A: >= 90
- B: >= 80
- C: >= 70
- D: >= 60
- F: < 60
**H. Boundary Conditions**: Highest/lowest initialized to extreme bounds (-1.0, 101.0).
**I. Missing/Invalid Input Behavior**: Raises `ValueError` if array is empty or schema malformed.
**J. Data Provenance**: Derived directly from user-supplied subject percentages.
**K. Traceability Path**: `Tool.execute` in `calculate-grade-summary.py`.
**N. Source-code reference**: `tools/calculate-grade-summary.py`
**O. Test reference**: `test_calculate_grade_summary` in `tests/test_tools.py`

### 6. analyze-performance-trend
**A. Purpose**: Identify trajectory direction over multiple time periods.
**B. Input Schema**: Object requiring `student_id` and `periods` (array of `period`, `percentage`).
**C. Output Schema**: Object containing `first_score`, `latest_score`, `absolute_change`, `average_change_per_period`, `category`, `trend_explanation`.
**D. Validation Rules**: Requires at least 2 periods. Periods cannot be duplicates. Percentages must be 0-100.
**E. Calculation/Formula**: 
- `absolute_change` = `latest_score - first_score`
- `average_change_per_period` = `absolute_change / (len(periods) - 1)`
**F. Decision Rules**: Maps the absolute change to a descriptive category.
**G. Thresholds**:
- `improving`: >= 5
- `declining`: <= -5
- `relatively stable`: between -4.99 and 4.99
**H. Boundary Conditions**: Assumes array order represents chronological sequence.
**I. Missing/Invalid Input Behavior**: Raises `ValueError` for < 2 periods or duplicates.
**J. Data Provenance**: Derived from user-supplied historical periods.
**K. Traceability Path**: `Tool.execute` in `analyze-performance-trend.py`.
**N. Source-code reference**: `tools/analyze-performance-trend.py`
**O. Test reference**: `test_analyze_performance_trend` in `tests/test_tools.py`

### 7. generate-improvement-plan
**A. Purpose**: Provide structured recommendations based strictly on deterministic risk flags.
**B. Input Schema**: Object containing optional boolean/array flags: `weak_subjects`, `attendance_concern`, `declining_trend`, `low_overall_percentage`.
**C. Output Schema**: Object containing `priority_areas`, `actions`, `reasoning`, `assumptions`.
**D. Validation Rules**: `weak_subjects` must be a list if provided.
**E. Calculation/Formula**: N/A (boolean logic).
**F. Decision Rules**: For each flag evaluated as `True`, predetermined text strings are appended to the arrays. If no flags are true, a default "Maintenance" action is returned.
**G. Thresholds**: N/A
**H. Boundary Conditions**: None.
**I. Missing/Invalid Input Behavior**: Missing fields default to `False` safely.
**J. Data Provenance**: Hardcoded strings triggered by user-supplied boolean parameters.
**K. Traceability Path**: `Tool.execute` in `generate-improvement-plan.py`.
**N. Source-code reference**: `tools/generate-improvement-plan.py`
**O. Test reference**: `test_generate_improvement_plan` in `tests/test_tools.py`

---

## 4. CONCRETE JSON I/O EXAMPLES

### Example: analyze-student-performance
Input:
```json
{
  "student_id": "S1",
  "attendance_percentage": 80,
  "subjects": [
    {"subject_id": "M1", "marks_obtained": 80, "max_marks": 100},
    {"subject_id": "P1", "marks_obtained": 40, "max_marks": 100}
  ]
}
```
Output:
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

### Example: analyze-subject-performance
Input:
```json
{
  "subjects": [
    {"subject_id": "M1", "marks_obtained": 95, "max_marks": 100}
  ]
}
```
Output:
```json
{
  "subject_level_findings": [
    {
      "subject_id": "M1",
      "percentage": 95.0,
      "pass": true,
      "score_category": "excellent"
    }
  ],
  "strongest_subjects": ["M1"],
  "weakest_subjects": []
}
```

### Example: analyze-attendance
Input:
```json
{
  "student_id": "S1",
  "classes_attended": 60,
  "classes_conducted": 100
}
```
Output:
```json
{
  "student_id": "S1",
  "attendance_percentage": 60.0,
  "attendance_category": "high concern",
  "shortage_percentage": 15.0,
  "findings": "Attendance is high concern.",
  "required_additional_attendance": 60
}
```

### Example: detect-performance-risk
Input:
```json
{
  "overall_percentage": 45,
  "failing_subjects_count": 3
}
```
Output:
```json
{
  "risk_indicators": [
    {
      "rule_triggered": "R1",
      "affected_metrics": ["overall_percentage"],
      "severity": "high",
      "explanation": "overall percentage below 50 -> academic performance concern"
    },
    {
      "rule_triggered": "R2",
      "affected_metrics": ["failing_subjects_count"],
      "severity": "high",
      "explanation": "two or more failing subjects -> multi-subject concern"
    }
  ]
}
```

### Example: calculate-grade-summary
Input:
```json
[
  {"subject_id": "M1", "percentage": 85}
]
```
Output:
```json
{
  "total_subjects": 1,
  "average_percentage": 85.0,
  "highest_percentage": 85.0,
  "lowest_percentage": 85.0,
  "grade_counts": {
    "A": 0, "B": 1, "C": 0, "D": 0, "F": 0
  },
  "subject_categories": [
    {"subject_id": "M1", "category": "B"}
  ],
  "summary_explanation": "Project-defined grade bands: A (90-100), B (80-89.9), C (70-79.9), D (60-69.9), F (<60)."
}
```

### Example: analyze-performance-trend
Input:
```json
{
  "student_id": "S1",
  "periods": [
    {"period": "T1", "percentage": 50},
    {"period": "T2", "percentage": 60}
  ]
}
```
Output:
```json
{
  "first_score": 50,
  "latest_score": 60,
  "absolute_change": 10,
  "average_change_per_period": 10.0,
  "category": "improving",
  "trend_explanation": "Based on analytic thresholds (+/- 5 points), trend is improving."
}
```

### Example: generate-improvement-plan
Input:
```json
{
  "weak_subjects": ["Math"],
  "attendance_concern": true
}
```
Output:
```json
{
  "priority_areas": [
    "Attendance",
    "Subject: Math"
  ],
  "actions": [
    "Improve class attendance.",
    "Recommend additional practice for subjects: Math."
  ],
  "reasoning": [
    "Attendance is below acceptable project thresholds.",
    "Identified 1 weak subject(s)."
  ],
  "assumptions": [
    "Plan generated from supplied deterministic data."
  ]
}
```
