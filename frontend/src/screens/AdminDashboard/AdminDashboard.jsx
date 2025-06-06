import './AdminDashboard.css'

import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL

import app_logo from "../../assets/images/App_logo.svg"
import auth_logo from "../../assets/images/auth_logo.svg"
import logout_icon from "../../assets/images/Header_logout.svg"
import downarrow from "../../assets/images/downarrow.svg"
import users_icon from "../../assets/images/AdminDashboard_users.svg"
import add_icon from "../../assets/images/AdminDashboard_add.svg"
import tick_icon from "../../assets/images/AdminDashboard_tick.svg"
import cross_icon from "../../assets/images/AdminDashboard_cross.svg"
import browse_icon from "../../assets/images/AdminDashboard_browse.svg"
import upload_icon from "../../assets/images/AdminDashboard_upload.svg"
import sources_icon from "../../assets/images/AdminDashboard_sources.svg"
import content_icon from "../../assets/images/AdminDashboard_content.svg"
import delete_icon from "../../assets/images/delete.svg"
import undo_icon from "../../assets/images/undo.svg"

export default function AdminDashboard ()
{
        const navigate = useNavigate()

        const [username, setUsername] = useState("")
        const [email, setEmail] = useState("")

        const [users, setUsers] = useState([])

        async function getProfile ()
        {
                const response = await fetch(`${API_BASE_URL}/admin/profile`, {
                        method: "GET",
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include'
                })

                if(response.ok)
                {
                        const data = await response.json()
                        setUsername(data.username)
                        setEmail(data.email)
                }
                else if(response.status === 401)
                {
                        sessionStorage.setItem("session_expired", "Session expired. Please login again.")
                        navigate("/adminlogin")
                }
                else
                        navigate("/adminlogin")
        }

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
                else if(response.status === 401)
                {
                        sessionStorage.setItem("session_expired", "Session expired. Please login again.")
                        navigate("/adminlogin")
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
                else if(response.status === 401)
                {
                        sessionStorage.setItem("session_expired", "Session expired. Please login again.")
                        navigate("/adminlogin")
                }
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
                else if(response.status === 401)
                {
                        sessionStorage.setItem("session_expired", "Session expired. Please login again.")
                        navigate("/adminlogin")
                }
        }

        async function handleLogoutClick ()
        {
                const response = await fetch(`${API_BASE_URL}/admin/logout`, {
                        method: "POST",
                        credentials: "include",
                        headers: { "Content-Type": "application/json" }
                })

                if(response)
                        navigate("/adminlogin")
        }

        const [url, setUrl] = useState("")
        const urlRegex = /^(https?:\/\/)(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,6}(?::\d{1,5})?(?:\/\S*)?$/
        const [addButtonText, setAddButtonText] = useState("Add")
        const [addButtonIcon, setAddButtonIcon] = useState(add_icon)
        const [addLoading, setAddLoading] = useState(false)
        async function handleAddWebsiteClick ()
        {
                setLoading(true)
                setAddLoading(true)
                setAddButtonText("Adding")

                const response = await fetch(`${API_BASE_URL}/admin/add-url`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ email, url }),
                        credentials: "include"
                })

                if(response.ok)
                {
                        setLoading(false)
                        setAddLoading(false)
                        setAddButtonText("Added!")
                        setAddButtonIcon(tick_icon)
                        setUrl("")
                        setTimeout(() => {
                                setAddButtonText("Add")
                                setAddButtonIcon(add_icon)
                        }, 2000)
                }
                else if(response.status === 401)
                {
                        sessionStorage.setItem("session_expired", "Session expired. Please login again.")
                        navigate("/adminlogin")
                }
                else if(response.status === 409)
                {
                        setLoading(false)
                        setAddLoading(false)
                        setAddButtonText("URL already exists!")
                        setAddButtonIcon(cross_icon)
                        setTimeout(() => {
                                setAddButtonText("Add")
                                setAddButtonIcon(add_icon)
                        }, 2000)
                }
                else
                {
                        setLoading(false)
                        setAddLoading(false)
                        setAddButtonText("Failed, try again.")
                        setAddButtonIcon(cross_icon)
                        setTimeout(() => {
                                setAddButtonText("Add")
                                setAddButtonIcon(add_icon)
                        }, 2000)
                }
        }

        const fileInputRef = useRef(null)
        const [files, setFiles] = useState([])
        function handleFileChange (event)
        {
                const selected = Array.from(event.target.files)
                const allowed = [
                        'application/pdf',
                        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                        'text/plain'
                ]
                const filtered = selected.filter(file => allowed.includes(file.type))
                setFiles(filtered)
        }

        const [uploadLoading, setUploadLoading] = useState(false)
        const [uploadButtonIcon, setUploadButtonIcon] = useState(upload_icon)
        const [uploadStatusMessage, setUploadStatusMessage] = useState(null)
        async function handleFileUpload ()
        {
                if (!files.length) return

                setLoading(true)
                setUploadLoading(true)

                const formData = new FormData()
                // files.forEach((file, idx) => {
                //         formData.append(`files[${idx}]`, file)
                // })
                formData.append("file", files[0])
                formData.append("email", email)

                try
                {
                        const response = await fetch(`${API_BASE_URL}/admin/upload-doc`, {
                                method: 'POST',
                                body: formData,
                                credentials: "include"
                        })

                        if (response.ok)
                        {
                                setUploadStatusMessage("Uploaded!")
                                setUploadButtonIcon(tick_icon)
                                setLoading(false)
                                setUploadLoading(false)
                                setTimeout(() => {
                                        setFiles([])
                                        setUploadStatusMessage(null)
                                        setUploadButtonIcon(upload_icon)
                                }, 2000)
                        }
                        else if(response.status === 401)
                        {
                                sessionStorage.setItem("session_expired", "Session expired. Please login again.")
                                navigate("/adminlogin")
                        }
                        else if(response.status === 409)
                        {
                                setUploadStatusMessage("File already exists!")
                                setUploadButtonIcon(cross_icon)
                                setLoading(false)
                                setUploadLoading(false)
                                setTimeout(() => {
                                        setFiles([])
                                        setUploadStatusMessage(null)
                                        setUploadButtonIcon(upload_icon)
                                }, 2000)
                        }
                        else
                        {
                                setUploadStatusMessage("Failed, try again.")
                                setUploadButtonIcon(cross_icon)
                                setLoading(false)
                                setUploadLoading(false)
                                setTimeout(() => {
                                        setFiles([])
                                        setUploadStatusMessage(null)
                                        setUploadButtonIcon(upload_icon)
                                }, 2000)
                        }
                }
                catch (error)
                {
                        setUploadStatusMessage("Failed, try again.")
                        setUploadButtonIcon(cross_icon)
                        setLoading(false)
                        setUploadLoading(false)
                        setTimeout(() => {
                                setFiles([])
                                setUploadStatusMessage(null)
                                setUploadButtonIcon(upload_icon)
                        }, 2000)
                }
        }

        function handleUploadButtonClick ()
        {
                if(!files.length)
                {
                        fileInputRef.current.value = ''
                        fileInputRef.current.click()
                }
                else
                        handleFileUpload()
        }

        const [loading, setLoading] = useState(false)
        const [extractLoading, setExtractLoading] = useState(false)
        const [scrapingStatus, setScrapingStatus] = useState("N/A")
        const [lastExtracted, setLastExtracted] = useState("N/A")
        const [scrapedSections, setScrapedSections] = useState([])

        async function scrapeContent ()
        {
                setLoading(true)
                setExtractLoading(true)

                const response = await fetch(`${API_BASE_URL}/admin/extract`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        credentials: "include"
                })

                if(response.ok)
                {
                        const data = await response.json()

                        setScrapingStatus(data.message)
                        setLastExtracted(data.last_updated_on)
                        setScrapedSections(data.sections)
                }
                else if(response.status === 401)
                {
                        sessionStorage.setItem("session_expired", "Session expired. Please login again.")
                        navigate("/adminlogin")
                }

                setLoading(false)
                setExtractLoading(false)
        }

        async function getContent ()
        {
                setLoading(true)
                setExtractLoading(true)

                const response = await fetch(`${API_BASE_URL}/admin/extractions`, {
                        method: "GET",
                        headers: { "Content-Type": "application/json" },
                        credentials: "include"
                })

                if(response.ok)
                {
                        const data = await response.json()

                        setScrapingStatus("Content fetched.")
                        setLastExtracted(data.last_updated_on)
                        setScrapedSections(data.sections)
                }
                else if(response.status === 401)
                {
                        sessionStorage.setItem("session_expired", "Session expired. Please login again.")
                        navigate("/adminlogin")
                }
                else if(response.status === 404)
                {
                        scrapeContent()
                }

                setLoading(false)
                setExtractLoading(false)
        }

        useEffect(() => {
                getProfile()
                getUsers()
                getContent()
        }, [])

        return  <div className="AdminDashboard">
                <header className='AdminDashboard_header'>
                        <div className="AdminDashboard_header_left">
                                <img src={app_logo} className='AdminDashboard_appLogo' />
                                <hr className='AdminDashboard_header_delineator' />
                                <img src={auth_logo} className='AdminDashboard_authLogo' />
                                Administrator Portal
                        </div>

                        <div className="AdminDashboard_header_right">
                                <button className="Chat_header_right_profileItemsContainer" popoverTarget='ID_AdminDashboard_logoutPopover'>
                                        <div className="Chat_header_dp">{username && username.split('')[0].toUpperCase()}</div>

                                        <div className='Chat_header_right-nameContainer'>
                                                <div className='Chat_header_right_nameContainer-name'>{username}</div>
                                                <div className='Chat_header_right_nameContainer-email'>{email}</div>
                                        </div>

                                        <img className="Chat_header_downarrow" src={downarrow} />
                                </button>

                                <button
                                        type="button"
                                        popover='auto'
                                        id="ID_AdminDashboard_logoutPopover"
                                        className='Chat_logoutPopover'
                                        onClick={handleLogoutClick}
                                >
                                        <img src={logout_icon} alt="Logout icon" />
                                        Logout
                                </button>
                        </div>
                </header>

                <main className='AdminDashboard_content'>
                        <div className="AdminDashboard_content_partition">
                                <section className="AdminDashboard_content_body">
                                        <h2 className="AdminDashboard_content_title">
                                                <img src={users_icon} alt="Users" />
                                                Users
                                        </h2>
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
                                                                                <button
                                                                                        type="button"
                                                                                        aria-label={user.active ? `Ban ${user.username}` : `Unban ${user.username}`}
                                                                                        onClick={user.active ? () => handleDelete(user) : () => handleRestore(user)}
                                                                                        className="AdminDashboard_actionIconButton"
                                                                                >
                                                                                        <img
                                                                                                className='AdminDashboard_actionIcon'
                                                                                                src={user.active === true ? delete_icon : undo_icon}
                                                                                                alt={user.active ? 'Ban icon' : 'Unban icon'}
                                                                                        />
                                                                                </button>
                                                                        </td>
                                                                </tr>
                                                        )}
                                                </tbody>
                                        </table>
                                </section>
                        </div>

                        <div className='AdminDashboard_content_partition'>
                                <section className='AdminDashboard_content_body Sources'>
                                        <h2 className="AdminDashboard_content_title">
                                                <img src={sources_icon} />
                                                Sources
                                        </h2>

                                        <div className="AdminDashboard_knowledgeInputs">
                                                <div className="AdminDashboard_knowledgeInputs_website">
                                                        <h4 className='AdminDashboard_knowledgeInput_heading'>Add Website</h4>
                                                        <div className="AdminDashboard_knowledgeInput_textInputContainer">
                                                                <input
                                                                        type='text'
                                                                        className='AdminDashboard_urlInput'
                                                                        value={url}
                                                                        onChange={e => setUrl(e.target.value)}
                                                                        placeholder='Enter website URL'
                                                                        disabled={loading || files.length}
                                                                />

                                                                <button
                                                                        type='button'
                                                                        className='AdminDashboard_addUrlButton'
                                                                        onClick={handleAddWebsiteClick}
                                                                        disabled={!urlRegex.test(url) || loading || files.length}
                                                                >
                                                                        {loading && addLoading ?
                                                                                <span className='submitButtonSpinner' />
                                                                                :
                                                                                <img src={addButtonIcon} alt="Add URL" />
                                                                        }
                                                                        {addButtonText}
                                                                </button>
                                                        </div>
                                                </div>

                                                <div className="AdminDashboard_knowledgeInputs_file">
                                                        <h4 className='AdminDashboard_knowledgeInput_heading'>Add File</h4>

                                                        <input
                                                                type='file'
                                                                ref={fileInputRef}
                                                                multiple
                                                                accept='.pdf, .pptx, .txt'
                                                                onChange={handleFileChange}
                                                        />

                                                        <div className='AdminDashboard_fileUpload_buttonsGroup'>
                                                                <button
                                                                        type="button"
                                                                        className='AdminDashboard_fileUpload_button Upload'
                                                                        onClick={handleUploadButtonClick}
                                                                        disabled={loading}
                                                                >
                                                                        {loading && uploadLoading ?
                                                                                <span className='submitButtonSpinner' />
                                                                                :
                                                                                <img src={!files.length ? browse_icon : uploadButtonIcon} alt="Add file" />
                                                                        }
                                                                        {!files.length ?
                                                                                "Browse files"
                                                                                :
                                                                                uploadStatusMessage !== null ?
                                                                                        uploadStatusMessage
                                                                                        :
                                                                                        loading && uploadLoading ?
                                                                                                `Uploading ${files.length} file${files.length > 1 ? 's' : ''}`
                                                                                                :
                                                                                                `Upload ${files.length} file${files.length > 1 ? 's' : ''}`
                                                                        }
                                                                </button>

                                                                {files.length ? <button
                                                                        type="button"
                                                                        className='AdminDashboard_fileUpload_button Cancel'
                                                                        onClick={() => setFiles([])}
                                                                        disabled={loading}
                                                                >
                                                                        <img src={cross_icon} alt="Cancel upload" />
                                                                </button> : ""}
                                                        </div>
                                                </div>
                                        </div>
                                </section>

                                <section className='AdminDashboard_content_body'>
                                        <h2 className="AdminDashboard_content_title">
                                                <img src={content_icon} />
                                                Content
                                        </h2>
                                        <div className='AdminDashboard_contentManagement'>
                                                <button type="button" onClick={scrapeContent} className='AdminDashboard_extractButton' disabled={loading}>
                                                        {loading && extractLoading ? <span className='submitButtonSpinner' /> : ""}
                                                        {loading && extractLoading ? "Extracting content..." : "Extract New Content"}
                                                </button>

                                                {scrapedSections.length && !loading ?
                                                        <div className='AdminDashboard_extractionStatus'>
                                                                <p className="AdminDashboard_extractionStatus_status">{loading ? "Scraping..." : scrapingStatus}</p>
                                                                <p className='AdminDashboard_extractionStatus_lastExtracted'>Last extracted on: {lastExtracted}</p>
                                                        </div>
                                                        :
                                                        ""
                                                }

                                                <div className="AdminDashboard_extractedSections">
                                                        {scrapedSections ? scrapedSections.map((section, i) =>
                                                                <article key={i} className='AdminDashboard_extractedSection'>
                                                                        <h4 className='AdminDashboard_extractedSection_title'>{section.title}</h4>
                                                                        <p className='AdminDashboard_extractedSection_content'>{section.text}</p>
                                                                </article>
                                                        ) : ""}
                                                </div>
                                        </div>
                                </section>
                        </div>
                </main>
        </div>
}
