let favoritePlaces = [];
let favoriteEvents = [];
let mapInitialized = false;
const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
let currentLat;
let currentLng;
console.log()


// Default view is Places. User can switch between Places and Events views.
$(document).ready(function() {
    // Handle button click
    $('#places-button, #events-button').click(function() {
        // Remove active-button styling from all buttons
        $('#places-button, #events-button').removeClass('bg-sky-800 text-white hover:bg-sky-950 active-button').addClass('bg-gray-300 text-gray-800 hover:bg-gray-400');
        
        // Add active-button styling to the clicked button
        $(this).removeClass('bg-gray-300 text-gray-800 hover:bg-gray-400').addClass('bg-sky-800 text-white hover:bg-sky-950 active-button');
        
        // Toggle content display based on which button is clicked
        if ($(this).attr('id') === 'places-button') {
            // Show place list content
            $('#places-list').removeClass('hidden');
            $('#events-list').addClass('hidden'); // Hide events content if it exists
        } else if ($(this).attr('id') === 'events-button') {
            // Show events content (if you add it later)
            $('#events-list').removeClass('hidden');
            $('#places-list').addClass('hidden');
        }
    });

    $('#places-button').click(function() {
        markPlaces(map, nearbyPlaces);
    });
    $('#events-button').click(function() {
        console.log(mapMarkerDetails);
        markEventVenues(map, mapMarkerDetails);
    });
    // We don't need to trigger list display functions,
    // as list data has been fetched when the map is loaded,
    // we're just going to toggle the list container hidden/unhidden.

    // The following code: update favorite button status based on user data

    // Fetch favorite places and events on page load
    $.get('api/favorites/places/', function(data) {
        favoritePlaces = data.favorites;
        console.log(favoritePlaces);
        // updateFavoritePlaceButtons(favoritePlaces);  // Ensured to run after DOM is ready
    });

    $.get('api/favorites/events/', function(data) {
        favoriteEvents = data.favorites;
        // updateFavoriteEventButtons(favoriteEvents);  // Ensured to run after DOM is ready
    });

    // Toggle favorite place
    $(document).on('click', '.add-favorite-place-btn', function() {
        const $button = $(this);
        const placeId = $button.data('place_id');
        const isFavorite = favoritePlaces.includes(placeId);

        if (isFavorite) {
            $.ajax({
                url: 'api/favorite/place/remove/',
                type: 'POST',
                data: JSON.stringify({ place_id: placeId }),
                contentType: 'application/json',
                headers: { 'X-CSRFToken': getCookie('csrftoken') },
                success: function(response) {
                    favoritePlaces = favoritePlaces.filter(id => id !== placeId);
                    $button.removeClass('bg-red-800 hover:bg-red-900').text('Add to Favorites');
                }
            });
        } else {
            $.ajax({
                url: 'api/favorite/place/add/',
                type: 'POST',
                data: JSON.stringify({
                    place_id: placeId,
                    place_name: $button.data('place_name'),
                    place_address: $button.data('place_address'),
                    place_website: $button.data('place_website'),
                    place_longitude: $button.data('place_longitude'),
                    place_latitude: $button.data('place_latitude'),
                }),
                contentType: 'application/json',
                headers: { 'X-CSRFToken': getCookie('csrftoken') },
                success: function(response) {
                    favoritePlaces.push(placeId);
                    $button.addClass('bg-red-800 hover:bg-red-900').text('Remove Favorites');
                }
            });
        }
    });

    // Toggle favorite event
    $(document).on('click', '.save-event-btn', function() {
        const $button = $(this);
        const eventId = $button.data('event_id');
        const isFavorite = favoriteEvents.includes(eventId);

        if (isFavorite) {
            $.ajax({
                url: 'api/favorite/event/remove/',
                type: 'POST',
                data: JSON.stringify({ event_id: eventId }),
                contentType: 'application/json',
                headers: { 'X-CSRFToken': getCookie('csrftoken') },
                success: function(response) {
                    favoriteEvents = favoriteEvents.filter(event_id => event_id !== eventId);
                    $button.removeClass('bg-red-800 hover:bg-red-900').text('Save');
                }
            });
        } else {
            $.ajax({
                url: 'api/favorite/event/add/',
                type: 'POST',
                data: JSON.stringify({
                    event_id: eventId,
                    event_name: $button.data('event_name'),
                    event_venue: $button.data('event_venue'),
                    event_venue_id: $button.data('event_venue_id'),
                    event_address: $button.data('event_address'),
                    event_start_time: $button.data('event_start_time'),
                    event_url: $button.data('event_url')
                }),
                contentType: 'application/json',
                headers: { 'X-CSRFToken': getCookie('csrftoken') },
                success: function(response) {
                    favoriteEvents.push(eventId);
                    $button.addClass('bg-red-800 hover:bg-red-900').text('Remove');
                }
            });
        }
    });

    // Trigger search on Enter key
    $('#location-search').on('keypress', function (e) {
        if (e.which === 13) { // Enter key
            e.preventDefault();
            const query = $(this).val();
            searchLocation(query);
            // $(this).val('');
        }
    });

    // Trigger search on button click
    $('#search-button').on('click', function () {
        const query = $('#location-search').val();
        searchLocation(query);
        // Clear the input field after search
        // $('#location-search').val('');
    });

});

// Listen for the custom mapReady event
$(document).on("mapReady", function() {
    // Check if the redirectToEvents flag is set
    if (sessionStorage.getItem('redirectToEvents') === 'true') {
        // Clear the flag after use
        sessionStorage.removeItem('redirectToEvents');
        // Click the events button to switch to the events tab
        $('#events-button').trigger('click');
    }
});

let events = JSON.parse($('#events').text());
let mapApiKey = JSON.parse($('#mapApiKey').text());
console.log(mapApiKey);
let mapMarkerDetails = events?.mapMarkerDetails;
let eventList = events?.eventList;
let map, infoWindow, center;
let markers = []
let nearbyPlaces;
// let nearbyEvents = []
// Avoid importing libraries twice
let markerLibraryImported = false
let placeLibraryImported = false
let AdvancedMarkerElement, Place, SearchNearbyRankPreference, PinElement;

const mapID = '9f8b4bb546abc551'; // Need to pass from an env var
async function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: -34.397, lng: 150.644 },
        zoom: 12,
        mapId: mapID,
    })
    infoWindow = new google.maps.InfoWindow();

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
        async (position) => {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;
            currentLat = latitude;
            currentLng = longitude;
            center = {
                lat: latitude,
                lng: longitude,
            };
            // const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            console.log(timezone);
            await resendLocation(latitude, longitude, timezone);
            map.setCenter(center);
            console.log("Center confirmed");
            await nearbyPlaceSearch(map, center);
            // Dispatch the custom event when map is fully loaded
            $(document).trigger("mapReady");
            const overlay = document.getElementById('map-loading-overlay');
            if (overlay) {
                overlay.style.display = 'none';
            }
        },
        () => {
            handleLocationError(true, infoWindow, map.getCenter());
        }
        )
    } else {
        handleLocationError(false, infoWindow, map.getCenter());
    }
}

// Send location info by AJAX request and fetch event info
async function resendLocation(latitude, longitude, timezone) {
    console.log('Ready to resend location');
    disableEventsButton();
    $.ajax({
        url: "api/",  // Your Django view URL
        type: "POST",
        data: JSON.stringify({
            latitude: latitude,
            longitude: longitude,
            timezone: timezone,
        }),
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        contentType: "application/json",
        success: function (response) {
            // console.log("Location sent successfully!", response);
            events = response.events;
            // console.log(events);
            mapMarkerDetails = events?.mapMarkerDetails;
            console.log(mapMarkerDetails);
            eventList = events?.eventList;
            // console.log(eventList);
            // You can use the response to update the UI if needed
            displayEvents(eventList);
            console.log('Events updated');
        },
        error: function (error) {
            console.error("Error sending location:", error);
        },
        complete: function () {
            enableEventsButton();  // Re-enable the button after processing is complete
        }
    });  
}

// Function to search location using Google Maps Geocoding API
async function searchLocation(query) {
    const geocodeUrl = `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(query)}&key=${mapApiKey}`;
    try {
        const response = await fetch(geocodeUrl);
        const data = await response.json();
        console.log(data);
        if (data.status === "OK") {
            const { lat, lng } = data.results[0].geometry.location;
            const newCenter = { lat, lng };
            await resendLocation(lat, lng, timezone);
            map.setCenter(newCenter); // Re-center the map
            map.setZoom(12); // Optionally adjust zoom level
            await nearbyPlaceSearch(map, newCenter);
        } else {
            console.error("Geocoding error:", data.status);
            alert("Location not found. Please try again.");
        }
    } catch (error) {
        console.error("Error with the geocode request:", error);
    }
}

async function nearbyPlaceSearch(map, center) {

    // const { Place, SearchNearbyRankPreference } = await google.maps.importLibrary("places");
    // const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");
    await importPlaceLibraries();
    const request = {
        fields: ["displayName", "formattedAddress", "location", "websiteURI",
                "photos"],
        locationRestriction: {
            center: center,
            radius: 50000,
        },
        includedPrimaryTypes: ["art_gallery", "museum"],
        maxResultCount: 20,
        rankPreference: SearchNearbyRankPreference.POPULARITY,
        language: "en-US",
        region: "us",
    };
    
    try {
        const { places }  = await Place.searchNearby(request);
        console.log(places);
        nearbyPlaces = places

        if (nearbyPlaces.length) {
            console.log(nearbyPlaces);
            // To make sure that the user can see pinpoints when the map is loaded
            map.setCenter(nearbyPlaces[0].location);
            markPlaces(map, nearbyPlaces);
            displayPlaces(nearbyPlaces);
        } else {
            console.log('no results');
        }
    } catch (error) {
        console.error("Error during searchNearby request:", error);
    }
}

async function markPlaces(map, places) {
    await importMarkerLibraries();
    clearMarkers(markers);
    
    places.forEach(place => {
        // const placeId = place.id;
        // const place_name = place.displayName;
        // const place_location = place.location;
        // const images = place.images;
        // const place_images = images.map(image => image.flagContentURI);
        // console.log(place_images);
        const marker = new AdvancedMarkerElement({
            map,
            position: place.location,
        }
        )
        // console.log(place.location);
        marker.addListener('click', () => {
            displayPlaceDetails(place);
        });

        markers.push(marker);
        
    });
}

async function markEventVenues(map, mapMarkerDetails) {
    await importMarkerLibraries();
    clearMarkers(markers);

    Object.keys(mapMarkerDetails).forEach((venueId) => {
        const location = mapMarkerDetails[venueId]?.location;
        const latitude = parseFloat(location.latitude);
        const longitude = parseFloat(location.longitude);
        const position = { lat: latitude, lng: longitude };

        const marker = new AdvancedMarkerElement({
            map,
            position: position,
        });

        // On marker click, display the slide-in panel with event details
        marker.addListener('click', () => {
            displayVenueDetails(venueId);
        });

        markers.push(marker);
    });
}

function startCarousel({ containerId, images, prevButtonId, nextButtonId, indicatorsContainerId }) {
    let currentImageIndex = 0;
    const $carouselImage = $(`#${containerId} img`);

    if (!images || images.length === 0) return;

    // Set the initial image and make it visible
    $carouselImage.attr("src", images[currentImageIndex]).removeClass('opacity-0').addClass('opacity-100');

    // Function to smoothly update the displayed image
    function updateCarouselImage() {
        // Fade out
        $carouselImage.removeClass('opacity-100').addClass('opacity-0');
        
        // After fade-out, wait a bit, then fade in the next image
        setTimeout(() => {
            currentImageIndex = (currentImageIndex + 1) % images.length; // Cycle to the next image
            $carouselImage.attr("src", images[currentImageIndex]);

            // Trigger fade-in with a delay to match CSS transition timing
            setTimeout(() => {
                $carouselImage.removeClass('opacity-0').addClass('opacity-100');
            }, 50); // Adjust this delay as needed (in ms)
        }, 500); // Duration of fade-out transition (matches CSS transition)
    }

    // Navigation Buttons
    $(`#${prevButtonId}`).on("click", function() {
        currentImageIndex = (currentImageIndex === 0) ? images.length - 1 : currentImageIndex - 1;
        updateCarouselImage();
    });
    $(`#${nextButtonId}`).on("click", function() {
        currentImageIndex = (currentImageIndex + 1) % images.length;
        updateCarouselImage();
    });
}



function imageLink(name, apiKey, maxWidth, maxHeight) {
    const imageURL = `https://places.googleapis.com/v1/${name}/media?maxHeightPx=${maxHeight}&maxWidthPx=${maxWidth}&key=${mapApiKey}`;
    return imageURL;
}

function displayPlaceDetails(place) {
    $('#place-name').text(place.displayName);
    $('#place-address').text(place.formattedAddress);

    const placeImages = place.photos || [];
    const images = placeImages.map(image => imageLink(image.name, mapApiKey, 650, 400));
    console.log(images);

    startCarousel({
        containerId: "place-image-carousel",
        images: images,
        prevButtonId: "place-prev-button",
        nextButtonId: "place-next-button",
        indicatorsContainerId: "place-carousel-indicators"
    });

    loadComments(place.id);

    // Show the detail panel and hide the place list container
    $('#place-detail-panel').removeClass('translate-x-full').addClass('show');
    $('#place-list-container').addClass('hidden');
}


function displayVenueDetails(venueId) {
    // Get the venue object
    const venue = mapMarkerDetails[venueId];

    // Populate the detail panel with the venue's event data
    $('#venue-name').text(venue.placename);
    $('#venue-address').text(venue.address);

    // Clear any existing events in the detail panel
    $('#venue-events').empty();

    // Populate the event list
    venue.events.forEach(event => {
        const eventItem = `
            <div class="event-item py-4 border-b last:border-b-0">
                <h3 class="text-lg font-semibold">${event.name}</h3>
                <p class="text-gray-500">${new Date(event.date_time).toLocaleString()}</p>
                <a href="${event.url}" target="_blank" class="text-sky-800 underline">Event Details</a>
            </div>`;
        $('#venue-events').append(eventItem);
    });

    const venueImages = venue.images;
    startCarousel({
        containerId: "venue-image-carousel",
        images: venueImages,
        prevButtonId: "venue-prev-button",
        nextButtonId: "venue-next-button",
        indicatorsContainerId: "venue-carousel-indicators"
    });

    $('#venue-detail-panel').removeClass('translate-x-full').addClass('show');
    $('#place-list-container').addClass('hidden');
}

// Handle 'Go Back' button to slide out the detail panel and return to the place list
$('#venue-back-button').click(function() {
    $('#venue-detail-panel').removeClass('show').addClass('translate-x-full');
    $('#place-list-container').removeClass('hidden');
});

$('#place-back-button').click(function() {
    $('#place-detail-panel').removeClass('show').addClass('translate-x-full');
    $('#place-list-container').removeClass('hidden');
});




function clearMarkers(markerArray) {
    markerArray.forEach((marker) => {
        marker.map = null; // This clears the marker from the map
    });
    markerArray.length = 0; // Empty the array
    }

function displayPlaces(places) {
    const $placesList = $("#places-list");
    const $noPlacesMessage = $("#no-places-message");
    const searchInput = document.getElementById("location-search");
    $placesList.empty();  // Clear any existing content

    if (places.length === 0) {
        $noPlacesMessage.removeClass('hidden');  // Show "No places" message
        searchInput.setAttribute("autofocus", "");
    } else {
        $noPlacesMessage.addClass('hidden');
        searchInput.removeAttribute("autofocus");
        places.forEach(place => {
            // Create place container
            const $placeContainer = $("<div>").addClass("py-4 border-b last:border-b-0");
  
            // Text container to hold info about the place
            const $textContainer = $("<div>").addClass("flex justify-between items-start mb-4");
    
            // Image container for place image
            const $imageContainer = $("<div>").addClass("w-full h-48 bg-gray-200 rounded-lg overflow-hidden");
    
            // Info container with place name and address
            const $infoContainer = $("<div>").addClass("flex-1 pr-4");
            ($infoContainer).on('click', () => {
                displayPlaceDetails(place);
            });
            $infoContainer.on('mouseenter', () => {
                $infoContainer.css('cursor', 'pointer');
            });
    
            const $buttonContainer = $("<div>").addClass("flex flex-col items-end space-y-2");
    
            // Create elements for name, location, and description
            const $nameElement = $("<h4>")
                .addClass("text-xl font-semibold text-gray-800 leading-none mb-3")
                .text(place.displayName);
    
            const $locationElement = $("<p>")
                .addClass("text-sm text-gray-400 leading-tight")
                .text(place.formattedAddress);
    
            const $websiteLinkElement = $("<a>")
                .text("Visit Website")
                .attr("href", place.websiteURI)
                .attr("target", "_blank")
                .attr("rel", "noopener noreferrer")
                .addClass("bg-slate-600 text-white text-center text-xs font-medium py-2 px-4 rounded hover:bg-slate-800");
    
            $buttonContainer.append($websiteLinkElement);
    
            // If user is logged in, add 'Add to Favorites' button
            if (isUserLoggedIn) {
                const $addFavoritesButton = $("<button>")
                    .addClass("add-favorite-place-btn text-center bg-emerald-600 text-white text-xs font-medium py-2 px-4 rounded hover:bg-emerald-800")
                    .text("Add to Favorites")
                    .data({
                        "place_id": place.id,
                        "place_name": place.displayName,
                        "place_address": place.formattedAddress,
                        "place_website": place.websiteURI,
                        "place_longitude": place.location.lng(),
                        "place_latitude": place.location.lat(),
                    });
                $buttonContainer.append($addFavoritesButton);
            }
    
            // Image element for the place
            const $imageElement = $("<img>")
                .addClass("object-cover w-full h-full")
                .attr("src", place.photos[0].getURI({ maxHeight: 400 }))
                .attr("alt", place.displayName);
    
            $imageContainer.append($imageElement);
    
            // Append elements to their containers
            $infoContainer.append($nameElement).append($locationElement);
            $textContainer.append($infoContainer).append($buttonContainer);
            $placeContainer.append($textContainer).append($imageContainer);
    
            // Append place container to places list
            $placesList.append($placeContainer);
        });
        updateFavoritePlaceButtons(favoritePlaces);
    }

}
    

function displayEvents(eventList) {
    const $eventsList = $('#events-list');
    const $noEventsMessage = $("#no-events-message");
    const searchInput = document.getElementById("location-search");

    // Clear the existing events before appending new ones
    $eventsList.empty();
    // console.log(eventList);

    if (eventList.length === 0) {
        $noEventsMessage.removeClass('hidden');  // Show "No events" message
        searchInput.setAttribute("autofocus", "");  // Set autofocus to guide the user
    } else {
        $noEventsMessage.addClass('hidden');  // Hide the message if there are events
        searchInput.removeAttribute("autofocus");
        eventList.forEach(event => {

            const $eventCard = $('<div>').addClass('event-card p-4 mb-4 bg-white shadow-md rounded-lg');
    
            const $textContainer = $('<div>').addClass('justify-between items-start mb-4');
            const $title = $('<h4>').addClass('text-xl font-semibold text-gray-800 leading-none mb-3').text(event.eventname);
            const $placeName = $('<p>').addClass('text-md text-gray-700 mb-2').text(event.placename);
            const $address = $('<p>').addClass('text-sm text-gray-500 mb-4').text(event.address);
            $textContainer.append($title).append($placeName).append($address);
    
            const $timeSlotsContainer = $('<div>').addClass('time-slots mb-2');
            // console.log(typeof event);
            // console.log(event);
            const timeSlots = event.eventdates;
            Object.keys(timeSlots).forEach(timeSlot => {
                if (timeSlot !== '') {
                    const $slotItem = $('<div>').addClass('flex w-full justify-between items-center mb-1');
                    
                    // Left-aligned time text
                    const $slotTime = $('<span>').addClass('text-sm text-slate-600 my-2').text(timeSlot);
                    
                    // Right-aligned button container
                    const $buttonContainer = $('<div>').addClass('flex space-x-2');
            
                    const $ticketButton = $('<a>')
                        .addClass('bg-slate-600 text-white text-xs font-medium py-2 px-4 rounded hover:bg-slate-800')
                        .attr('href', timeSlots[timeSlot][1])
                        .attr('target', '_blank')
                        .text('Tickets');
                    
                    $buttonContainer.append($ticketButton);
            
                    if (isUserLoggedIn) {
                        const $saveEventButton = $('<button>')
                        .addClass('save-event-btn bg-emerald-600 text-white text-xs font-medium py-2 px-4 rounded hover:bg-emerald-800')
                        .text('Save')
                        .data({
                            'event_id': timeSlots[timeSlot][0],
                            'event_name': event.eventname,
                            'event_venue': event.placename,
                            'event_venue_id': event.venue_id,
                            'event_address': event.address,
                            'event_start_time': event.date_time, 
                            // Send back UTC standard instead of local time,
                            // as the user might retrieve the data in a different timezone later
                            'event_url': timeSlots[timeSlot][1],
                        });
                        $buttonContainer.append($saveEventButton);
                    }
            
                    // Append the time and button container to the main item container
                    $slotItem.append($slotTime).append($buttonContainer);
                    $timeSlotsContainer.append($slotItem);
                }
            });
            
            
            $eventCard.append($textContainer).append($timeSlotsContainer);
            $eventsList.append($eventCard);
        })
    
        updateFavoriteEventButtons(favoriteEvents); 
    }



}

async function importPlaceLibraries() {
    if(!placeLibraryImported) {
        const {Place : importedPlace, SearchNearbyRankPreference : importedRank} = await google.maps.importLibrary('places');
        Place = importedPlace;
        SearchNearbyRankPreference = importedRank;
        placeLibraryImported = true;
        console.log('Place Libraries Imported');
    }
}

async function importMarkerLibraries() {
    if(!markerLibraryImported) {
        const {AdvancedMarkerElement : importedMarker, PinElement : importedPinElement} = await google.maps.importLibrary('marker');
        AdvancedMarkerElement = importedMarker;
        PinElement = importedPinElement;
        markerLibraryImported = true;
    }
}

function handleLocationError(browserHasGeolocation, infoWindow, pos) {
    infoWindow.setPosition(pos);
    infoWindow.setContent(
        browserHasGeolocation
            ? "Error: The Geolocation service failed."
            : "Error: Your browser doesn't support geolocation",
    );
    infoWindow.open(map);
}

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

// Update place buttons based on favorites
function updateFavoritePlaceButtons(favoritePlaces) {
    $('.add-favorite-place-btn').each(function() {
        // console.log(favoritePlaces);
        const placeId = $(this).data('place_id');
        if (favoritePlaces.includes(placeId)) {
            $(this).addClass('bg-red-800 hover:bg-red-900').text('Remove Favorites');
        } else {
            $(this).removeClass('bg-red-800 hover:bg-red-900').text('Add to Favorites');
        }
    });
}

function updateFavoriteEventButtons(favoriteEvents) {
    $('.save-event-btn').each(function() {
        // console.log('Favorite events buttons checked');
        const eventId = $(this).data('event_id');
        if (favoriteEvents.includes(eventId)) {
            $(this).addClass('bg-red-800 hover:bg-red-900').text('Remove');
        } else {
            $(this).removeClass('bg-red-800 hover:bg-red-900').text('Save');
        }
    });
}

// async function checkLocationAccess() {
//     if (navigator.permissions) {
//         const status = await navigator.permissions.query({ name: 'geolocation' });
        
//         if (status.state === 'granted' && !mapInitialized) {
//             // If permission is granted and map is not yet initialized
//             initMap();
//             mapInitialized = true;
//         } else if (status.state === 'prompt' && !mapInitialized) {
//             // If the permission is promptable, try loading map and set mapInitialized
//             initMap();
//             mapInitialized = true;
//         } else if (status.state === 'denied') {
//             // Show modal only if location is persistently denied
//             showLocationModal();
//         }
//     } else {
//         // Fallback if permissions API isn't supported
//         initMap();
//     }
// }

// // Show location modal
// function showLocationModal() {
//     $('#location-modal').removeClass('hidden');
//     $('#places-unavailable, #events-unavailable').removeClass('hidden');
// }

// // Retry location access on button click
// $('#allow-location-btn').on('click', function() {
//     $('#location-modal').addClass('hidden');
//     checkLocationAccess(); // Re-check location permissions
// });

// $(document).ready(async function() {
//     await checkLocationAccess();
//     console.log('Location access checked');
// });
// Helper functions to disable and enable the Events button
function disableEventsButton() {
    const eventsButton = $('#events-button');
    eventsButton.prop('disabled', true);
    eventsButton.addClass('bg-stone-300 text-gray-950 cursor-not-allowed'); // Gray out for disabled effect
    eventsButton.removeClass('bg-gray-300 text-gray-800 hover:bg-gray-400');
}

function enableEventsButton() {
    const eventsButton = $('#events-button');
    eventsButton.prop('disabled', false);
    eventsButton.removeClass('bg-stone-300 text-gray-950 cursor-not-allowed');
    eventsButton.addClass('bg-gray-300 text-gray-800 hover:bg-gray-400');
}

function loadComments(placeId) {
    $.get(`/api/v1/map/api/comments/${placeId}/`, function (data) {
        const { user_comment, other_comments} = data.comments;
        // Display user's comment
        const $userCommentSection = $('#user-comment');
        $userCommentSection.empty();
        if (user_comment) {
            const userCommentHtml = `
                <div class="p-4 border rounded bg-blue-50">
                    <strong>You</strong>
                    <p>${user_comment.comment}</p>
                    <div class="flex items-center">
                        <span class="text-gray-500 ml-auto text-sm">
                            Updated at: ${new Date(user_comment.updated_at).toLocaleString()}
                        </span>
                    </div>
                    <div class="flex justify-end">
                        <button id="edit-button" class="text-sky-800 font-semibold underline mx-3">Edit</button>
                        <button id="delete-button" class="text-sky-800 font-semibold underline">Delete</button>
                    </div>
                </div>
            `;
            
            $userCommentSection.html(userCommentHtml);
            $('#publish-comment').addClass('hidden');
            $('#edit-button').on('click', function () {
                $('#edit-text').val('');
                $('#edit-comment').removeClass('hidden');
            })

            $('#delete-button').on('click', function () {
                deleteUserComment(placeId);
            })

        } else if (isUserLoggedIn && !user_comment) {
            $userCommentSection.html('<p class="text-gray-500 mb-2">You don\'t have any comments yet.</p>');
            $('#publish-comment').removeClass('hidden');
        }

        // Display other comments
        const $commentsList = $('#comments-list');
        $commentsList.empty();
        other_comments.forEach(comment => {
            const commentHtml = `
                <li class="p-4 border rounded">
                    <strong>${comment.alias}</strong>
                    <p>${comment.comment}</p>
                    <div class="flex items-center">
                        <span class="text-gray-500 ml-auto text-sm">
                            Updated at: ${new Date(comment.updated_at).toLocaleString()}
                        </span>
                    </div>
                </li>
            `;
            $commentsList.append(commentHtml);
        });
    });
    // Submit comment and rating
    $('#submit-comment-btn').on('click', function () {
        if (!isUserLoggedIn) {
            alert('You need to log in to post a comment.');
        }

        const comment = $('#comment-text').val();

        if (!comment) {
            alert('Please add a comment.');
        }

        $.ajax({
            url: '/api/v1/map/api/comments/add/',
            type: 'POST',
            data: JSON.stringify({ place_id: placeId, comment: comment}),
            contentType: 'application/json',
            headers: { 'X-CSRFToken': getCookie('csrftoken') },
            success: function () {
                const newCommentHtml = `
                    <div class="p-4 border rounded bg-blue-50">
                        <strong>You</strong>
                        <p>${comment}</p>
                        <div class="flex items-center">
                            <span class="text-gray-500 ml-auto text-sm">Just now</span>
                        </div>
                        <div class="flex justify-end">
                            <button id="edit-button" class="text-sky-800 font-semibold underline mx-3">Edit</button>
                            <button id="delete-button" class="text-sky-800 font-semibold underline">Delete</button>
                        </div>
                    </div>
                `;
                $('#user-comment').html(newCommentHtml);
                $('#comment-text').val('');
                $('#publish-comment').addClass('hidden');
            },
        });
    });

    $('#edit-comment-btn').on('click', function () {
        const commentText = $('#edit-text').val();

        $.ajax({
            url: 'api/comments/add/',
            type: 'POST',
            data: JSON.stringify({ place_id: placeId, comment: commentText }),
            contentType: 'application/json',
            headers: { 'X-CSRFToken': getCookie('csrftoken') },
            success: function(response) {
                const newCommentHtml = `
                    <div class="p-4 border rounded bg-blue-50">
                        <strong>You</strong>
                        <p>${commentText}</p>
                        <div class="flex items-center">
                            <span class="text-gray-500 ml-auto text-sm">Just now</span>
                        </div>
                        <div class="flex justify-end">
                            <button id="edit-button" class="text-sky-800 font-semibold underline mx-3">Edit</button>
                            <button id="delete-button" class="text-sky-800 font-semibold underline">Delete</button>
                        </div>
                    </div>
                `;
                $('#user-comment').html(newCommentHtml);
                $('#publish-comment').addClass('hidden');
                $('#edit-comment').addClass('hidden');
            },
            error: function(error) {
                console.error('Error adding comment:', error);
            }
        });
    })

    $('#cancel-comment-btn').on('click', function () {
        $('#edit-comment').addClass('hidden');
        $('#edit-text').val('');
    })
}


// Function to delete a user's comment
function deleteUserComment(placeId) {
    $.ajax({
        url: 'api/comments/delete/',
        type: 'POST',
        data: JSON.stringify({ place_id: placeId }),
        contentType: 'application/json',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        success: function(response) {
            $('#publish-comment').removeClass('hidden');
            $('#edit-comment').addClass('hidden');
            $('#user-comment').addClass('hidden').empty();
            $('#comment-text').val(''); // Reset the text box
        },
        error: function(error) {
            console.error('Error deleting comment:', error);
        }
    });
}


document.addEventListener("mapReady", function() {
    // Check if the redirectToEvents flag is set
    if (sessionStorage.getItem('redirectToEvents') === 'true') {
        // Clear the flag after use
        sessionStorage.removeItem('redirectToEvents');
        // Click the events button to switch to the events tab
        document.getElementById('events-button').click();
    }
});

window.onload = initMap;
console.log("map loaded");
