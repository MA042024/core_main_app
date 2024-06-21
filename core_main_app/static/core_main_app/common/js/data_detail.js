/**
 * Shows a dialog to choose download options
 */
var downloadOptions = function() {
    $("#download-modal").modal("show");
};


$(document).on('click', '.btn.download', downloadOptions);



console.log('CSRF Token:', csrftoken);  // Debugging: Print the CSRF token

var loadXmlData = function(event) {
    event.preventDefault();  // Prevent the default action of the event (e.g., navigating away)
    
    console.log('loadDocumentUrl:', loadDocumentUrl);  // Debugging: Print the URL

    // Your data loading logic here
    $.ajax({
        url: loadDocumentUrl,
        type: 'POST',  // Adjust the type as needed
        headers: {
            'X-CSRFToken': csrftoken
        },
        success: function(response) {
            console.log('Data loaded successfully:', response);
            // Handle success (update UI, display message, etc.)
        },
        error: function(xhr, status, error) {
            console.error('Failed to load data:', error);
            console.error('XHR:', xhr);  // Debugging: Print the XHR object
            console.error('Status:', status);  // Debugging: Print the status
            console.error('Error:', error);  // Debugging: Print the error
            // Handle error (display error message, etc.)
        }
    });
};

$(document).on('click', '.load-btn', loadXmlData);
