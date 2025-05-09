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
import downarrow from "../../assets/images/downarrow.svg"
import bulb from "../../assets/images/Chat_bulb.svg"
import fileIcon from "../../assets/images/Chat_fileIcon.svg"
import attachIcon from "../../assets/images/Chat_attachIcon.svg"
import sendIcon from "../../assets/images/Chat_sendIcon.svg"

export default function Chat ()
{
        const [username, setUsername] = useState("John Doe")
        const [email, setEmail] = useState("johndoe@example.com")

        const navigate = useNavigate()
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
                                setMessages({ messages: data.conversation })
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
                        if(p && p.messages.length)
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
                        const response = await fetch(`${API_BASE_URL}/chat`, {
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
                if(e.key === "Enter" && input.trim().length)
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
                        query: "What documents do I need to legally migrate from my country to the destination country?"
                },
                {
                        bgcolor: "#FFF0E9",
                        iconBgcolor: "#FF671F",
                        title: "Planning Your Migration Journey",
                        query: "How can I plan a safe and legal migration journey from my country?"
                },
                {
                        bgcolor: "#FFF9ED",
                        iconBgcolor: "#FFC649",
                        title: "Settling Abroad",
                        query: "What should I know about living in the destination country, including housing and healthcare?"
                },
                {
                        bgcolor: "#E6F6F5",
                        iconBgcolor: "#01A89A",
                        title: "Employment Opportunities",
                        query: "How can I find legitimate job opportunities in the destination country?"
                }
        ]

        const [input, setInput] = useState("")

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
                <header className='Chat-header'>
                        <div className='Chat_header-left'>
                                <img className='Chat_header_left_appLogo' src={logo} alt="My Rafiki" />
                        </div>

                        <div className='Chat_header-right'>
                                <img src={downloadChat} alt="My Rafiki" />
                                <img src={showChats} alt="My Rafiki" />
                                <div className="Chat_header_right_profileItemsContainer" onClick={handleLogoutClick} >
                                        <img className="Chat_header_dp" src={dp} alt="My Rafiki" />
                                        <div className='Chat_header_right-nameContainer'>
                                                <div className='Chat_header_right_nameContainer-name'>{username}</div>
                                                <div className='Chat_header_right_nameContainer-email'>{email}</div>
                                        </div>
                                        <img className="Chat_header_downarrow" src={downarrow} alt="My Rafiki"/>
                                </div>
                        </div>
                </header>

                <main className='Chat-content'>
                        {messages && messages.messages.length > 0 ?
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
                                                                {message.sender === "user" ? <img className='Chat_userDp' src={dp} /> : ""}
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
                                                        <button type="button" key={i} onClick={() => setInput(template.query)} className="Chat_landing_template" style={{background: template.bgcolor}}>
                                                                <h6 className="Chat_landing_templateTitle">
                                                                        <div className="Chat_landing_template_icon" style={{background: template.iconBgcolor}}>
                                                                                <img src={fileIcon} />
                                                                        </div>
                                                                        {template.title}
                                                                </h6>

                                                                <p className="Chat_landing_templateContent" onClick={() => setInput(template.query)}>"{template.query}"</p>
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

                        <button type="button" aria-label="send" className="Chat_inputButtons_send" onClick={handleSendClick} disabled={!input.trim().length}>
                                <img src={sendIcon} />
                        </button>
                </footer>
        </div>
}
