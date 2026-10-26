import { useNavigate } from 'react-router-dom';
import { useAuth } from '../Context/AuthorizationContext.jsx';

function Profile() {
    const { user, token, logout } = useAuth();
    const navigate = useNavigate();

    function handleLogout() {
        logout();
        navigate('/login');
    }

    if (!token || !user) {
        return (
            <main>
                <h1>Profile</h1>
                <p>Please log in to view your profile.</p>
                <button onClick={() => navigate('/login')}>
                    Log in
                </button>
            </main>
        );
    }

    return (
        <main>
            <h1>Profile</h1>
            <p><strong>Email:</strong> {user.email}</p>
            <p><strong>Account ID:</strong> {user.id}</p>
            <p>
                <strong>Member since:</strong>{' '}
                {user.created_at
                    ? new Date(user.created_at).toLocaleDateString()
                    : 'Unavailable'}
            </p>
            <p>
                <strong>Account type:</strong>{' '}
                {user.role === 'business_owner' ? 'Business Owner' : 'Member'}
            </p>

            <button onClick={handleLogout}>Log out</button>
        </main>
    );
}

export default Profile;
