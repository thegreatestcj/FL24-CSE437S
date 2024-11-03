from rest_framework import serializers
from .services import * 

class EventSerializer(serializers.Serializer):
    name = serializers.CharField()
    date_time = serializers.CharField()
    url = serializers.URLField()
    venue_id = serializers.CharField()
    event_id = serializers.CharField()
    date_time_str = serializers.CharField(required=False, allow_null=True)

    def to_representation(self, instance):
        # Convert Event instance to a dictionary using its `to_dict` method
        return instance.to_dict()

class EventVenueSerializer(serializers.Serializer):
    event_venue = serializers.CharField()
    eventname = serializers.CharField()
    date_time = serializers.CharField()
    venue_id = serializers.CharField()
    date_time_str = serializers.CharField(required=False, allow_null=True)
    images = serializers.ListField(child=serializers.URLField(), required=False)
    placename = serializers.CharField(required=False, allow_null=True)
    address = serializers.CharField(required=False, allow_null=True)
    eventdates = serializers.DictField(
    child=serializers.ListField(
        child=serializers.CharField(),
        min_length=2,
        max_length=2
    ),
    required=False,
    allow_null=True
)

    def to_representation(self, instance):
        # Use instance's to_dict method to generate a dictionary representation
        return instance.to_dict()

class MapMarkerSerializer(serializers.Serializer):
    venue_id = serializers.CharField()
    placename = serializers.CharField()
    address = serializers.CharField(required=False, allow_null=True)
    location = serializers.DictField(child=serializers.FloatField(), required=False)
    events = EventSerializer(many=True)
    images = serializers.ListField(
    child=serializers.URLField(), required=False, allow_empty=True
)

    def to_representation(self, instance):
        # Ensure all fields, including images, are included
        representation = instance.to_dict()
        representation['images'] = getattr(instance, 'images', [])
        return representation