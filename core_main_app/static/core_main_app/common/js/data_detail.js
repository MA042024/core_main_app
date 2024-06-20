/**
 * Shows a dialog to choose download options
 */
var downloadOptions = function() {
    $("#download-modal").modal("show");
};


$(document).on('click', '.btn.download', downloadOptions);


function getC(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken1 = getC('csrftoken');


var loadXmlData = function(event) {
    //event.preventDefault();  // Prevent the default action of the event (e.g., navigating away)
    
    // Your data loading logic here
    $.ajax({
        url: loadDocumentUrl,
        type: 'POST',  // Adjust the type as needed
        data: {},  // Optional data to send with the request
        headers: {
            'X-CSRFToken': csrftoken1
        },
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
