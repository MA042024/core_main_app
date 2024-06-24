/**
 * Shows a dialog to choose download options
 */
var downloadOptions = function() {
    $("#download-modal").modal("show");
};


$(document).on('click', '.btn.download', downloadOptions);



console.log('CSRF Token:', csrftoken);  // Debugging: Print the CSRF token

var loadXmlData = function(event) {
    event.preventDefault();
    
    console.log('CSRF Token:', csrftoken);
    console.log('loadDocumentUrl:', loadDocumentUrl);

    $.ajax({
        url: loadDocumentUrl,
        type: 'POST',
       /* headers: {
            'X-CSRFToken': csrftoken
        },*/
        contentType: 'application/json',
        success: function(response) {
            console.log('Data loaded successfully:', response);
        },
        error: function(xhr, status, error) {
            console.error('Failed to load data:', error);
            console.error('XHR:', xhr);
            console.error('Status:', status);
            console.error('Error:', error); 
        }
    });
};

$(document).on('click', '.load-btn', loadXmlData);
