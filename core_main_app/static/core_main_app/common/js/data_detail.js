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
            console.log('Data loaded successfully');
            var data_id = response.data_id;
            var data_content = response.data_content;
            
            // Now you can use data_id and data_content in your JavaScript code
            console.log('Data ID:', data_id);
            console.log('Data Content:', data_content);

            $.post('/store-data-content/', { data_content: data_content }, function(storageResponse) {
                console.log('Data content stored on server:', storageResponse);

                // Redirect to /gensel/ with data_id
                window.location.href = '/gensel/?data_id=' + encodeURIComponent(data_id);
            });
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
