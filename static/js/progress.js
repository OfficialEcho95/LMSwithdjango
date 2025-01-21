function updateProgress(courseId, progress) {
    fetch('/update_progress/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            course_id: courseId,
            progress: progress
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Progress updated!');
                document.getElementById('progress').textContent = progress;
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error updating progress:', error);
        });
}

// Utility function to get CSRF token from cookies (if using CSRF protection)
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
