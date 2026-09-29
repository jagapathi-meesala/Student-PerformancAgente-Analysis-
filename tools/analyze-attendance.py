from typing import Any, Dict
from contracts.tool_contract import ToolContract

class Tool(ToolContract):
    @property
    def name(self) -> str:
        return "analyze-attendance"

    @property
    def description(self) -> str:
        return "Analyze student attendance."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "student_id": {"type": "string"},
                "attendance_percentage": {"type": "number"},
                "classes_attended": {"type": "integer"},
                "classes_conducted": {"type": "integer"}
            },
            "required": ["student_id"]
        }

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        student_id = input_data.get("student_id")
        if not student_id or not isinstance(student_id, str):
            raise ValueError("Invalid student_id.")
            
        classes_attended = input_data.get("classes_attended")
        classes_conducted = input_data.get("classes_conducted")
        attendance_percentage = input_data.get("attendance_percentage")
        
        # Calculate from classes if available
        if classes_attended is not None and classes_conducted is not None:
            if not isinstance(classes_attended, (int, float)) or not isinstance(classes_conducted, (int, float)):
                raise ValueError("Classes counts must be numbers.")
            if classes_attended < 0 or classes_conducted <= 0:
                raise ValueError("Invalid class counts (negative or zero conducted).")
            if classes_attended > classes_conducted:
                raise ValueError("Attended classes cannot exceed conducted classes.")
                
            attendance_percentage = (classes_attended / classes_conducted) * 100
        
        if attendance_percentage is None:
            raise ValueError("Must provide either attendance_percentage or classes_attended/conducted.")
            
        if not isinstance(attendance_percentage, (int, float)) or attendance_percentage < 0 or attendance_percentage > 100:
            raise ValueError("Invalid attendance percentage.")
            
        category = "high concern"
        if attendance_percentage >= 90:
            category = "strong attendance"
        elif attendance_percentage >= 75:
            category = "acceptable"
        elif attendance_percentage >= 65:
            category = "attendance concern"
            
        result = {
            "student_id": student_id,
            "attendance_percentage": attendance_percentage,
            "attendance_category": category,
            "shortage_percentage": max(0, 75 - attendance_percentage) if attendance_percentage < 75 else 0,
            "findings": f"Attendance is {category}."
        }
        
        if classes_conducted and attendance_percentage < 75:
            # required additional attendance to reach 75%
            # (attended + x) / (conducted + x) >= 0.75
            # attended + x >= 0.75 * conducted + 0.75 * x
            # 0.25 * x >= 0.75 * conducted - attended
            # x >= 3 * conducted - 4 * attended
            required_additional = max(0, 3 * classes_conducted - 4 * classes_attended)
            result["required_additional_attendance"] = required_additional
            
        return result
