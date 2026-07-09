 
import { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('tamweel_user');
    return savedUser ? JSON.parse(savedUser) : null;
  });
  const [loading] = useState(false);

  useEffect(() => {
    // Session check is handled in useState initialization
  }, []);

  const login = async (email, password) => {
    // محاكاة تسجيل الدخول
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (email && password) {
          const mockUser = { email, id: '123', name: 'User' };
          setUser(mockUser);
          localStorage.setItem('tamweel_user', JSON.stringify(mockUser));
          resolve(mockUser);
        } else {
          reject(new Error('Invalid credentials'));
        }
      }, 1000);
    });
  };

  const register = async (email, password, name) => {
    // محاكاة إنشاء حساب
    return new Promise((resolve) => {
      setTimeout(() => {
        const mockUser = { email, id: '123', name };
        setUser(mockUser);
        localStorage.setItem('tamweel_user', JSON.stringify(mockUser));
        resolve(mockUser);
      }, 1000);
    });
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('tamweel_user');
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => useContext(AuthContext);
