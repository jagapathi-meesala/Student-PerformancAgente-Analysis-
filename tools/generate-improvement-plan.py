from typing import Any, Dict
from contracts.tool_contract import ToolContract

class Tool(ToolContract):
    @property
    def name(self) -> str:
        return "generate-improvement-plan"

    @property
    def description(self) -> str:
        return "Generate a structured, rule-based improvement plan from detected weak areas."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "weak_subjects": {"type": "array", "items": {"type": "string"}},
                "attendance_concern": {"type": "boolean"},
                "declining_trend": {"type": "boolean"},
                "low_overall_percentage": {"type": "boolean"}
            }
        }

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        weak_subjects = input_data.get("weak_subjects", [])
        if not isinstance(weak_subjects, list):
            raise ValueError("weak_subjects must be a list.")
            
        attendance = input_data.get("attendance_concern", False)
        trend = input_data.get("declining_trend", False)
        overall = input_data.get("low_overall_percentage", False)
        
        priority_areas = []
        actions = []
        reasoning = []
        assumptions = ["Plan generated from supplied deterministic data."]
        
        if overall:
            priority_areas.append("Overall academic standing")
            actions.append("Establish a comprehensive study schedule to lift overall average.")
            reasoning.append("Low overall percentage indicates broad academic difficulty.")
            
        if trend:
            priority_areas.append("Performance trend")
            actions.append("Review recent assessment performance to identify the cause of the decline.")
            reasoning.append("Declining trend across recent periods detected.")
            
        if attendance:
            priority_areas.append("Attendance")
            actions.append("Improve class attendance.")
            reasoning.append("Attendance is below acceptable project thresholds.")
            
        if weak_subjects:
            priority_areas.extend([f"Subject: {s}" for s in weak_subjects])
            actions.append(f"Recommend additional practice for subjects: {', '.join(weak_subjects)}.")
            if len(weak_subjects) > 1:
                actions.append("Prioritize subjects with the largest score gaps.")
            reasoning.append(f"Identified {len(weak_subjects)} weak subject(s).")
            
        if not priority_areas:
            priority_areas.append("Maintenance")
            actions.append("Maintain current study habits.")
            reasoning.append("No critical risk areas detected.")
            
        return {
            "priority_areas": priority_areas,
            "actions": actions,
            "reasoning": reasoning,
            "assumptions": assumptions
        }
