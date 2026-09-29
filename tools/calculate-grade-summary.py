from typing import Any, Dict
from contracts.tool_contract import ToolContract

class Tool(ToolContract):
    @property
    def name(self) -> str:
        return "calculate-grade-summary"

    @property
    def description(self) -> str:
        return "Produce a deterministic grade summary from subject percentages."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "subject_id": {"type": "string"},
                    "percentage": {"type": "number"}
                },
                "required": ["subject_id", "percentage"]
            }
        }

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Input validation for top-level array since tool inputs are usually dicts in AgentCore
        # Allowing list directly or dict with 'subjects' key for flexibility
        subjects = input_data if isinstance(input_data, list) else input_data.get("subjects", [])
        
        if not isinstance(subjects, list):
            raise ValueError("Input must be a list of subjects.")
            
        if not subjects:
            raise ValueError("Empty subjects list.")
            
        total = 0.0
        highest = -1.0
        lowest = 101.0
        
        grade_counts = {
            "A": 0, "B": 0, "C": 0, "D": 0, "F": 0
        }
        
        subject_categories = []
        
        for sub in subjects:
            sid = sub.get("subject_id")
            pct = sub.get("percentage")
            
            if not sid or pct is None:
                raise ValueError("Missing subject_id or percentage.")
                
            if not isinstance(pct, (int, float)) or pct < 0 or pct > 100:
                raise ValueError("Invalid percentage.")
                
            total += pct
            if pct > highest:
                highest = pct
            if pct < lowest:
                lowest = pct
                
            if pct >= 90:
                grade = "A"
            elif pct >= 80:
                grade = "B"
            elif pct >= 70:
                grade = "C"
            elif pct >= 60:
                grade = "D"
            else:
                grade = "F"
                
            grade_counts[grade] += 1
            subject_categories.append({"subject_id": sid, "category": grade})
            
        return {
            "total_subjects": len(subjects),
            "average_percentage": total / len(subjects),
            "highest_percentage": highest,
            "lowest_percentage": lowest,
            "grade_counts": grade_counts,
            "subject_categories": subject_categories,
            "summary_explanation": "Project-defined grade bands: A (90-100), B (80-89.9), C (70-79.9), D (60-69.9), F (<60)."
        }
