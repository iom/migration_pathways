import './AdminLogin.css'

import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL

import iom_logo from "../../assets/images/appLogo_inverted.svg"
import app_logo from "../../assets/images/App_logo.svg"
import auth_logo from "../../assets/images/auth_logo.svg"
import show from "../../assets/images/login_showPassword.svg"
import hide from "../../assets/images/login_hidePassword.svg"

export default function AdminLogin ()
{
        const navigate = useNavigate()

        const [formData, setFormData] = useState({ email: "", password: "" })

        const [showPassword, setShowPassword] = useState(false)

        const errorPopover = useRef()
        const [errorText, setErrorText] = useState("")
        useEffect(() => {
                const sessionExpiredError = sessionStorage.getItem("session_expired")
                if(sessionExpiredError && errorPopover.current.showPopover) {
                        setErrorText(sessionExpiredError)
                        errorPopover.current.showPopover()
                        sessionStorage.removeItem("session_expired")
                }
        }, [])

        useEffect(() => {
                if(errorPopover.current?.hidePopover && formData.password) {
                        setErrorText("")
                        errorPopover.current.hidePopover()
                }
                else
                        setShowPassword(false)
        }, [...Object.values(formData)])

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

        const [loading, setLoading] = useState(false)
        async function handleSubmit (e)
        {
                e.preventDefault()

                setLoading(true)

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
                        {
                                const data = await response.json()
                                errorPopover.current.showPopover()
                                setErrorText(data.error ?? "Login failed!")

                                setLoading(false)
                                setFormData({ email: "", password: "" })
                                setShowPassword(false)
                        }
                }
                catch (error)
                {
                        setLoading(false)
                        setFormData(p => ({ email: "", password: "" }))
                        setShowPassword(false)
                        console.log(error)
                }
        }

        return  <div className='AdminLogin'>
                <div popover="auto" className='Login-errorPopover' data-testid="adminError-popover" ref={errorPopover}>
                        <span>🛇 {errorText}</span>
                        <span onClick={() => errorPopover.current.hidePopover()} style={{ cursor: "pointer" }}>✖</span>
                </div>

                <form className='AdminLogin_form' onSubmit={handleSubmit}>
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

                        <main className='Login-form'>
                                <label className='Login-label' htmlFor='Login_emailInput'>Email</label>
                                <input type='email' id="Login_emailInput" placeholder='Enter your email address' className='AdminLogin_email' value={formData.email} onChange={handleInputChange} />

                                <label className='Login-label' htmlFor="Login_passwordInput">Password</label>
                                <input type={showPassword ? 'text' : 'password'} id="Login_passwordInput" placeholder='Enter your password' className='AdminLogin_password' value={formData.password} onChange={handlePasswordChange} />
                                {formData.password ? <div className="Login_showPasswordToggleContainer">
                                        <img className='Login_passwordShowToggle' src={showPassword ? hide : show} onClick={() => setShowPassword(p => !p)}/>
                                </div> : ""}

                                <button
                                        type='submit'
                                        className='Login-submit'
                                        disabled={
                                                !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)
                                                ||
                                                formData.password.length < 8
                                        }
                                        style={{ marginTop: "45px" }}
                                >
                                        {loading ? "LOGGING IN" : "LOGIN"}
                                        {loading ? <span className='submitButtonSpinner' /> : ""}
                                </button>
                        </main>
                </form>
        </div>
}