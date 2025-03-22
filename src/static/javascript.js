document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('btn-oauth-start').addEventListener('click', function (event) {
        let w = window.open('/oauth_start');
        let timer = setInterval(function () {
            if (!w.closed)
                return;
            // once the window is closed, release oauth waiting
            clearInterval(timer);
            fetch('/oauth_end')
                .then(response => response.json())
                .then(json => alert(json.message));
        }, 1000);
    });

    document.getElementById('input-container').addEventListener('submit', function (event) {
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
                if (json.dir_name)
                    getFile(json.dir_name);
                loadingIcon.style.display = 'none';
            })
            .catch(error => {
                console.error('Error:', error);

                // Hide loading spinner
                loadingIcon.style.display = 'none';
            });
    });

    function getFile(dir_name) {
        let form = document.createElement('form');
        form.method = 'POST';
        form.action = `/get_file?dir_name=${dir_name}`;
        document.body.appendChild(form);
        form.submit();
        setTimeout(() => {
            form.remove();
        }, 10);
    }
});
