let load = function() {
    console.log("Load URL: " + loadDocumentUrl);

    // Fetch the document data using its ID
    fetch(loadDocumentUrl)
        .then(response => response.json())
        .then(data => {
            console.log("Loaded data:", data);

            // Send the fetched data to another page via an AJAX request
            $.ajax({
                url: '/gensel/', // Replace with the URL of the target page
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    documentId: data.documentId,
                    otherData: data // Include any other data you need to send
                }),
                success: function(response) {
                    console.log("Data successfully sent to another page:", response);
                    // Add any success handling logic here
                },
                error: function(xhr, status, error) {
                    console.error("Error sending data to another page:", error);
                    // Add any error handling logic here
                }
            });
        })
        .catch(error => console.error('Error loading document:', error));
};

// Bind the click event of the load button to the load function
$('.load-document-btn').on('click', load);
