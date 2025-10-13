import React, { createContext, useContext, useState, useEffect } from 'react';
import { useColorScheme } from 'react-native';
// Import AsyncStorage conditionally to avoid SSR issues
let AsyncStorage: any = null;
try {
  AsyncStorage = require('@react-native-async-storage/async-storage').default;
} catch (error) {
  // AsyncStorage not available (e.g., during SSR)
  console.log('AsyncStorage not available during initialization');
}

export interface ThemeColors {
  primary: string;
  background: string;
  surface: string;
  text: string;
  textSecondary: string;
  border: string;
  card: string;
  notification: string;
  error: string;
  success: string;
  warning: string;
}

export const lightTheme: ThemeColors = {
  primary: '#E86BA9',
  background: 'linear-gradient(to bottom, #F8BBD9, #F4A6CD, #F092C1, #EC7FB5, #E86BA9)',
  surface: 'rgba(255, 255, 255, 0.9)',
  text: '#FFFFFF',
  textSecondary: 'rgba(255, 255, 255, 0.8)',
  border: 'rgba(255, 255, 255, 0.2)',
  card: 'rgba(255, 255, 255, 0.15)',
  notification: '#E86BA9',
  error: '#FF6B6B',
  success: '#4CAF50',
  warning: '#FFC107',
};

export const darkTheme: ThemeColors = {
  primary: '#E86BA9',
  background: 'linear-gradient(to bottom, #F8BBD9, #F4A6CD, #F092C1, #EC7FB5, #E86BA9)',
  surface: 'rgba(255, 255, 255, 0.9)',
  text: '#FFFFFF',
  textSecondary: 'rgba(255, 255, 255, 0.8)',
  border: 'rgba(255, 255, 255, 0.2)',
  card: 'rgba(255, 255, 255, 0.15)',
  notification: '#E86BA9',
  error: '#FF6B6B',
  success: '#4CAF50',
  warning: '#FFC107',
};

interface ThemeContextType {
  theme: ThemeColors;
  isDark: boolean;
  toggleTheme: () => void;
  setThemeMode: (mode: 'light' | 'dark' | 'system') => void;
  themeMode: 'light' | 'dark' | 'system';
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

interface ThemeProviderProps {
  children: React.ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const systemColorScheme = useColorScheme();
  const [themeMode, setThemeModeState] = useState<'light' | 'dark' | 'system'>('system');
  
  // Determine the actual theme based on mode and system preference
  const isDark = themeMode === 'dark' || (themeMode === 'system' && systemColorScheme === 'dark');
  const theme = isDark ? darkTheme : lightTheme;

  // Load theme preference from storage
  useEffect(() => {
    const loadThemePreference = async () => {
      try {
        if (!AsyncStorage) {
          console.log('AsyncStorage not available, using default theme');
          return;
        }
        const savedThemeMode = await AsyncStorage.getItem('@theme_mode');
        if (savedThemeMode && ['light', 'dark', 'system'].includes(savedThemeMode)) {
          setThemeModeState(savedThemeMode as 'light' | 'dark' | 'system');
        }
      } catch (error) {
        console.warn('Failed to load theme preference:', error);
      }
    };
    
    loadThemePreference();
  }, []);

  // Save theme preference to storage
  const setThemeMode = async (mode: 'light' | 'dark' | 'system') => {
    try {
      if (AsyncStorage) {
        await AsyncStorage.setItem('@theme_mode', mode);
      }
      setThemeModeState(mode);
    } catch (error) {
      console.warn('Failed to save theme preference:', error);
      setThemeModeState(mode); // Still update state even if save fails
    }
  };

  const toggleTheme = () => {
    const newMode = isDark ? 'light' : 'dark';
    setThemeMode(newMode);
  };

  return (
    <ThemeContext.Provider 
      value={{ 
        theme, 
        isDark, 
        toggleTheme, 
        setThemeMode, 
        themeMode 
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
};