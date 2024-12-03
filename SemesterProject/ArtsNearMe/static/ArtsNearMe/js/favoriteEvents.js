document.addEventListener("DOMContentLoaded", function() {
    const eventTimeElements = document.querySelectorAll(".event-time");

    eventTimeElements.forEach(element => {
        // Get the original UTC time from the data attribute
        const utcTime = element.getAttribute("data-time");
        
        if (utcTime) {
            // Create a new Date object from the UTC time
            const eventDate = new Date(utcTime);

            // Format the date to the user's local timezone
            const localTimeString = eventDate.toLocaleString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: 'numeric',
                minute: '2-digit',
                timeZoneName: 'short' // This will add the timezone abbreviation
            });

            // Display the converted time in the element
            element.textContent = `Date: ${localTimeString}`;
        }
    });
});

$(document).on('click', '.remove-favorite-event-btn', function () {
    const eventId = $(this).data('event_id');
    const containerId = `#container-${eventId}`;
    $.ajax({
        url: 'remove/',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ event_id: eventId }),
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        success: function (response) {
            alert('Event removed from favorites!');
            $(containerId).remove();
        },
        error: function (error) {
            alert('Failed to remove the event. Please try again.');
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
