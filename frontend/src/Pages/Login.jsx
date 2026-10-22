import { useState } from 'react';
import './Login.css';

function Login() {
    // state for the email and password
    const [mode, setMode] = useState('login');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [name, setName] = useState('');
    const [confirmP, setConfirmP] = useState('');

    function handlingLoginInfo(event) {
        event.preventDefault();
        
        if (mode === 'signup' && password !== confirmP) {
            console.log("Passwords don't match");
            return; 
        }
        console.log(mode, name, email, password);
    }

    function switchingMode() {
        setMode(mode === 'login' ? 'signup' : 'login');
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
                        value={name}
                        onChange={(event) => setName(event.target.value)}
                    />
                )}
                <input 
                    type="email"
                    placeholder="Email"
                    aria-label="Email"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                />
               <input  
                    type="password"
                    placeholder="Password"
                    aria-label="Password"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                />
                {mode === 'signup' && (
                    <input
                        type="password"
                        placeholder="Confirm password"
                        aria-label="Confirm password"
                        value={confirmP}
                        onChange={(event) => setConfirmP(event.target.value)}
                    />  
                )}

                <button type="submit" className="login-button">
                    {mode === 'login' ? 'Log in' : 'Sign up'}
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