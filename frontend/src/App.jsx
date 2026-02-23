import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        {/* Новые страницы добавляй сюда, например:
        <Route path="order" element={<OrderForm />} />
        <Route path="orders" element={<OrderList />} />
        */}
      </Route>
    </Routes>
  )
}

export default App
