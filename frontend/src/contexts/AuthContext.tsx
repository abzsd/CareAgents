import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { auth, googleProvider } from '../firebase/config';
import { 
  signInWithPopup, 
  signOut, 
  onAuthStateChanged, 
  User
} from 'firebase/auth';
import { userApi } from '../services/api';

interface AuthContextType {
  user: User | null;
  userProfile: any | null;
  loading: boolean;
  googleSignIn: () => Promise<void>;
  logout: () => Promise<void>;
  setUserProfile: (profile: any) => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [userProfile, setUserProfile] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        setUser(firebaseUser);
        
        try {
          // Check if user exists in our database
          let userRecord;
          try {
            userRecord = await userApi.getUserByFirebaseUid(firebaseUser.uid);
          } catch (error: any) {
            // User not found (404), create new user
            if (error.message) {
              const userData = {
                email: firebaseUser.email || '',
                display_name: firebaseUser.displayName || '',
                photo_url: firebaseUser.photoURL || '',
                role: 'patient', // default role
                is_onboarded: false,
                firebase_uid: firebaseUser.uid,
                provider_id: firebaseUser.providerId || 'google.com'
              };
              
              try {
                userRecord = await userApi.createUser(userData);
              } catch (createError) {
                console.error('Error creating user:', createError);
                // Even if creation fails, we still want to proceed
                setUserProfile(null);
                setLoading(false);
                return;
              }
            } else {
              console.error('Error fetching user:', error);
              setUserProfile(null);
              setLoading(false);
              return;
            }
          }
          
          setUserProfile(userRecord);
        } catch (error) {
          console.error('Error in auth state change:', error);
          setUserProfile(null);
        }
      } else {
        setUser(null);
        setUserProfile(null);
      }
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  const googleSignIn = async () => {
    try {
      const result = await signInWithPopup(auth, googleProvider);
      setUser(result.user);
      
      // Create or update user in our database
      try {
        let userRecord;
        try {
          userRecord = await userApi.getUserByFirebaseUid(result.user.uid);
        } catch (error: any) {
          // User not found (404), create new user
          if (error.message && error.message.includes('404')) {
            const userData = {
              email: result.user.email || '',
              display_name: result.user.displayName || '',
              photo_url: result.user.photoURL || '',
              role: 'patient', // default role
              is_onboarded: false,
              firebase_uid: result.user.uid,
              provider_id: result.user.providerId || 'google.com'
            };
            
            try {
              userRecord = await userApi.createUser(userData);
            } catch (createError) {
              console.error('Error creating user:', createError);
              // Even if creation fails, we still want to proceed with Firebase user
              setUserProfile(null);
              return;
            }
          } else {
            console.error('Error fetching user:', error);
            setUserProfile(null);
            return;
          }
        }
        
        setUserProfile(userRecord);
      } catch (error) {
        console.error('Error handling user profile:', error);
        setUserProfile(null);
      }
    } catch (error) {
      console.error('Google sign-in error:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      await signOut(auth);
      setUser(null);
      setUserProfile(null);
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  };

  const value = {
    user,
    userProfile,
    loading,
    googleSignIn,
    logout,
    setUserProfile
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
