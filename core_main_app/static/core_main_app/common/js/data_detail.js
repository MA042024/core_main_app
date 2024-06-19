/**
 * Shows a dialog to choose download options
 */
var downloadOptions = function() {
    $("#download-modal").modal("show");
};


$(document).on('click', '.btn.download', downloadOptions);


let load = function() {
    var loadDocumentUrl = "{% url 'core_main_app_rest_data_download' data.data.id %}";
    console.log("Load URL: " + loadDocumentUrl);

    // Fetch the document data using its ID
    fetch(loadDocumentUrl)
        .then(response => response.json())
        .then(data => {
            console.log("Loaded data:", data);
        })
};

// Bind the click event of the load button to the load function
$('.load-btn').on('click', load);
