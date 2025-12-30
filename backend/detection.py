"""
SIGMA Detection Engine
Rule-based fruit freshness detection using color sensor data
"""
import config

def detect_freshness(fruit_type: str, r: int, g: int, b: int, temperature: float = None) -> tuple[str, float]:
    """
    Detect fruit freshness based on RGB values and optional temperature
    
    Args:
        fruit_type: Type of fruit (apple, banana, orange, etc.)
        r, g, b: RGB color values (0-255)
        temperature: Optional temperature in Celsius
    
    Returns:
        tuple: (status, confidence) where status is 'fresh', 'warning', or 'rotten'
               and confidence is a float between 0.0 and 1.0
    """
    # Get rules for this fruit type, fallback to default
    rules = config.DETECTION_RULES.get(fruit_type.lower(), config.DETECTION_RULES["default"])
    
    # Check fresh conditions
    fresh_rules = rules.get("fresh", {})
    if check_rgb_conditions(r, g, b, fresh_rules):
        confidence = calculate_confidence(r, g, b, fresh_rules)
        return "fresh", confidence
    
    # Check warning conditions
    warning_rules = rules.get("warning", {})
    if check_rgb_conditions(r, g, b, warning_rules):
        confidence = calculate_confidence(r, g, b, warning_rules) * 0.7  # Lower confidence for warning
        return "warning", confidence
    
    # If neither fresh nor warning, it's rotten
    return "rotten", 0.8

def check_rgb_conditions(r: int, g: int, b: int, conditions: dict) -> bool:
    """
    Check if RGB values meet all conditions in the rule
    
    Args:
        r, g, b: RGB values
        conditions: Dictionary of conditions (r_min, r_max, g_min, etc.)
    
    Returns:
        bool: True if all conditions are met
    """
    checks = []
    
    # Red channel checks
    if "r_min" in conditions:
        checks.append(r >= conditions["r_min"])
    if "r_max" in conditions:
        checks.append(r <= conditions["r_max"])
    
    # Green channel checks
    if "g_min" in conditions:
        checks.append(g >= conditions["g_min"])
    if "g_max" in conditions:
        checks.append(g <= conditions["g_max"])
    
    # Blue channel checks
    if "b_min" in conditions:
        checks.append(b >= conditions["b_min"])
    if "b_max" in conditions:
        checks.append(b <= conditions["b_max"])
    
    # All conditions must be True
    return all(checks) if checks else False

def calculate_confidence(r: int, g: int, b: int, conditions: dict) -> float:
    """
    Calculate confidence score based on how well values match conditions
    Simple implementation: base confidence of 0.85 for matching conditions
    Can be enhanced with ML later
    """
    return 0.85

def get_status_color(status: str) -> str:
    """Get hex color code for status visualization"""
    colors = {
        "fresh": "#4ade80",      # Green
        "warning": "#fb923c",    # Orange
        "rotten": "#ef4444"      # Red
    }
    return colors.get(status, "#6b7280")  # Gray as default
