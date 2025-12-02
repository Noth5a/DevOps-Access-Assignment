from website.State_Transition import VALID_TRANSITONS, allowed_transition

def test_allowed_transitions():
# Not Started
    assert allowed_transition(0, 1) == True  # Not Started to Access Requested
    assert allowed_transition(0, 4) == True  # Not Started to Access Denied

# Access Requested
    assert allowed_transition(1, 2) == True  # Access Requested to Teams Requested
    assert allowed_transition(1, 4) == True  # Access Requested to Access Denied

# Teams Requested
    assert allowed_transition(2, 3) == True  # Teams Requested to Access Granted
    assert allowed_transition(2, 4) == True  # Teams Requested to Access Denied

    

def test_invalid_transitions():
# Not Started
    assert allowed_transition(0, 2) == False  # Not Started to Teams Requested
    assert allowed_transition(0, 3) == False # Not Started to Access Granted

# Access Requested
    assert allowed_transition(1, 3) == False  # Access Requested to Access Granted
    assert allowed_transition(1, 0) == False # Access Requested to Not Started

# Teams Requested
    assert allowed_transition(2, 1) == False # Teams Requested to Access Requested
    assert allowed_transition(2, 0) == False # Teams Requested to Not Started

# Access Granted
    assert allowed_transition(3, 1) == False # Access Granted to Access Requested
    assert allowed_transition(3, 0) == False # Access Granted to Not Started (invalid)
    assert allowed_transition(3, 2) == False # Access Granted to Teams Requested
    assert allowed_transition(3, 4) == False  # Access Granted to Access Denied

# Access Denied
    assert allowed_transition(4, 3) == False # Access Denied to Access Granted
    assert allowed_transition(4, 1) == False # Access Denied to Access Requested
    assert allowed_transition(4, 2) == False # Access Denied to Teams Requested  
    assert allowed_transition(4, 1) == False # Access Denied to Access Requested (invalid)
    assert allowed_transition(4, 0) == False  # Access Denied to Not Started









