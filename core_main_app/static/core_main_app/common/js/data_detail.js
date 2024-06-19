/**
 * Shows a dialog to choose download options
 */
var downloadOptions = function() {
    $("#download-modal").modal("show");
};


$(document).on('click', '.btn.download', downloadOptions);



var loadXmlData = function() {
    $.ajax({
        url: /data/load/,
        type: 'POST',
        data: { 'data_id': data.data.id },
        success: function(response) {
            console.log('XML data sent successfully');
            console.log(response.data_id);
            console.log(response.data_content);
            // Send the data to /gensel/
            /*$.ajax({
                url: '/gensel/',
                type: 'POST',
                data: {
                    'data_id': response.data_id,
                    'data_content': response.data_content
                },
                success: function() {
                    console.log('Data successfully sent to /gensel/');
                },
                error: function(xhr, status, error) {
                    console.error('Error sending data to /gensel/:', error);
                }
            });*/
        },
        error: function(xhr, status, error) {
            console.error('Error sending XML data:', error);
        }
    });
};

$(document).on('click', '.load-btn', loadXmlData);

