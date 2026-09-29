import pytest
import os
import importlib.util

def load_tool(module_name):
    tools_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools"))
    path = os.path.join(tools_dir, f"{module_name}.py")
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Tool()

def test_analyze_student_performance():
    tool = load_tool("analyze-student-performance")
    data = {
        "student_id": "S1",
        "subjects": [
            {"subject_id": "M1", "marks_obtained": 80, "max_marks": 100},
            {"subject_id": "P1", "marks_obtained": 40, "max_marks": 100}
        ],
        "attendance_percentage": 80
    }
    res = tool.execute(data)
    assert res["total_subjects"] == 2
    assert res["overall_percentage"] == 60.0
    assert res["highest_performing_subject"] == "M1"
    assert res["passing_subjects"] == ["M1"]
    assert res["below_threshold_subjects"] == ["P1"]
    assert res["attendance_status"] == "satisfactory"

def test_analyze_student_performance_invalid():
    tool = load_tool("analyze-student-performance")
    with pytest.raises(ValueError):
        tool.execute({"student_id": "S1", "subjects": [{"subject_id": "M1", "marks_obtained": 110, "max_marks": 100}]})

def test_analyze_subject_performance():
    tool = load_tool("analyze-subject-performance")
    data = {"subjects": [{"subject_id": "M1", "marks_obtained": 95, "max_marks": 100}]}
    res = tool.execute(data)
    assert res["strongest_subjects"] == ["M1"]
    assert res["subject_level_findings"][0]["score_category"] == "excellent"

def test_analyze_attendance():
    tool = load_tool("analyze-attendance")
    res = tool.execute({"student_id": "S1", "classes_attended": 60, "classes_conducted": 100})
    assert res["attendance_category"] == "high concern"
    assert res["shortage_percentage"] == 15

def test_detect_performance_risk():
    tool = load_tool("detect-performance-risk")
    res = tool.execute({"overall_percentage": 45, "failing_subjects_count": 3})
    inds = [r["rule_triggered"] for r in res["risk_indicators"]]
    assert "R1" in inds
    assert "R2" in inds

def test_calculate_grade_summary():
    tool = load_tool("calculate-grade-summary")
    res = tool.execute([{"subject_id": "M1", "percentage": 85}])
    assert res["grade_counts"]["B"] == 1

def test_analyze_performance_trend():
    tool = load_tool("analyze-performance-trend")
    res = tool.execute({
        "student_id": "S1",
        "periods": [
            {"period": "T1", "percentage": 50},
            {"period": "T2", "percentage": 60}
        ]
    })
    assert res["category"] == "improving"

def test_generate_improvement_plan():
    tool = load_tool("generate-improvement-plan")
    res = tool.execute({"weak_subjects": ["Math"], "attendance_concern": True})
    assert any("attendance" in a.lower() for a in res["actions"])
    assert any("Math" in a for a in res["actions"])
