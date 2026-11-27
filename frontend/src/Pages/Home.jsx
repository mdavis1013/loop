import './Home.css';
import { Link } from 'react-router-dom';

// Importing photos
import signpost from '../Assets/postcard.jpg';
import street from '../Assets/street.jpg';
import beach from '../Assets/beach.jpg';
import venice from '../Assets/venice.jpg';
import petra from '../Assets/petra.jpg';

//Photos that will be shown in the scroll strip
//--tilt = CSS var. that Home.css reads to rotate each card
const POSTCARDS = [
    {src: street, style: {'--tilt' : '-6deg'}},
    {src: signpost, style: {'--tilt' : '-6deg'}},
    {src: venice, style: {'--tilt' : '-6deg'}},
    {src: beach, style: {'--tilt' : '-6deg'}},
    {src: petra, style: {'--tilt' : '-6deg'}}
];

function Home() {
    return (
        //Here the strip is the visible window and track is the long row inside it that actually slides to the left
        //Also the list is rendered twice so the loop looks seamless, and the repeats after the 5 pics
        <main className="home">
            <div className="home-text">
                <h1 className="home-title">Loop</h1>
                <p className="home-slogan">Your city, unlocked</p>
                <div className="home-divider"></div>
                <Link to="/login" className="home-button">Start Exploring</Link>
            </div>
            <div className="postcard-strip">
                <div className="postcard-track">
                    {[...POSTCARDS, ...POSTCARDS].map((p, i) => (
                        <img key={i} src={p.src} alt="" className="postcard" style={p.style} />
                    ))}
                </div>
            </div>
        </main> 
    )
}
export default Home;