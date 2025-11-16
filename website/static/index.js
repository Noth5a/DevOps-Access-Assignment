function deleteRequest(requestId) {
    // Sends a DELETE request to the '/delete-note' route with the noteId as the payload.
  if (confirm("Are you sure you want to delete this Request?")) {
    fetch('/delete-Request', {
        method: 'POST', 
        body: JSON.stringify({ requestId: requestId }),
        headers: { 'Content-Type': 'application/json' } 
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

function openUpdateModal(RequestId, requestedForEmail, accessLevel) {
    // Populate the modal with existing data
    document.getElementById("requestId").value = RequestId;
    document.getElementById("updateRequestedForEmail").value = requestedForEmail;
    document.getElementById("updateAccessLevel").value = accessLevel;
    // Show the modal
    const updateModal = new bootstrap.Modal(document.getElementById("updateRequestModal"));
    updateModal.show();
}

document.getElementById("saveUpdateBtn").addEventListener("click", function () {
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
