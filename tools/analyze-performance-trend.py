from typing import Any, Dict
from contracts.tool_contract import ToolContract

class Tool(ToolContract):
    @property
    def name(self) -> str:
        return "analyze-performance-trend"

    @property
    def description(self) -> str:
        return "Analyze multiple academic periods deterministically."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "student_id": {"type": "string"},
                "periods": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "period": {"type": "string"},
                            "percentage": {"type": "number"}
                        },
                        "required": ["period", "percentage"]
                    }
                }
            },
            "required": ["student_id", "periods"]
        }

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        periods = input_data.get("periods")
        
        if not isinstance(periods, list):
            raise ValueError("Periods must be a list.")
            
        if len(periods) < 2:
            raise ValueError("Fewer than required periods (minimum 2 needed for trend).")
            
        seen_periods = set()
        scores = []
        
        for p in periods:
            period_name = p.get("period")
            pct = p.get("percentage")
            
            if not period_name or pct is None:
                raise ValueError("Missing period or percentage.")
                
            if period_name in seen_periods:
                raise ValueError(f"Duplicate period: {period_name}")
                
            if not isinstance(pct, (int, float)) or pct < 0 or pct > 100:
                raise ValueError("Invalid percentage.")
                
            seen_periods.add(period_name)
            scores.append(pct)
            
        first = scores[0]
        latest = scores[-1]
        absolute_change = latest - first
        average_change = absolute_change / (len(scores) - 1)
        
        if absolute_change >= 5:
            category = "improving"
        elif absolute_change <= -5:
            category = "declining"
        else:
            category = "relatively stable"
            
        return {
            "first_score": first,
            "latest_score": latest,
            "absolute_change": absolute_change,
            "average_change_per_period": average_change,
            "category": category,
            "trend_explanation": f"Based on analytic thresholds (+/- 5 points), trend is {category}."
        }
