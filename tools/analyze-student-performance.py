from typing import Any, Dict
from contracts.tool_contract import ToolContract

class Tool(ToolContract):
    @property
    def name(self) -> str:
        return "analyze-student-performance"

    @property
    def description(self) -> str:
        return "Analyze a student's overall academic performance from structured records."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "student_id": {"type": "string"},
                "student_name": {"type": "string"},
                "subjects": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "subject_id": {"type": "string"},
                            "subject_name": {"type": "string"},
                            "marks_obtained": {"type": "number"},
                            "max_marks": {"type": "number"}
                        },
                        "required": ["subject_id", "marks_obtained", "max_marks"]
                    }
                },
                "attendance_percentage": {"type": "number"}
            },
            "required": ["student_id", "subjects"]
        }

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        student_id = input_data.get("student_id")
        if not student_id or not isinstance(student_id, str):
            raise ValueError("Invalid student_id.")
            
        subjects = input_data.get("subjects", [])
        if not isinstance(subjects, list):
            raise ValueError("Subjects must be a list.")
            
        total_subjects = len(subjects)
        total_marks_obtained = 0.0
        total_max_marks = 0.0
        
        highest_subject = None
        lowest_subject = None
        highest_score = -1.0
        lowest_score = float('inf')
        
        passing_subjects = []
        below_threshold_subjects = []
        
        seen_subject_ids = set()
        
        for subject in subjects:
            subject_id = subject.get("subject_id")
            if not subject_id or subject_id in seen_subject_ids:
                raise ValueError(f"Duplicate or missing subject_id: {subject_id}")
            seen_subject_ids.add(subject_id)
            
            marks_obtained = subject.get("marks_obtained")
            max_marks = subject.get("max_marks")
            
            if not isinstance(marks_obtained, (int, float)) or not isinstance(max_marks, (int, float)):
                raise ValueError("Marks must be numeric.")
                
            if marks_obtained < 0 or max_marks <= 0:
                raise ValueError("Marks obtained cannot be negative and max marks must be > 0.")
                
            if marks_obtained > max_marks:
                raise ValueError(f"Marks obtained ({marks_obtained}) exceeds max marks ({max_marks}) for {subject_id}.")
                
            total_marks_obtained += marks_obtained
            total_max_marks += max_marks
            
            percentage = (marks_obtained / max_marks) * 100
            
            if percentage > highest_score:
                highest_score = percentage
                highest_subject = subject_id
            if percentage < lowest_score:
                lowest_score = percentage
                lowest_subject = subject_id
                
            if percentage >= 50:  # Assuming 50 is the pass mark threshold
                passing_subjects.append(subject_id)
            else:
                below_threshold_subjects.append(subject_id)
                
        overall_percentage = (total_marks_obtained / total_max_marks * 100) if total_max_marks > 0 else 0.0
        average_percentage = overall_percentage # For this calculation, it's the same based on total weights
        
        result = {
            "total_subjects": total_subjects,
            "total_marks_obtained": total_marks_obtained,
            "total_maximum_marks": total_max_marks,
            "overall_percentage": overall_percentage,
            "average_percentage": average_percentage,
            "highest_performing_subject": highest_subject,
            "lowest_performing_subject": lowest_subject,
            "passing_subjects": passing_subjects,
            "below_threshold_subjects": below_threshold_subjects
        }
        
        attendance = input_data.get("attendance_percentage")
        if attendance is not None:
            if not isinstance(attendance, (int, float)) or attendance < 0 or attendance > 100:
                raise ValueError("Invalid attendance_percentage.")
            result["attendance_status"] = "satisfactory" if attendance >= 75 else "concern"
            
        return result
