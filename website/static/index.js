const csrfToken = document
  .querySelector('meta[name="csrf-token"]')
  .getAttribute('content');

function deleteRequest(requestId) {
    // Sends a DELETE request to the '/delete-note' route with the noteId as the payload.
  if (confirm("Are you sure you want to delete this Request?")) {
    fetch('/delete-Request', {
        method: 'POST', 
        body: JSON.stringify({ requestId: requestId }),
        headers: { 'Content-Type': 'application/json',
        "X-CSRFToken": csrfToken   // <--- required
        },

    })
    .then((_res) => {

        window.location.href = "/"; 
    })
    .catch((err) => {
      
        console.error("Error deleting the Request:", err);
    });
} else {
    console.log("deletion cancelled.")
}

}

function deleteUser (Userid) {
    // Sends a DELETE request to the '/delete-note' route with the noteId as the payload.
  if (confirm("Are you sure you want to delete this User?")) {
    fetch('/deleteUser', {
        method: 'POST', 
        body: JSON.stringify({ userId: Userid }),
        headers: { 'Content-Type': 'application/json' } ,
    })
    .then((_res) => {
        window.location.href = "/Users";
    })
    .catch((err) => {
      
        console.error("Error deleting the User:", err);
    });
} else {
    console.log("deletion cancelled.")
}

}

function updateState (RequestId, state){
    if (confirm("Are you sure you want to update the state of this Request?")) {
    fetch("/updateState",{
        method : "PUT",
        body: JSON.stringify({ requestId: RequestId, state : state }),
        headers: { 'Content-Type': 'application/json' } 
    })

    .then((_res) => {

        window.location.href = "/"; 
    })
    .catch((err) => {
      
        console.error("Error updating the state:", err);
    });
} else {
    console.log("Update cancelled.")
}
}

function Reject (RequestId, state){
    if (confirm("Are you sure you want to reject this Request?")) {
    fetch("/Reject",{
        method : "PUT",
        body: JSON.stringify({ requestId: RequestId, state : state }),
        headers: { 'Content-Type': 'application/json' } 
    })

    .then((_res) => {

        window.location.href = "/"; 
    })
    .catch((err) => {
      
        console.error("Error rejecting the Request:", err);
    });
} else {
    console.log("Rejection cancelled.")
}
}

function openUpdateModal(RequestId, requestedForEmail, accessLevel) {
    // Populate the modal with existing data
    document.getElementById("requestId").value = RequestId;
    document.getElementById("updateRequestedForEmail").value = requestedForEmail;
    document.getElementById("updateAccessLevel").value = accessLevel;
    // Show the modal
    const updateModal = new bootstrap.Modal(document.getElementById("updateRequestModal"));
    updateModal.show();
}

function openUpdateUserModal(UserId, UserEmail, UserRole) {
    // Populate the modal with existing data
    document.getElementById("userId").value = UserId;
    document.getElementById("updateUserEmail").value = UserEmail;
    document.getElementById("updateUserRole").value = UserRole;
    // Show the modal
    const updateModal = new bootstrap.Modal(document.getElementById("updateUserModal"));
    updateModal.show();
}


const saveUpdateBtn = document.getElementById("saveUpdateBtn");
if (saveUpdateBtn) {
    saveUpdateBtn.addEventListener("click", function () {
    const requestId = document.getElementById("requestId").value;
    const requestedForEmail = document.getElementById("updateRequestedForEmail").value;
    const accessLevel = document.getElementById("updateAccessLevel").value;
    // Debug: Check if requestId is set
    console.log("Request ID Sent:", requestId);

    if (!requestId) {
        alert("Error: Missing Request ID.");
        return;
    }

    fetch("/update_request", {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            request_id: requestId,  
            requested_for_email: requestedForEmail,
            access_level: accessLevel
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(data.message);
        }
        window.location.href = "/";
    })
    .catch(error => console.error("Error:", error));
});
}

const saveUpdateUserBtn = document.getElementById("saveUpdateUserBtn");
if (saveUpdateUserBtn) {
    saveUpdateUserBtn.addEventListener("click", function () {
    const userId = document.getElementById("userId").value;
    const userEmail = document.getElementById("updateUserEmail").value;
    const userRole = document.getElementById("updateUserRole").value;
    // Debug: Check if userId is set
    console.log("User ID Sent:", userId);

    if (!userId) {
        alert("Error: Missing User ID.");
        return;
    }

    fetch("/update_user", {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            user_id: userId,  
            email: userEmail,
            role: userRole
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(data.message);
        }
        window.location.href = "/Users";
    })
    .catch(error => console.error("Error:", error));
});
}