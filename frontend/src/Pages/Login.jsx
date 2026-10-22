import { useState } from 'react';
import './Login.css';

function Login() {
    // state for the email and password
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    function handlingLoginInfo(event) {
        event.preventDefault();
        // console.log the email & password
        console.log(email, password);
    }
    return (
        <main className="login">
            <h1 className="login-title">Welcome back</h1>
            <form className="login-form" onSubmit={handlingLoginInfo}>
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

                <button type="submit" className="login-button">Log in</button>
            </form>
        </main>
    )
}
export default Login;