import PlacesMap from '../Components/PlacesMap';
import { useState } from 'react';
import './Explore.css';
import CitySearch from '../Components/CitySearch';

const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001';

function Explore() {
    const [city, setCity] = useState('');
    const [citySearched, setCitySearched] = useState('');
    const [places, setPlaces] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    async function fetchPlaces(selectedCity) {
        if (!selectedCity.trim()) return;

        setCitySearched(selectedCity);
        setLoading(true);
        setError('');
        setPlaces([]);

        try {
            const query = encodeURIComponent(
                `Things to do in ${selectedCity}`
            );

            const response = await fetch(
                `${API_BASE_URL}/api/places/search?query=${query}`
            );

            if (!response.ok) {
                throw new Error('Failed to retrieve places');
            }

            const data = await response.json();

            console.log('Places API response:', data);

            setPlaces(data.places || []);
        } catch (err) {
            console.error(err);
            setError('Unable to retrieve places. Please try again.');
        } finally {
            setLoading(false);
        }
    }

    function handlingSearches(event) {
        event.preventDefault();
        fetchPlaces(city.trim());
    }

    return (
        <main className="explore">
            <h1 className="explore-title">Explore</h1>

            <p className="explore-subtitle">
                Find what the locals love, wherever you're headed!
            </p>

            <form className="search-bar" onSubmit={handlingSearches}>
                <CitySearch
                    value={city}
                    onChange={setCity}
                    onSelect={(c) =>
                        fetchPlaces(`${c.city}, ${c.state}`)
                    }
                />

                <button
                    type="submit"
                    className="search-button"
                    disabled={loading}
                >
                    {loading ? 'Searching...' : 'Search'}
                </button>
            </form>

            {citySearched && (
                <p className="search-result">
                    Showing local spots in
                    <strong> {citySearched}</strong>
                </p>
            )}

            {loading && <p>Loading places...</p>}
            {error && <p>{error}</p>}

            {!loading && !error && citySearched &&
                places.length === 0 && <p>No places found.</p>}
            {places.length > 0 && (
                <PlacesMap places={places} />
            )}
            <div className="places-results">
                {places.map((place) => (
                    <div key={place.id} className="place-card">
                        <h3>{place.name}</h3>
                        <p>{place.address}</p>
                        <p>Latitude: {place.location?.lat}</p>
                        <p>Longitude: {place.location?.lng}</p>
                    </div>
                ))}
            </div>
        </main>
    );
}

export default Explore;
