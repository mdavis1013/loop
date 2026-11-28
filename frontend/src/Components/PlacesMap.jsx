import { useEffect } from 'react';
import {
    MapContainer,
    TileLayer,
    Marker,
    Popup,
    useMap
} from 'react-leaflet';

import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './PlacesMap.css';

import {
    CATEGORIES,
    getPlaceCategory
} from '../Utilities/PlaceCategories';
import PlacePreviewCard from './PlacePreviewCard';

function createPin(category) {
    return L.divIcon({
        className: 'custom-marker',
        html: `
            <div class="category-pin"
                 style="background-color: ${category.color}">
                <span>${category.icon}</span>
            </div>
        `,
        iconSize: [36, 36],
        iconAnchor: [18, 36],
        popupAnchor: [0, -36]
    });
}

const categoryIcons = Object.fromEntries(
    Object.entries(CATEGORIES).map(([key, category]) => [
        key,
        createPin(category)
    ])
);

function MapBounds({ places }) {
    const map = useMap();

    useEffect(() => {
        if (places.length === 0) return;

        const coordinates = places.map((place) => [
            place.location.lat,
            place.location.lng
        ]);

        map.fitBounds(coordinates, {
            padding: [50, 50],
            maxZoom: 14
        });
    }, [places, map]);

    return null;
}

function PlacesMap({ places = [] }) {
    const validPlaces = places.filter(
        (place) =>
            Number.isFinite(place.location?.lat) &&
            Number.isFinite(place.location?.lng)
    );

    return (
        <MapContainer
            center={[29.6516, -82.3248]}
            zoom={12}
            className="places-map"
        >
            <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            <MapBounds places={validPlaces} />

            {validPlaces.map((place) => (
                <Marker
                    key={place.id}
                    position={[
                        place.location.lat,
                        place.location.lng
                    ]}
                    icon={categoryIcons[getPlaceCategory(place)]}
                >
                    <Popup>
                         <PlacePreviewCard place={place} />
                    </Popup>
                </Marker>
            ))}
        </MapContainer>
    );
}

export default PlacesMap;
