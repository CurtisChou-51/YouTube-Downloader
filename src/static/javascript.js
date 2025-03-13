document.getElementById('input-container').addEventListener('submit', function(event) {
    event.preventDefault();
    const url = document.getElementById('url').value;
    const audioOnly = document.getElementById('audioOnly').checked;

    // Show loading spinner
    const loadingIcon = document.getElementById('loading-icon');
    loadingIcon.style.display = 'block';

    fetch('/download', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ url: url, audioOnly: audioOnly })
    })
    .then(response => response.json())
    .then(json => {
        console.log(json);
        loadingIcon.style.display = 'none';
    })
    .catch(error => {
        console.error('Error:', error);

        // Hide loading spinner
        loadingIcon.style.display = 'none';
    });
});