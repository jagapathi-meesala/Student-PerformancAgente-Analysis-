from typing import Any, Dict
from contracts.tool_contract import ToolContract

class Tool(ToolContract):
    @property
    def name(self) -> str:
        return "detect-performance-risk"

    @property
    def description(self) -> str:
        return "Detect academic risk indicators using deterministic rules."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "overall_percentage": {"type": "number"},
                "attendance_percentage": {"type": "number"},
                "failing_subjects_count": {"type": "integer"},
                "recent_performance_change": {"type": "number"}
            }
        }

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        indicators = []
        
        overall = input_data.get("overall_percentage")
        if overall is not None:
            if not isinstance(overall, (int, float)) or overall < 0 or overall > 100:
                raise ValueError("Invalid overall percentage.")
            if overall < 50:
                indicators.append({
                    "rule_triggered": "R1",
                    "affected_metrics": ["overall_percentage"],
                    "severity": "high",
                    "explanation": "overall percentage below 50 -> academic performance concern"
                })
                
        failing_subjects = input_data.get("failing_subjects_count")
        if failing_subjects is not None:
            if not isinstance(failing_subjects, int) or failing_subjects < 0:
                raise ValueError("Invalid failing subjects count.")
            if failing_subjects >= 2:
                indicators.append({
                    "rule_triggered": "R2",
                    "affected_metrics": ["failing_subjects_count"],
                    "severity": "high",
                    "explanation": "two or more failing subjects -> multi-subject concern"
                })
                
        attendance = input_data.get("attendance_percentage")
        if attendance is not None:
            if not isinstance(attendance, (int, float)) or attendance < 0 or attendance > 100:
                raise ValueError("Invalid attendance percentage.")
            if attendance < 75:
                indicators.append({
                    "rule_triggered": "R3",
                    "affected_metrics": ["attendance_percentage"],
                    "severity": "medium",
                    "explanation": "attendance below 75 -> attendance concern"
                })
                
        trend = input_data.get("recent_performance_change")
        if trend is not None:
            if not isinstance(trend, (int, float)):
                raise ValueError("Invalid recent performance change.")
            if trend <= -10:
                indicators.append({
                    "rule_triggered": "R4",
                    "affected_metrics": ["recent_performance_change"],
                    "severity": "medium",
                    "explanation": "performance decrease of at least 10 percentage points across comparable periods -> declining trend indicator"
                })
                
        return {
            "risk_indicators": indicators
        }
