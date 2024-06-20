/**
 * Shows a dialog to choose download options
 */
var downloadOptions = function() {
    $("#download-modal").modal("show");
};


$(document).on('click', '.btn.download', downloadOptions);


var loadXmlData = function() {
    window.location.href = loadDocumentUrl;
};

$(document).on('click', '.load-btn', loadXmlData);
