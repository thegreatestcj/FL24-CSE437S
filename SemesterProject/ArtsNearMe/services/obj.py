from typing import Optional, List, Dict

class Event:
    def __init__(
        self, name: str, 
        venue_id: str,
        event_id: str,
        url: Optional[str] = None,
        date_time: Optional[str] = None, 
        date_time_str: Optional[str] = None,
        ):

        self.name = name
        self.event_id = event_id
        self.date_time = date_time
        self.url = url
        self.venue_id = venue_id
        self.date_time_str = date_time_str

    def to_dict(self):
        return {
            "name": self.name,
            "event_id": self.event_id,
            "date_time": self.date_time,
            "url": self.url,
            "date_time_str": self.date_time_str,
            "venue_id": self.venue_id,
        }

class EventVenue: # For items in the Events List
    def __init__(
        self,
        event_venue: str,
        eventname: str,
        date_time: str,
        venue_id: str,
        date_time_str: Optional[str] = None,
        images: Optional[List[str]] = None,  # Optional field with type hint
        placename: Optional[str] = None,  # Optional field with type hint
        address: Optional[str] = None,  # Optional field with type hint
        eventdates: Optional[Dict[str, List[str]]] = None, # List[0] is event_id, [1] is url
    ):

        self.event_venue = event_venue
        self.eventname = eventname
        self.date_time = date_time
        self.date_time_str = date_time_str
        self.images = images if images is not None else []  # Default to empty list if None
        self.venue_id = venue_id
        self.placename = placename
        self.address = address
        self.eventdates = eventdates if eventdates is not None else {}

    def to_dict(self):
        return {
            "event_venue": self.event_venue,
            "eventname": self.eventname,
            "date_time": self.date_time,
            "venue_id": self.venue_id,
            "date_time_str": self.date_time_str,
            "images": self.images,
            "placename": self.placename,
            "address": self.address,
            "eventdates": self.eventdates
        }

class MapMarker: # For unique venues that pop up on the map when user opens the Events view
    def __init__(
        self,
        venue_id: str,
        placename: str,
        address: Optional[str] = None,
        location: Optional[Dict[str, float]] = None,
        events: Optional[List[Event]] = None,  # List of Event objects
        images: Optional[List[str]] = None,
    ):
        self.venue_id = venue_id
        self.placename = placename
        self.address = address
        self.location = location if location is not None else {}
        self.events = events if events is not None else []
        self.images = images if images is not None else []

    def add_event(self, event: Event):
        """Add an Event object to this venue's list of events."""
        self.events.append(event)

    def add_image(self, image: str):
        self.images.append(image)

    def to_dict(self):
        return {
            "venue_id": self.venue_id,
            "placename": self.placename,
            "address": self.address,
            "location": self.location,
            "events": [event.to_dict() for event in self.events]  # Serialize each event
        }
