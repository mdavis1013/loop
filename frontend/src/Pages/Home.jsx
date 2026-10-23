import './Home.css';
import { Link } from 'react-router-dom';

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
            <div className="home-photo" role="img" aria-label="Signpost point to cities around the world"></div>
        </main> 
    )
}
export default Home;