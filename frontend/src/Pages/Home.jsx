import './Home.css';
import { Link } from 'react-router-dom';

// Importing photos
import signpost from '../Assets/postcard.jpg';
import street from '../Assets/street.jpg';
import beach from '../Assets/beach.jpg';
import venice from '../Assets/venice.jpg';
import petra from '../Assets/petra.jpg';

const POSTCARDS = [
    {src: street, style: {top: '6%', left: '6%', '--tilt': '-6deg', width: '230px'}},
    {src: signpost, style: {top: '8%', right: '7%', '--tilt': '5deg', width: '260px'}},
    {src: venice, style: {bottom: '6%', left: '10%', '--tilt': '4deg'}},
    {src: beach, style: {top: '29%', left: '23%', '--tilt': '-3deg', width: '200px'}},
    {src: petra, style: {bottom: '8%', right: '20%', '--tilt': '-5deg', width: '260px'}}
];

function Home() {
    return (
        <main className="home">
            {/* <h1 className="home-title">Loop</h1>
            <p className="home-slogan">Your city, unlocked</p>
            <div className="home-divider"></div>
            <Link to="/login" className="home-button">Start exploring</Link> */}
            <div className="home-text">
                <h1 className="home-title">Loop</h1>
                <p className="home-slogan">Your city, unlocked</p>
                <div className="home-divider"></div>
                <Link to="/login" className="home-button">Start Exploring</Link>
            </div>
            {POSTCARDS.map((p) => (
                <img key={p.src} src={p.src} alt="" className="postcard" style={p.style} />
            ))}
        </main> 
    )
}
export default Home;