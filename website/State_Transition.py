VALID_TRANSITONS = {
    0: [1, 4],  # From Not Started to Access Requested or Access Denied
    1: [2, 4],  # From Access Requested to Teams Requested or Access Denied
    2: [3, 4],  # From Teams Requested to Access Granted or Access Denied
    3: [],      # Access Granted is a terminal state
    4: []       # Access Denied is a terminal state
}

def allowed_transition(current_state: int, new_state: int) -> bool:
    """Check if transitioning from current_state to new_state is allowed."""
    return new_state in VALID_TRANSITONS.get(current_state, [])

def get_next_state(current_state: int) -> int:
    """Get the next state in the workflow."""
    allowed = VALID_TRANSITONS.get(current_state, [])
    return allowed[0] if allowed else current_state