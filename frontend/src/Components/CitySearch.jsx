/* ====== CREATING THE AUTOCOMPLETE ======*/ 
import { useState } from 'react';

const CITIES = [
    {city: "Gainesville", state: "FL"}, 
    {city: "Miami", state: "FL"},
    {city: "Tampa", state: "FL"}, 
    {city: "Orlando", state: "FL"},
    {city: "Lakeland", state: "FL"},
    {city: "Ocala", state: "FL"},
    {city: "Lake Wales", state: "FL"},
    {city: "Tallahassee", state: "FL"},
    {city: "St. Petersburg", state: "FL"},
    {city: "Naples", state: "FL"},
    {city: "Ft. Lauderdale", state: "FL"}
]

export default function CitySearch({value, onChange, onSelect}) {
    //const [query, setQuery] = useState(""); (NOW EXPLORE HAS IT)
    const [open, setOpen] = useState(false); 

    // MAKE SUGGESTIONS BELOW - FILTERING
    const qu = value.trim().toLowerCase();
    let suggestions = [];
    if (qu) {
        for (const c of CITIES) {
            if (c.city.toLocaleLowerCase().startsWith(qu)) {
                suggestions.push(c);
            }
        }
    } 
    //picking a city
    function choosingCity(c) {
        onChange(`${c.city}, ${c.state}`); 
        setOpen(false);
        if (onSelect) onSelect(c); //telling Explore that a city was picked
    }

    return (
        <div className="city-search">
            <input 
                type="text" 
                className="search-input" 
                placeholder="Search a city..." 
                value={value} 
                onChange={(e) => {onChange(e.target.value); setOpen(true);}}
                onBlur={() => setOpen(false)}
                onKeyDown={(e) => {if (e.key === "Enter") setOpen(false);}}  
                aria-label="Search a city"  
            /> 
            {/* show the suggestions as lists */
                open && suggestions.length > 0 && ( 
                    <ul className="city-search-list">
                        {suggestions.map((c) => (
                            <li key={`${c.city}-${c.state}`} onMouseDown={() => choosingCity(c)}>
                                {c.city}, {c.state}
                            </li>
                        ))}
                    </ul>
                )
            }
        </div>
    );
}