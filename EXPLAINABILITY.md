# Explainability

This document details the deterministic rules, formulas, and thresholds used by the Student Performance Analysis Agent.

**Important Note:** The agent analyzes ONLY supplied structured data and does not provide real-time institutional student information unless an external data integration is separately implemented. All thresholds are project-defined analytical parameters, not institutional policy.

## 1. analyze-student-performance
- **Purpose**: Calculate overall academic status.
- **Formulas**: 
  - `percentage = (marks_obtained / max_marks) * 100`
  - `overall_percentage = (total_marks_obtained / total_max_marks) * 100`
- **Thresholds**: 50% is considered the minimum passing threshold for individual subjects.

## 2. analyze-subject-performance
- **Purpose**: Categorize specific subject scores.
- **Formulas**: `percentage = (marks_obtained / max_marks) * 100`
- **Thresholds**: 
  - `>= 90`: Excellent
  - `75 - 89.9`: Strong
  - `60 - 74.9`: Satisfactory
  - `40 - 59.9`: Needs Improvement
  - `< 40`: Critical Improvement

## 3. analyze-attendance
- **Purpose**: Determine attendance sufficiency.
- **Formulas**: `percentage = (classes_attended / classes_conducted) * 100` (if explicit percentage is not provided).
- **Thresholds**:
  - `>= 90`: Strong Attendance
  - `>= 75`: Acceptable
  - `>= 65`: Attendance Concern
  - `< 65`: High Concern

## 4. detect-performance-risk
- **Purpose**: Flag analytical risk indicators.
- **Rules**:
  - **R1**: `overall_percentage < 50` -> Academic performance concern
  - **R2**: `>= 2` failing subjects -> Multi-subject concern
  - **R3**: `attendance_percentage < 75` -> Attendance concern
  - **R4**: `recent_performance_change <= -10` -> Declining trend indicator

## 5. calculate-grade-summary
- **Purpose**: Group subjects into standardized grade bands.
- **Thresholds**:
  - `A`: 90-100
  - `B`: 80-89.9
  - `C`: 70-79.9
  - `D`: 60-69.9
  - `F`: <60

## 6. analyze-performance-trend
- **Purpose**: Identify trajectory over time.
- **Formulas**: `absolute_change = latest_score - first_score`
- **Thresholds**:
  - `>= 5`: Improving
  - `<= -5`: Declining
  - Between `-4.9` and `4.9`: Relatively Stable

## 7. generate-improvement-plan
- **Purpose**: Generate structured actions.
- **Rules**: 
  - Driven purely by boolean flags (`weak_subjects`, `attendance_concern`, `declining_trend`, `low_overall_percentage`). If flagged, corresponding predefined text blocks are returned. No LLM generation occurs.
