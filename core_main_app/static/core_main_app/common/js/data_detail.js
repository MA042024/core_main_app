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
            var data_title = response.data_title;
            
            console.log('Data ID:', data_id);
            console.log('Data Content:', data_content);
            console.log('Data Title:', data_title);

            localStorage.setItem('data_id', data_id);
            localStorage.setItem('data_content', JSON.stringify(data_content));
            localStorage.setItem('data_title', data_title);

            window.location.href = '/gensel';
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
