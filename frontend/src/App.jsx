import './App.css'
import { Routes, Route } from 'react-router-dom'
import Explore from './Pages/Explore.jsx'
import Login from './Pages/Login.jsx'
import MapInfo from './Pages/MapInfo.jsx'
import OptionNotFound from './Pages/OptionNotFound.jsx'
import PlaceDetails from './Pages/PlaceDetails.jsx'
import Profile from './Pages/Profile.jsx'
import Home from './Pages/Home.jsx';

function App() {
  return (
  <Routes> 
    <Route path="/" element={<Home />} />
    <Route path="/" element={<Explore />} /> 
    <Route path="/login" element={<Login />} />
    <Route path="/map" element={<MapInfo />} />
    <Route path="/place/:id" element={<PlaceDetails />} />
    <Route path="/profile" element={<Profile />} />
    <Route path="*" element={<OptionNotFound />} />
  </Routes>
  )
}

export default App
