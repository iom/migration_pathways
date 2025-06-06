import { Routes, Route } from 'react-router-dom'

import Chat from './screens/Chat/Chat'
import Login from './screens/Login/Login'
import AdminLogin from './screens/AdminLogin/AdminLogin'
import AdminDashboard from './screens/AdminDashboard/AdminDashboard'

export default function App()
{
        return  <Routes>
                <Route path="/" element={<Login/>} />
                <Route path="/login" element={<Login/>} />
                <Route path="/register" element={<Login register/>} />
                <Route path="/forgotpassword" element={<Login forgotPassword/>} />
                <Route path="/chat" element={<Chat/>} />

                <Route path="/adminlogin" element={<AdminLogin />} />
                <Route path="/admindashboard" element={<AdminDashboard />} />
        </Routes>
}
