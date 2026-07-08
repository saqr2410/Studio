import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './contexts/AuthContext'

import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Reports from './pages/Reports'
import ReportGenerator from './pages/ReportGenerator'
import ReportDetail from './pages/ReportDetail'
import Bookings from './pages/Bookings'
import Customers from './pages/Customers'
import Users from './pages/Users'
import Payments from './pages/Payments'
import Finance from './pages/Finance'

import MainLayout from './layouts/MainLayout'

const PrivateRoute = ({ children }) => {
  const { user, loading } = useAuth()

  console.log('Auth:', { user, loading })

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        fontSize: '24px'
      }}>
        Loading...
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return children
}


function App() {
  return (
    <Routes>

      <Route path="/login" element={<Login />} />

      <Route
        path="/"
        element={
          <PrivateRoute>
            <MainLayout>
              <Dashboard />
            </MainLayout>
          </PrivateRoute>
        }
      />

      <Route
        path="/reports"
        element={
          <PrivateRoute>
            <MainLayout>
              <Reports />
            </MainLayout>
          </PrivateRoute>
        }
      />

      <Route
        path="/reports/generate"
        element={
          <PrivateRoute>
            <MainLayout>
              <ReportGenerator />
            </MainLayout>
          </PrivateRoute>
        }
      />

      <Route
        path="/reports/:id"
        element={
          <PrivateRoute>
            <MainLayout>
              <ReportDetail />
            </MainLayout>
          </PrivateRoute>
        }
      />

      <Route
        path="/bookings"
        element={
          <PrivateRoute>
            <MainLayout>
              <Bookings />
            </MainLayout>
          </PrivateRoute>
        }
      />

      <Route
        path="/customers"
        element={
          <PrivateRoute>
            <MainLayout>
              <Customers />
            </MainLayout>
          </PrivateRoute>
        }
      />

      <Route
        path="/users"
        element={
          <PrivateRoute>
            <MainLayout>
              <Users />
            </MainLayout>
          </PrivateRoute>
        }
      />

      <Route
        path="/payments"
        element={
          <PrivateRoute>
            <MainLayout>
              <Payments />
            </MainLayout>
          </PrivateRoute>
        }
      />

      <Route
        path="/finance"
        element={
          <PrivateRoute>
            <MainLayout>
              <Finance />
            </MainLayout>
          </PrivateRoute>
        }
      />

      {/* أي رابط غير معروف */}
      <Route path="*" element={<Navigate to="/" replace />} />

    </Routes>
  )
}

export default App