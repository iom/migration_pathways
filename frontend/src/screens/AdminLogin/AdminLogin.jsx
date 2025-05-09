import './AdminLogin.css'

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL

import iom_logo from "../../assets/images/appLogo_inverted.svg"
import app_logo from "../../assets/images/App_logo.svg"
import auth_logo from "../../assets/images/auth_logo.svg"

export default function AdminLogin ()
{
        const navigate = useNavigate()

        const [formData, setFormData] = useState({
                email: "",
                password: ""
        })

        function handleInputChange (e)
        {
                if (e => /^[a-zA-Z0-9@._%+-]*$/.test(e.target.value))
                {
                        setFormData(p => ({
                                ...p,
                                email: e.target.value
                        }))
                }
        }

        function handlePasswordChange (e)
        {
                setFormData(p => ({
                        ...p,
                        password: e.target.value
                }))
        }

        async function handleSubmit (e)
        {
                e.preventDefault()

                try
                {
                        const response = await fetch(`${API_BASE_URL}/admin/login`, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ email: formData.email, password: formData.password }),
                                credentials: 'include'
                        })

                        if (response.ok)
                                navigate("/admindashboard")
                        else
                                console.log(response)
                }
                catch (error)
                {
                        console.log(error)
                }
        }

        return  <div className='AdminLogin'>
                <form className='AdminLogin_form'>
                        <header className='AdminLogin_form_header'>
                                <div className='AdminLogin_form_header_left'>
                                        <img src={iom_logo} />
                                </div>

                                <div className='AdminLogin_form_header_right'>
                                        <img src={app_logo} />
                                </div>
                        </header>

                        <h2 className='AdminLogin_form_title'>
                                <img src={auth_logo} />
                                Administrator Login
                        </h2>

                        <main className='AdminLogin_form_inputs'>
                                <label>Email</label>
                                <input type='email' placeholder='email' className='AdminLogin_email' value={formData.email} onChange={handleInputChange} />

                                <label>Password</label>
                                <input type='password' placeholder='password' className='AdminLogin_password' value={formData.password} onChange={handlePasswordChange} />

                                <button type='submit' className='AdminLogin_form_submit' onClick={handleSubmit}>LOGIN</button>
                        </main>
                </form>
        </div>
}