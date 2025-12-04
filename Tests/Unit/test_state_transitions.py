from website.State_Transition import VALID_TRANSITONS, allowed_transition

def test_allowed_transitions():
# Not Started
    assert allowed_transition(0, 1) == True  
    assert allowed_transition(0, 4) == True  

# Access Requested
    assert allowed_transition(1, 2) == True  
    assert allowed_transition(1, 4) == True  

# Teams Requested
    assert allowed_transition(2, 3) == True  
    assert allowed_transition(2, 4) == True  

    

def test_invalid_transitions():
# Not Started
    assert allowed_transition(0, 2) == False  
    assert allowed_transition(0, 3) == False 

# Access Requested
    assert allowed_transition(1, 3) == False 
    assert allowed_transition(1, 0) == False 

# Teams Requested
    assert allowed_transition(2, 1) == False 
    assert allowed_transition(2, 0) == False 

# Access Granted
    assert allowed_transition(3, 1) == False 
    assert allowed_transition(3, 0) == False 
    assert allowed_transition(3, 2) == False 
    assert allowed_transition(3, 4) == False  

# Access Denied
    assert allowed_transition(4, 3) == False
    assert allowed_transition(4, 1) == False 
    assert allowed_transition(4, 2) == False 
    assert allowed_transition(4, 1) == False 
    assert allowed_transition(4, 0) == False  









