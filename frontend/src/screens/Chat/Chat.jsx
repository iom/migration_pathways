import './Chat.css'

import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import Markdown from 'react-markdown'

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL

import appIcon from "../../assets/images/myrafiki_icon.svg"
import logo from "../../assets/images/App_logo.svg"
import altlogo from "../../assets/images/myrafiki_logo_alternate.svg"
import showChats from "../../assets/images/showChats.svg"
import downloadChat from "../../assets/images/downloadChat.svg"
import dp from "../../assets/images/dp.png"
import logout_icon from "../../assets/images/Header_logout.svg"
import downarrow from "../../assets/images/downarrow.svg"
import bulb from "../../assets/images/Chat_bulb.svg"
import fileIcon from "../../assets/images/Chat_fileIcon.svg"
import cross from "../../assets/images/Chat_cross.svg"
import attachIcon from "../../assets/images/Chat_attachIcon.svg"
import sendIcon from "../../assets/images/Chat_sendIcon.svg"

export default function Chat ()
{
        const [username, setUsername] = useState("")
        const [email, setEmail] = useState("")

        const navigate = useNavigate()

        const [preferences, setPreferences] = useState({
                sourceCountry: "",
                destinationCountry: ""
        })

        useEffect(() => {
                async function fetchProfile ()
                {
                        const response = await fetch(`${API_BASE_URL}/profile`, {
                                method: 'GET',
                                headers: { 'Content-Type': 'application/json' },
                                credentials: 'include'
                        })

                        if (response.ok) {
                                const data = await response.json()
                                setUsername(data.username)
                                setEmail(data.email)
                                setPreferences({
                                        sourceCountry: data.source_country,
                                        destinationCountry: data.destination_country
                                })
                                setMessages({ messages: data.conversation })
                        }
                        else if(response.status === 401)
                        {
                                sessionStorage.setItem("session_expired", "Session expired. Please login again.")
                                navigate("/login")
                        }
                        else
                                navigate("/login")
                }

                fetchProfile()
        }, [navigate])

        const messagesRef = useRef()
        const [messages, setMessages] = useState(null)
        async function handleSendClick ()
        {
                const localInput = input

                setMessages(p => {
                        if(p && p.messages && p.messages.length)
                        {
                                return {
                                        messages: [
                                                ...p.messages,
                                                {
                                                        sender: "user",
                                                        text: localInput
                                                },
                                                {
                                                        sender: "assistant",
                                                        text: "⏳"
                                                }
                                        ]
                                }
                        }
                        else
                        {
                                return {
                                        messages: [
                                                {
                                                        sender: "user",
                                                        text: localInput
                                                },
                                                {
                                                        sender: "assistant",
                                                        text: "⏳"
                                                }
                                        ]
                                }
                        }
                })

                setInput("")

                try
                {
                        const response = await fetch(`${API_BASE_URL}/chat/crew`, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                credentials: 'include',
                                body: JSON.stringify({ "message": localInput }),
                        })

                        if(response.ok)
                        {
                                const responseJson = await response.json()

                                setMessages(p => ({
                                        messages: [
                                                ...p.messages.slice(0, -1),
                                                {
                                                        sender: "assistant",
                                                        text: responseJson.text
                                                }
                                        ]
                                }))
                        }
                        else if(response.status === 401)
                        {
                                sessionStorage.setItem("session_expired", "Session expired. Please login again.")
                                navigate("/login")
                        }
                        else
                        {
                                setMessages(p => ({
                                        messages: [
                                                ...p.messages.slice(0, -1),
                                                {
                                                        sender: "assistant",
                                                        text: "Error: unable to get reply."
                                                }
                                        ]
                                }))
                        }
                }
                catch (error)
                {
                        setMessages(p => ({
                                messages: [
                                        ...p.messages.slice(0, -1),
                                        {
                                                sender: "assistant",
                                                text: "Network error."
                                        }
                                ]
                        }))
                }
        }
        useEffect(() => {
                const domNode = messagesRef.current

                if(domNode && messages.messages.at(-1).sender === 'assistant' && messages.messages.at(-1).text === "⏳")
                        domNode.scrollTop = domNode.scrollHeight
        }, [messages])

        function handleEnterClick (e)
        {
                if(e.key === "Enter" && input.trim().length && !(messagesRef.current && messages.messages.at(-1).text === "⏳"))
                {
                        e.preventDefault()
                        handleSendClick()
                }
        }

        const templates = [
                {
                        bgcolor: "#E5E6FF",
                        iconBgcolor: "#0008FF",
                        title: "Visa & Legal Requirements",
                        query: `What documents do I need to legally migrate from ${preferences.sourceCountry ?? "my country"} to ${preferences.destinationCountry ?? "the destination country"}?`
                },
                {
                        bgcolor: "#FFF0E9",
                        iconBgcolor: "#FF671F",
                        title: "Planning Your Migration Journey",
                        query: `How can I plan a safe and legal migration journey from ${preferences.sourceCountry ?? "my country"}?`
                },
                {
                        bgcolor: "#FFF9ED",
                        iconBgcolor: "#FFC649",
                        title: "Settling Abroad",
                        query: `What should I know about living in ${preferences.destinationCountry ?? "the destination country"}, including housing and healthcare?`
                },
                {
                        bgcolor: "#E6F6F5",
                        iconBgcolor: "#01A89A",
                        title: "Employment Opportunities",
                        query: `How can I find legitimate job opportunities in ${preferences.destinationCountry ?? "the destination country"}?`
                }
        ]

        const [input, setInput] = useState("")

        const dialogRef = useRef()
        const [clickedQuery, setClickedQuery] = useState(null)
        const [localSourceCountry, setLocalSourceCountry] = useState("")
        const [localDestinationCountry, setLocalDesinationCountry] = useState("")
        function handleTemplateClick (query)
        {
                if(!preferences.sourceCountry || !preferences.destinationCountry)
                {
                        setClickedQuery(query)
                        dialogRef.current.showModal()
                }
                else
                        setInput(templates[query].query)
        }
        function handleDialogClose () {
                setClickedQuery(null)
                setLocalSourceCountry("")
                setLocalDesinationCountry("")
                dialogRef.current.close()
        }
        async function handleDialogSubmit (e) {
                e.preventDefault()

                const response = await fetch(`${API_BASE_URL}/preferences`, {
                        method: "POST",
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                                source_country: localSourceCountry,
                                destination_country: localDestinationCountry
                        }),
                        credentials: 'include'
                })

                if(response.ok)
                {
                        setPreferences({
                                sourceCountry: localSourceCountry,
                                destinationCountry: localDestinationCountry
                        })
                }
                else if(response.status === 401)
                {
                        sessionStorage.setItem("session_expired", "Session expired. Please login again.")
                        navigate("/login")
                }

                // else
                        // navigate("/login")
        }
        useEffect(() => {
                if(preferences.sourceCountry && preferences.destinationCountry && (clickedQuery !== null && clickedQuery >= 0))
                {
                        setInput(templates[clickedQuery].query)
                        handleDialogClose()
                }
        }, [...Object.values(preferences)])

        async function handleLogoutClick ()
        {
                const response = await fetch(`${API_BASE_URL}/logout`, {
                        method: "POST",
                        credentials: "include",
                        headers: { "Content-Type": "application/json" }
                })

                if(response)
                        navigate("/login")
        }

        const textareaRef = useRef()

        return  <div className='Chat'>
                <dialog className='Chat_countryDialogContainer' ref={dialogRef}>
                        <form method='dialog' className="Chat_countryDialog" onSubmit={handleDialogSubmit}>
                                <button type="button" className='Chat_countryDialog_close' onClick={handleDialogClose}>
                                        <img src={cross}  />
                                </button>

                                <header className='Chat_countryDialog_titleContainer'>
                                        <img className="Chat_landing_topLogo" src={altlogo} />

                                        <span>
                                                <h3 className='Chat_countryDialog_title'>Tell me more about yourself.</h3>
                                                <p className='Chat_countryDialog_subtitle'>It will help me give you relevant answers.</p>
                                        </span>
                                </header>

                                <main className='Chat_countryDialog_inputs'>
                                        <label htmlFor='Chat_countryDialog_sourceCountryInput'>What country are you from?</label>
                                        <input type="text" id="Chat_countryDialog_sourceCountryInput" value={localSourceCountry} onChange={e => setLocalSourceCountry(e.target.value)} placeholder="Enter your country's name" />

                                        <label htmlFor='Chat_countryDialog_destinationCountryInput'>What country are you migrating to?</label>
                                        <input type="text" id="Chat_countryDialog_destinationCountryInput" value={localDestinationCountry} onChange={e => setLocalDesinationCountry(e.target.value)} placeholder="Enter your destination's name" />
                                </main>

                                <footer className='Chat_countryDialog_buttons'>
                                        <button type="button" className='Chat_countryDialog_button cancel' onClick={handleDialogClose}>Cancel</button>
                                        <button type="submit" className='Chat_countryDialog_button submit' disabled={localSourceCountry.length < 4 || localDestinationCountry.length < 4}>Submit</button>
                                </footer>
                        </form>
                </dialog>

                <header className='Chat-header'>
                        <div className='Chat_header-left'>
                                <img className='Chat_header_left_appLogo' src={logo} alt="My Rafiki" />
                        </div>

                        <div className='Chat_header-right'>
                                <button className="Chat_header_right_profileItemsContainer" popoverTarget='ID_Chat_logoutPopover'>
                                        <div className="Chat_header_dp">{username && username.split('')[0].toUpperCase()}</div>

                                        <div className='Chat_header_right-nameContainer'>
                                                <div className='Chat_header_right_nameContainer-name'>{username && username}</div>
                                                <div className='Chat_header_right_nameContainer-email'>{email && email}</div>
                                        </div>

                                        <img className="Chat_header_downarrow" src={downarrow} alt="My Rafiki" />
                                </button>

                                <div popover='auto' id="ID_Chat_logoutPopover" className='Chat_logoutPopover' onClick={handleLogoutClick}>
                                        <img src={logout_icon} />
                                        Logout
                                </div>
                        </div>
                </header>

                <main className='Chat-content'>
                        {messages && messages.messages && messages.messages.length > 0 ?
                                <div className='Chat_messageList' ref={messagesRef}>
                                        {messages.messages.map((message, i) =>
                                                <div key={i} className='Chat_messageContainer'>
                                                        <div className="Chat_assistantDpContainer">
                                                                {message.sender !== "user" ? <img className='Chat_assistantDp' src={appIcon} />: ""}
                                                        </div>

                                                        <div key={i} className={`Chat_message ${message.sender === "user" ? "user" : ""}`} data-testid="chat-message">
                                                                <Markdown
                                                                        components={{
                                                                                a(props) {
                                                                                        const {node, target, ...rest} = props
                                                                                        return <a target="_blank" {...rest} />
                                                                                }
                                                                        }}
                                                                >
                                                                        {message.text}
                                                                </Markdown>
                                                        </div>

                                                        <div className="Chat_userDpContainer">
                                                                {message.sender === "user" ? <div className="Chat_header_dp">{username && username.split('')[0].toUpperCase()}</div> : ""}
                                                        </div>
                                                </div>
                                        )}
                                </div>
                                :
                                <div className='Chat_landing'>
                                        <header className='Chat_landing_titleContainer'>
                                                <img className="Chat_landing_topLogo" src={altlogo} />
                                                <h3 className='Chat_landing_title'>What can I help with?</h3>
                                        </header>

                                        <main className='Chat_landing_templateContainer'>
                                                {templates.map((template, i) =>
                                                        <button type="button" key={i} onClick={() => handleTemplateClick(i)} className="Chat_landing_template" style={{background: template.bgcolor}}>
                                                                <h6 className="Chat_landing_templateTitle">
                                                                        <div className="Chat_landing_template_icon" style={{background: template.iconBgcolor}}>
                                                                                <img src={fileIcon} />
                                                                        </div>
                                                                        {template.title}
                                                                </h6>

                                                                <p className="Chat_landing_templateContent">"{template.query}"</p>
                                                        </button>
                                                )}
                                        </main>

                                        <footer className='Chat_landing_footerContainer'>
                                                <img className='Chat_landing_footerIcon' src={bulb} />
                                                You can also type in your query and hit send.
                                        </footer>
                                </div>
                        }
                </main>

                <footer className='Chat_inputContainer'>
                        {/* <button type="button" className="Chat_inputButtons_attach">
                                <img src={attachIcon} />
                        </button> */}

                        <textarea ref={textareaRef} value={input} onChange={e => setInput(e.target.value)} onKeyDown={handleEnterClick} placeholder="Message MIGRATION PATHWAYS Chatbot" className="Chat_input" />

                        <button type="button" aria-label="send" className="Chat_inputButtons_send" onClick={handleSendClick} disabled={!input.trim().length || (messagesRef.current && messages.messages.at(-1).text === "⏳")}>
                                <img src={sendIcon} />
                        </button>
                </footer>
        </div>
}
