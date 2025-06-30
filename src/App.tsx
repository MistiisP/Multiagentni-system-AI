import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import '/css/App.css'
import {Routes, Route} from "react-router-dom";


/* import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import User from './pages/User'
import LogIn from './pages/LogIn'
import SignUp from './pages/SignUp'
import Settings from './pages/Settings' */


function App() {
  const [count, setCount] = useState(0)

  return (
    <main className='App'>
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/user" element={<User />} />
      <Route path="/login" element={<LogIn />} />
      <Route path="/signup" element={<SignUp />} />
      <Route path="/settings" element={<Settings />} />
      


    </Routes>
    </main>
  )
}

export default App
