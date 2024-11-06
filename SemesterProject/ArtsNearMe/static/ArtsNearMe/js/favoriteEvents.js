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
