
import { createContext, useContext, useState } from 'react';

const AuthContext = createContext(null);

export function AuthorizationProvider({ children }) {
    const [user, setUser] = useState(() => {
        try {
            const savedUser = localStorage.getItem('loop_user');
            return savedUser ? JSON.parse(savedUser) : null;
        } catch {
            localStorage.removeItem('loop_user');
            return null;
        }
    });

    const [token, setToken] = useState(
        () => localStorage.getItem('loop_token')
    );

    function login(authData) {
        localStorage.setItem('loop_token', authData.token);
        localStorage.setItem('loop_user', JSON.stringify(authData.user));
        setToken(authData.token);
        setUser(authData.user);
    }

    function logout() {
        localStorage.removeItem('loop_token');
        localStorage.removeItem('loop_user');
        setToken(null);
        setUser(null);
    }

    return (
        <AuthContext.Provider value={{ user, token, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    return useContext(AuthContext);
}
