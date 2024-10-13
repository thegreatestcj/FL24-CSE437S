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
        markEventVenues(map, mapMarkerDetails);
    });
    // We don't need to trigger list display functions,
    // as list data has been fetched when the map is loaded,
    // we're just going to toggle the list container hidden/unhidden.
});

let events = JSON.parse($('#events').text());
// console.log(events)
let mapMarkerDetails = events?.mapMarkerDetails;
let eventList = events?.eventList;
console.log(mapMarkerDetails);
console.log(eventList);
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
        zoom: 13,
        mapId: mapID,
    })
    infoWindow = new google.maps.InfoWindow();

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
        async (position) => {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;
            center = {
                lat: latitude,
                lng: longitude,
            };
            $.ajax({
                url: "/api/map/",  // Your Django view URL
                type: "POST",
                data: JSON.stringify({
                    latitude: latitude,
                    longitude: longitude,
                }),
                contentType: "application/json",
                success: function (response) {
                    console.log("Location sent successfully!", response);
                    events = response.events;
                    // console.log(events);
                    mapMarkerDetails = events?.mapMarkerDetails;
                    // console.log(mapMarkerDetails);
                    eventList = events?.eventList;
                    // console.log(eventList);
                    // You can use the response to update the UI if needed
                    displayEvents(eventList);
                    console.log('Events displayed');
                },
                error: function (error) {
                    console.error("Error sending location:", error);
                }
            });
            map.setCenter(center);
            console.log("Center confirmed");
            await nearbyPlaceSearch(map, center);
        },
        () => {
            handleLocationError(true, infoWindow, map.getCenter());
        }
        )
    } else {
        handleLocationError(false, infoWindow, map.getCenter());
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
        maxResultCount: 8,
        // rankPreference: SearchNearbyRankPreference.POPULARITY,
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
        const marker = new AdvancedMarkerElement({
            map,
            position: place.location,
        }
        )
        // console.log(place.location);
        markers.push(marker);
    });
}

async function markEventVenues(map, mapMarkerDetails) {
    await importMarkerLibraries();
    clearMarkers(markers);
    Object.keys(mapMarkerDetails).forEach((venueId) => {
        // Reformat the coordinates in Google Maps API style
        const location = mapMarkerDetails[venueId]?.location;
        const latitude = parseFloat(location.latitude);
        const longitude = parseFloat(location.longitude);
        const position = { lat: latitude, lng: longitude };
        // console.log(position);
        console.log(mapMarkerDetails[venueId]?.address)
        const marker = new AdvancedMarkerElement({
            map,
            position: position,
        })
        markers.push(marker);
    });
}

function clearMarkers(markerArray) {
    markerArray.forEach((marker) => {
        marker.map = null; // This clears the marker from the map
    });
    markerArray.length = 0; // Empty the array
    }

function displayPlaces(places) {
    const placesList = document.getElementById("places-list");
    places.forEach(place => {
        // Create a container for each place
        const placeContainer = document.createElement("div");
        placeContainer.className = "py-4 border-b last:border-b-0";

        const textContainer = document.createElement("div");
        textContainer.className = "flex justify-between items-start mb-4"

        const imageContainer = document.createElement("div");
        imageContainer.className = "w-full h-48 bg-gray-200 rounded-lg overflow-hidden"

        const infoContainer = document.createElement("div");
        infoContainer.className = "flex-1 pr-4";

        const buttonContainer = document.createElement("div");
        buttonContainer.className = "flex flex-col items-end space-y-2";

        // Create elements for name, location, and description
        const nameElement = document.createElement("h4");
        nameElement.className = "text-xl font-semibold text-gray-800 leading-none mb-3";
        nameElement.textContent = place.displayName;

        const locationElement = document.createElement("p");
        locationElement.className = "text-sm text-gray-400 leading-tight";
        locationElement.textContent = place.formattedAddress;

        const websiteLinkElement = document.createElement("a");
        websiteLinkElement.textContent = "Visit Website";
        websiteLinkElement.href = place.websiteURI;
        websiteLinkElement.target = "_blank";
        websiteLinkElement.rel = "noopener noreferrer";
        websiteLinkElement.className = "bg-slate-600 text-white text-xs font-medium py-2 px-4 rounded hover:bg-slate-800";
        buttonContainer.appendChild(websiteLinkElement);

        if (isUserLoggedIn) {
            const addFavoritesElement = document.createElement("button");
            addFavoritesElement.className = "bg-green-500 text-white text-xs font-medium py-2 px-4 rounded hover:bg-green-600";
            addFavoritesElement.textContent = "Add to Favorites";
            buttonContainer.appendChild(addFavoritesElement);
        }

        // const iconContainer = document.createElement("div");
        // iconContainer.className = "icon-frame";
        // const iconElement = document.createElement("img");
        // iconElement.src = place.svgIconMaskURI;
        // iconElement.alt = place.displayName;
        // iconContainer.appendChild(iconElement);
        // const descriptionElement = document.createElement("p");
        // descriptionElement.className = "text-gray-500";
        // descriptionElement.textContent = place.description;
        const imageElement = document.createElement("img");
        imageElement.className = "object-cover w-full h-full";
        imageElement.src = place.photos[0].getURI({maxHeight: 400});
        imageElement.alt = place.displayName;
        imageContainer.appendChild(imageElement);
        // Append elements to the place container
        infoContainer.appendChild(nameElement);
        infoContainer.appendChild(locationElement);

        buttonContainer.appendChild(websiteLinkElement);
        // placeContainer.appendChild(descriptionElement);
        textContainer.appendChild(infoContainer);
        textContainer.appendChild(buttonContainer);

        placeContainer.appendChild(textContainer);
        placeContainer.appendChild(imageContainer);
        // placeContainer.appendChild(iconContainer);
        // Append the place container to the places list
        placesList.appendChild(placeContainer);
    });
}

function displayEvents(eventList) {
    const $eventsList = $('#events-list');
    console.log(eventList);

    Object.keys(eventList).forEach(event => {

        const $eventCard = $('<div>').addClass('event-card p-4 mb-4 bg-white shadow-md rounded-lg');

        const $textContainer = $('<div>').addClass('justify-between items-start mb-4');
        const $title = $('<h4>').addClass('text-xl font-semibold text-gray-800 leading-none mb-3').text(eventList[event].eventname);
        const $placeName = $('<p>').addClass('text-md text-gray-700 mb-2').text(eventList[event].placename);
        const $address = $('<p>').addClass('text-sm text-gray-500 mb-4').text(eventList[event].address);
        $textContainer.append($title).append($placeName).append($address);

        const $timeSlotsContainer = $('<div>').addClass('time-slots mb-4');
        // console.log(typeof event);
        // console.log(event);
        const timeSlots = eventList[event].start_dates;
        console.log(timeSlots);
        // console.log(typeof timeSlots);
        Object.keys(timeSlots).forEach(timeSlot => {
            if (timeSlot !== 'N/A') {
                const $slotItem = $('<div>').addClass('flex w-full justify-between items-center mb-1');
            
                const $slotTime = $('<span>').addClass('text-xs text-slate-600 my-2').text(timeSlot);
                const $ticketButton = $('<a>').addClass('bg-slate-600 text-white text-xs font-medium py-2 px-4 rounded hover:bg-slate-800')
                    .attr('href', timeSlots[timeSlot]).attr('target', '_blank')
                    .text('Tickets');
                $slotItem.append($slotTime).append($ticketButton);

                if(isUserLoggedIn) {
                    const $saveButton = $('<button>').addClass('bg-green-500 text-white px-3 py-1 rounded')
                        .text('Save');
                    $slotItem.append($saveButton);
                }

                $timeSlotsContainer.append($slotItem);
            }
        })
        
        $eventCard.append($textContainer).append($timeSlotsContainer);
        $eventsList.append($eventCard);
    })

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

window.onload = initMap;
console.log("map loaded");