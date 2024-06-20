/**
 * Shows a dialog to choose download options
 */
var downloadOptions = function() {
    $("#download-modal").modal("show");
};


$(document).on('click', '.btn.download', downloadOptions);


var loadXmlData = function() {
    $.ajax({
        url: loadDocumentUrl,  // URL is set from the other JS variable
        type: 'POST',
        data: { 'data_id': data.data.id },
        success: function(response) {
            console.log('Data sent successfully');
            console.log(response.message);
        },
        error: function(xhr, status, error) {
            console.error('Error sending data:', error);
        }
    });
};

$(document).on('click', '.load-btn', loadXmlData);
