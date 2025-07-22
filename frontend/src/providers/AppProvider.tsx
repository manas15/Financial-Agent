'use client'

import { createContext, useContext, useReducer, ReactNode, useEffect } from 'react'
import { notifications } from '@mantine/notifications'
import { api } from '@/lib/api'

// Types
interface User {
  id: number
  email: string
  full_name?: string
  is_active: boolean
  created_at: string
}

// Removed Portfolio interfaces - focusing on watchlist and reports

interface WatchlistItem {
  id: number
  symbol: string
  current_price?: number
  notes?: string
  added_date: string
}

interface AppState {
  // Auth
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean

  // Watchlist
  watchlist: WatchlistItem[]
  watchlistLoading: boolean


  // UI State
  sidebarCollapsed: boolean
  colorScheme: 'light' | 'dark'
}

type AppAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_USER'; payload: { user: User; token: string } }
  | { type: 'LOGOUT' }
  | { type: 'SET_WATCHLIST'; payload: WatchlistItem[] }
  | { type: 'SET_WATCHLIST_LOADING'; payload: boolean }
  | { type: 'TOGGLE_SIDEBAR' }
  | { type: 'SET_COLOR_SCHEME'; payload: 'light' | 'dark' }

const initialState: AppState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
  watchlist: [],
  watchlistLoading: false,
  sidebarCollapsed: false,
  colorScheme: 'light',
}

function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload }
    
    case 'SET_USER':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
      }
    
    case 'LOGOUT':
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      return {
        ...initialState,
        isLoading: false,
        colorScheme: state.colorScheme,
        sidebarCollapsed: state.sidebarCollapsed,
      }
    
    // Removed portfolio actions
    
    case 'SET_WATCHLIST':
      return { ...state, watchlist: action.payload, watchlistLoading: false }
    
    case 'SET_WATCHLIST_LOADING':
      return { ...state, watchlistLoading: action.payload }
    
    
    case 'TOGGLE_SIDEBAR':
      return { ...state, sidebarCollapsed: !state.sidebarCollapsed }
    
    case 'SET_COLOR_SCHEME':
      return { ...state, colorScheme: action.payload }
    
    default:
      return state
  }
}

// Context
const AppContext = createContext<{
  state: AppState
  dispatch: React.Dispatch<AppAction>
  actions: {
    login: (email: string, password: string) => Promise<void>
    register: (email: string, password: string, fullName?: string) => Promise<void>
    logout: () => void
    fetchWatchlist: () => Promise<void>
    addToWatchlist: (symbol: string, notes?: string) => Promise<void>
    removeFromWatchlist: (symbol: string) => Promise<void>
  }
} | null>(null)

export function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState)

  // Initialize app - check for stored auth
  useEffect(() => {
    const initializeAuth = () => {
      const token = localStorage.getItem('token')
      const userStr = localStorage.getItem('user')
      
      if (token && userStr) {
        try {
          const user = JSON.parse(userStr)
          api.setAuthToken(token)
          dispatch({ type: 'SET_USER', payload: { user, token } })
        } catch (error) {
          console.error('Failed to parse stored user:', error)
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          dispatch({ type: 'SET_LOADING', payload: false })
        }
      } else {
        dispatch({ type: 'SET_LOADING', payload: false })
      }
    }

    initializeAuth()
  }, [])

  // Actions
  const actions = {
    login: async (email: string, password: string) => {
      try {
        console.log('Attempting login with:', { email, password: '***' })
        dispatch({ type: 'SET_LOADING', payload: true })
        const response = await api.auth.login(email, password)
        console.log('Login response:', response)
        
        localStorage.setItem('token', response.access_token)
        localStorage.setItem('user', JSON.stringify(response.user))
        api.setAuthToken(response.access_token)
        
        dispatch({ 
          type: 'SET_USER', 
          payload: { user: response.user, token: response.access_token } 
        })
        
        notifications.show({
          title: 'Welcome back!',
          message: 'Successfully logged in',
          color: 'green',
        })
      } catch (error: any) {
        console.error('Login error details:', error)
        console.error('Error response:', error.response)
        notifications.show({
          title: 'Login failed',
          message: error.response?.data?.detail || 'Invalid credentials',
          color: 'red',
        })
        dispatch({ type: 'SET_LOADING', payload: false })
        throw error
      }
    },

    register: async (email: string, password: string, fullName?: string) => {
      try {
        dispatch({ type: 'SET_LOADING', payload: true })
        const response = await api.auth.register(email, password, fullName)
        
        localStorage.setItem('token', response.access_token)
        localStorage.setItem('user', JSON.stringify(response.user))
        api.setAuthToken(response.access_token)
        
        dispatch({ 
          type: 'SET_USER', 
          payload: { user: response.user, token: response.access_token } 
        })
        
        notifications.show({
          title: 'Welcome!',
          message: 'Account created successfully',
          color: 'green',
        })
      } catch (error: any) {
        notifications.show({
          title: 'Registration failed',
          message: error.response?.data?.detail || 'Failed to create account',
          color: 'red',
        })
        dispatch({ type: 'SET_LOADING', payload: false })
        throw error
      }
    },

    logout: () => {
      dispatch({ type: 'LOGOUT' })
      notifications.show({
        title: 'Goodbye!',
        message: 'Successfully logged out',
        color: 'blue',
      })
    },

    // Removed fetchPortfolio

    fetchWatchlist: async () => {
      try {
        dispatch({ type: 'SET_WATCHLIST_LOADING', payload: true })
        const watchlist = await api.watchlist.getAll()
        dispatch({ type: 'SET_WATCHLIST', payload: watchlist })
      } catch (error: any) {
        console.error('Failed to fetch watchlist:', error)
        dispatch({ type: 'SET_WATCHLIST_LOADING', payload: false })
      }
    },


    removeFromWatchlist: async (symbol: string) => {
      try {
        await api.watchlist.remove(symbol)
        await actions.fetchWatchlist()
        notifications.show({
          title: 'Success',
          message: `Removed ${symbol} from watchlist`,
          color: 'green',
        })
      } catch (error: any) {
        notifications.show({
          title: 'Error',
          message: error.response?.data?.detail || 'Failed to remove from watchlist',
          color: 'red',
        })
        throw error
      }
    },

    addToWatchlist: async (symbol: string, notes?: string) => {
      try {
        await api.watchlist.add(symbol, notes)
        await actions.fetchWatchlist()
        notifications.show({
          title: 'Success',
          message: `Added ${symbol} to watchlist`,
          color: 'green',
        })
      } catch (error: any) {
        notifications.show({
          title: 'Error',
          message: error.response?.data?.detail || 'Failed to add to watchlist',
          color: 'red',
        })
        throw error
      }
    },

  }

  return (
    <AppContext.Provider value={{ state, dispatch, actions }}>
      {children}
    </AppContext.Provider>
  )
}

export function useApp() {
  const context = useContext(AppContext)
  if (!context) {
    throw new Error('useApp must be used within AppProvider')
  }
  return context
}