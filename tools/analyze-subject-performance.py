from typing import Any, Dict, List
from contracts.tool_contract import ToolContract

class Tool(ToolContract):
    @property
    def name(self) -> str:
        return "analyze-subject-performance"

    @property
    def description(self) -> str:
        return "Analyze one or multiple subjects deterministically."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "subjects": {
                    "type": "array",
                    "items": {
                        "type": "object"
                    }
                }
            },
            "required": ["subjects"]
        }

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        subjects = input_data.get("subjects", [])
        if not isinstance(subjects, list):
            raise ValueError("Subjects must be a list.")
            
        results = []
        strongest_subjects = []
        weakest_subjects = []
        
        for subject in subjects:
            subject_id = subject.get("subject_id")
            marks_obtained = subject.get("marks_obtained")
            max_marks = subject.get("max_marks")
            
            if not subject_id or marks_obtained is None or not max_marks:
                raise ValueError("Subject record missing required fields.")
                
            if not isinstance(marks_obtained, (int, float)) or not isinstance(max_marks, (int, float)):
                raise ValueError("Marks must be numeric.")
                
            if marks_obtained < 0 or max_marks <= 0 or marks_obtained > max_marks:
                raise ValueError("Invalid marks range.")
                
            percentage = (marks_obtained / max_marks) * 100
            
            category = "critical improvement"
            if percentage >= 90:
                category = "excellent"
            elif percentage >= 75:
                category = "strong"
            elif percentage >= 60:
                category = "satisfactory"
            elif percentage >= 40:
                category = "needs improvement"
                
            results.append({
                "subject_id": subject_id,
                "percentage": percentage,
                "pass": percentage >= 40,
                "score_category": category
            })
            
            if percentage >= 75:
                strongest_subjects.append(subject_id)
            if percentage < 60:
                weakest_subjects.append(subject_id)
                
        return {
            "subject_level_findings": results,
            "strongest_subjects": strongest_subjects,
            "weakest_subjects": weakest_subjects
        }
