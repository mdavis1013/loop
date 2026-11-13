import { useState, useEffect} from 'react';
import './Explore.css';
import CitySearch from '../Components/CitySearch';
const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001/api';

function Explore() {
    /*
        city - holds what is in the search box
        setCity - how you change it
        citySearched - holding the city that the user is looking for
    */
    const [city, setCity] = useState('');
    const [citySearched, setCitySearched] = useState('');
    const [places, setPlaces] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    function handlingSearches(event) {
        event.preventDefault();
        setCitySearched(city.trim() /* trim() - removing extra space */); 
    }

    // Whenever a city is searched, ask the backend for places there
    useEffect(() => {
        if (!citySearched) return;
        let ignore = false;

        async function loadPlaces() {
            setLoading(true);
            setError('');
            try {
                const query = encodeURIComponent(`things to do in ${citySearched}`);
                const response = await fetch(
                    `${API_BASE_URL}/places/search?query=${query}`
                );
                const data = await response.json();
                if (!response.ok) {
                    throw new Error(data.message || 'Could not load places.');
                }
                if (!ignore) setPlaces(data.places);
            } catch (err) {
                if (!ignore) {
                    setPlaces([]);
                    setError(
                        err instanceof TypeError
                            ? 'Issue connecting to the server.'
                            : err.message
                    );
                }
            } finally {
                if (!ignore) setLoading(false);
            }
        }

        loadPlaces();
        return () => { ignore = true; };
    }, [citySearched]);


    return (
        <main className="explore">
            <h1 className="explore-title">Explore</h1>
            <p className="explore-subtitle">Find what the locals love, wherever you're headed!</p>

            <form className="search-bar" onSubmit={handlingSearches}>
                <CitySearch value={city} onChange={setCity} />
                <button type="submit" className="search-button">Search</button>
            </form>

            {citySearched && (
                <p className="search-result">Showing local spots in <strong>{citySearched}</strong></p>
            )}

            {loading && <p>Loading places...</p>}
            {error && <p role="alert">{error}</p>}
            {!loading && !error && places.length > 0 && (
                <ul className="places-list">
                    {places.map((place) => (
                        <li key={place.id}>
                            <strong>{place.name}</strong>
                            <br />
                            {place.address}
                        </li>
                    ))}
                </ul>
            )}
        </main>
    );
}


export default Explore;