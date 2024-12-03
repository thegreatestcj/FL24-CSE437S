$(document).on('click', '.remove-favorite-place-btn', function () {
    const placeId = $(this).data('place_id');
    const containerId = `#container-${placeId}`;
    $.ajax({
        url: 'remove/',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ place_id: placeId }),
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        success: function (response) {
            alert('Place removed from favorites!');
            $(containerId).remove();
        },
        error: function (error) {
            alert('Failed to remove the place. Please try again.');
        },
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Check if this cookie string begins with the name we want
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
