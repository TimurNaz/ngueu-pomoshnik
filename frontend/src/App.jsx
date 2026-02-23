import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import Onboarding from './pages/Onboarding'
import NewOrder from './pages/NewOrder'
import Orders from './pages/Orders'
import OrderDetail from './pages/OrderDetail'
import FAQ from './pages/FAQ'
import Profile from './pages/Profile'

function requireOnboarding(element) {
  const done = localStorage.getItem('onboarding_done')
  if (!done) return <Navigate to="/onboarding" replace />
  return element
}

const router = createBrowserRouter([
  {
    path: '/onboarding',
    element: <Onboarding />,
  },
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        index: true,
        element: requireOnboarding(<Home />),
      },
      {
        path: 'new-order',
        element: <NewOrder />,
      },
      {
        path: 'orders',
        element: <Orders />,
      },
      {
        path: 'orders/:id',
        element: <OrderDetail />,
      },
      {
        path: 'faq',
        element: <FAQ />,
      },
      {
        path: 'profile',
        element: <Profile />,
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
])

export default function App() {
  return <RouterProvider router={router} />
}
