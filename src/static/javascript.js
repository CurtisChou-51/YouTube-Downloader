document.getElementById('input-container').addEventListener('submit', function(event) {
    event.preventDefault();
    const url = document.getElementById('url').value;
    const audioOnly = document.getElementById('audioOnly').value;

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
    .then(response => response.blob())
    .then(blob => {
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = downloadUrl;
        a.download = audioOnly === 'yes' ? 'audio.mp3' : 'video.mp4';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(downloadUrl);

        // Hide loading spinner
        loadingIcon.style.display = 'none';
    })
    .catch(error => {
        console.error('Error:', error);

        // Hide loading spinner
        loadingIcon.style.display = 'none';
    });
});