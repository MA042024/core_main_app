/**
 * Shows a dialog to choose download options
 */
var downloadOptions = function() {
    $("#download-modal").modal("show");
};


$(document).on('click', '.btn.download', downloadOptions);


var loadXmlData = function(event) {
    //event.preventDefault();  // Prevent the default action of the event (e.g., navigating away)
    
    // Your data loading logic here
    $.ajax({
        url: loadDocumentUrl,
        type: 'POST',  // Adjust the type as needed
        data: {},  // Optional data to send with the request
        success: function(response) {
            console.log('Data loaded successfully:', response);
            // Handle success (update UI, display message, etc.)
        },
        error: function(xhr, status, error) {
            console.error('Failed to load data:', error);
            // Handle error (display error message, etc.)
        }
    });
};

$(document).on('click', '.load-btn', loadXmlData);
