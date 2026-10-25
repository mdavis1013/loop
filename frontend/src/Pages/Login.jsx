import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../Context/AuthorizationContext.jsx';
import './Login.css';

const API_BASE_URL = 'http://localhost:5001';

function Login() {
    // state for the email and password
    const [mode, setMode] = useState('login');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [name, setName] = useState('');
    const [confirmP, setConfirmP] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const { login } = useAuth();

    async function handlingLoginInfo(event) {
        event.preventDefault();
        setError('');
        
        if (mode === 'signup' && password !== confirmP) {
            console.log("Passwords don't match");
            return; 
        }
        setLoading(true);

        try {
            const endpoint =
                mode === 'signup'
                    ? '/api/auth/register'
                    : '/api/auth/login';

            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email.trim(),
                    password,
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.message || 'Authentication failed. Please try again.'
                );
            }

            login(data);
            navigate('/explore');
        } catch (err) {
            setError(
                err instanceof TypeError
                    ? 'Issue connecting to the server.'
                    : err.message
            );
        } finally {
            setLoading(false);
        }
    }

    function switchingMode() {
        setMode(mode === 'login' ? 'signup' : 'login');
        setError('');
        setPassword('');
        setConfirmP('');
    }
    return (
        <main className="login">
            <h1 className="login-title">
                {mode === 'login' ? 'Welcome back' : 'Create an account'}
            </h1>

            <form className="login-form" onSubmit={handlingLoginInfo}>
                {mode === 'signup' && (
                    <input
                        type="text"
                        placeholder="Name"
                        aria-label="Name"
                        required
                        value={name}
                        onChange={(event) => setName(event.target.value)}
                    />
                )}
                <input 
                    type="email"
                    placeholder="Email"
                    aria-label="Email"
                    required /* Forces the email being placed */
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                />
               <input  
                    type="password"
                    placeholder="Password"
                    aria-label="Password"
                    autoComplete={
                        mode === 'login'
                            ? 'current-password'
                            : 'new-password'
                    }
                    required
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                />
                {mode === 'signup' && (
                    <input
                        type="password"
                        placeholder="Confirm password"
                        aria-label="Confirm password"
                        autoComplete="new-password"
                        required
                        value={confirmP}
                        onChange={(event) => setConfirmP(event.target.value)}
                    />  
                )}

                {error && <p role="alert">{error}</p>}

                <button type="submit" className="login-button" disabled={loading}>
                    {loading
                        ? 'Please wait...'
                        : mode === 'login' ? 'Log in' : 'Sign up'}
                </button>
            </form>

            <p className="login-switch">
                {mode === 'login' ? "Don't have an account?" : 'Already have an account?'}
                <button type="button" className="login-switch-button" onClick={switchingMode}>
                    {mode === 'login' ? 'Sign up' : 'Log in'}
                </button>
            </p>
        </main>
    )
}
export default Login;