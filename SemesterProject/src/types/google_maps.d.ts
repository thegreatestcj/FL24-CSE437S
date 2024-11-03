// src/types/google-maps.d.ts
declare namespace google {
    export namespace maps {
        // Declare importLibrary function
        function importLibrary(name: string): Promise<any>;

        // Declare types for specific libraries or features you need
        interface Place {
            searchNearby(request: any): Promise<{ places: Place[] }>;
        }

        enum SearchNearbyRankPreference {
            DEFAULT = "default",
            POPULARITY = "popularity",
            DISTANCE = "distance"
        }

        interface AdvancedMarkerElement {
            new (options: any): AdvancedMarkerElement;
        }

        interface PinElement {
            new (options: any): PinElement;
        }
    }
}
