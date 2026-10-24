import './Home.css';
import { Link } from 'react-router-dom';

function Home() {
    return (
        <main className="home">
            <h1 className="home-title">Loop</h1>
            <p className="home-slogan">Your city, unlocked</p>
            <div className="home-divider"></div>
            <Link to="/explore" className="home-button">Start exploring</Link>
        </main> 
    )
}
export default Home;