import { useState } from 'react';
import './Explore.css';

function Explore() {
    /*
        city - holds what is in the search box
        setCity - how you change it
        citySearched - holding the city that the user is looking for
    */
    const [city, setCity] = useState('');
    const [citySearched, setCitySearched] = useState('');
    function handlingSearches(event) {
        event.preventDefault();
        setCitySearched(city.trim() /* trim() - removing extra space */); 
    }

    return (
        <main className="explore">
            <h1 className="explore-title">Explore</h1>
            <p className="explore-subtitle">Find what the locals love, wherever you're headed!</p>

            <form className="search-bar" onSubmit={handlingSearches}>
                <input type="text" className="search-input" placeholder="Search a city... " value={city} onChange={(event) => setCity(event.target.value)}/>
                <button type="submit" className="search-button">Search</button>
            </form>

            {citySearched && (
                <p className="search-result">Showing local spots in <strong>{citySearched}</strong></p>
            )}
        </main>
    );
}


export default Explore;