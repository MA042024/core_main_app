/**
 * Shows a dialog to choose download options
 */
var downloadOptions = function() {
    $("#download-modal").modal("show");
};


$(document).on('click', '.btn.download', downloadOptions);



var loadXmlData = function(event) {
    event.preventDefault();
    $.ajax({
        url: loadDocumentUrl,
        type: 'POST',
        contentType: 'application/json',
        success: function(response) {
            var data_id = response.data_id;
            var data_content = response.data_content;
            var data_title = response.data_title;
            #localStorage.setItem('data_content', JSON.stringify(data_content));
            #localStorage.setItem('data_title', data_title);
            #sessionStorage.setItem('data_id', data_id);
            sessionStorage.setItem('data_content', JSON.stringify(data_content));
            sessionStorage.setItem('data_title', data_title);
            
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
