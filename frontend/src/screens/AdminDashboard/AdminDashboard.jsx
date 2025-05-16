import './AdminDashboard.css'

import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL

import app_logo from "../../assets/images/App_logo.svg"
import auth_logo from "../../assets/images/auth_logo.svg"
import userInfo_icon from "../../assets/images/AdminDashboard_userInfo.svg"
import search_icon from "../../assets/images/search.svg"
import delete_icon from "../../assets/images/delete.svg"
import undo_icon from "../../assets/images/undo.svg"

export default function AdminDashboard ()
{
        const navigate = useNavigate()

        const [users, setUsers] = useState([])

        useEffect(() => {
                getUsers()
        }, [])

        async function getUsers ()
        {
                const response = await fetch(`${API_BASE_URL}/admin/users`, {
                        method: 'GET',
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include'
                })

                if(response.ok)
                {
                        const data = await response.json()
                        setUsers(data.users)
                }
                else
                        navigate("/adminlogin")
        }

        async function handleDelete (user) {
                const response = await fetch(`${API_BASE_URL}/admin/ban_user`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email: user.email }),
                        credentials: 'include'
                })

                if(response.ok)
                        getUsers()
        }

        async function handleRestore (user)
        {
                const response = await fetch(`${API_BASE_URL}/admin/unban_user`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email: user.email }),
                        credentials: 'include'
                })

                if(response.ok)
                        getUsers()
        }

        return <div className="AdminDashboard">
                <header className='AdminDashboard_header'>
                        <img src={app_logo} className='AdminDashboard_appLogo' />
                        <hr className='AdminDashboard_header_delineator' />
                        <img src={auth_logo} className='AdminDashboard_authLogo' />
                        Administrator Portal
                </header>

                <main className='AdminDashboard_content'>
                        <section className='AdminDashboard_title'>
                                <h2 className="AdminDashboard_title_left">
                                        <img src={userInfo_icon} />
                                        User Details
                                </h2>

                                {/* <div className="AdminDashboard_title_right">
                                        <img src={search_icon} />
                                        <input type="text" className='AdminDashboard_searchInput' placeholder='Search users' />
                                </div> */}
                        </section>

                        <table className="AdminDashboard_table">
                                <thead>
                                        <tr>
                                                <th>Sl No.</th>
                                                <th>Name</th>
                                                <th>Email</th>
                                                <th>Requests</th>
                                                <th>Active</th>
                                                <th>Action</th>
                                        </tr>
                                </thead>
                                <tbody>
                                        {users.map((user, idx) =>
                                                <tr key={idx} className={`AdminDashboard_table_row`}>
                                                        <td>{(idx + 1)}</td>
                                                        <td>{user.username}</td>
                                                        <td>{user.email}</td>
                                                        <td>{user.request_count}</td>
                                                        <td>
                                                                <div className={`AdminTable_userActiveIndicator ${user.active === true ? "active" : ""}`} />
                                                                {user.active ? "True" : "False"}
                                                        </td>
                                                        <td>
                                                                <img className='AdminDashboard_actionIcon' src={user.active === true ? delete_icon : undo_icon} onClick={user.active ? () => handleDelete(user) : () => handleRestore(user)} />
                                                        </td>
                                                </tr>
                                        )}
                                </tbody>
                        </table>
                </main>
        </div>
}