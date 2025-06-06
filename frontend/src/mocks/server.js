import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL

export const server = setupServer(
        http.post(`${API_BASE_URL}/login`, async ({ request }) => {
                const { email, password } = await request.json()

                if (email === 'karan@gmail.com' && password === 'Karan123')
                {
                        return new HttpResponse(null, {
                                status: 200,
                                headers: { 'Set-Cookie': 'token=fake-token HttpOnly Path=/ Secure' }
                        })
                }
                else
                {
                        return new HttpResponse(
                                JSON.stringify({ message: 'Invalid credentials' }),
                                { status: 401, headers: { 'Content-Type': 'application/json' } }
                        )
                }
        }),

        http.get(`${API_BASE_URL}/profile`, () =>
                HttpResponse.json({
                        username: 'Karan',
                        email: 'karan@gmail.com'
                })
        ),

        http.post(`${API_BASE_URL}/chat`, async () => {
                await new Promise((r) => setTimeout(r, 200))
                return new HttpResponse(
                        JSON.stringify({ text: 'This is a mock bot reply.' }),
                        { status: 200, headers: { 'Content-Type': 'application/json' } }
                )
        }),

        http.post(`${API_BASE_URL}/admin/login`, async ({ request }) => {
                const { email, password } = await request.json()
                if (email === 'admin@example.com' && password === 'Admin123!') {
                        return new HttpResponse(null, {
                                status: 200,
                                headers: { 'Set-Cookie': 'session=abc123; HttpOnly' },
                        })
                }
                return new HttpResponse(JSON.stringify({ error: 'Invalid credentials' }), {
                                status: 401,
                                headers: { 'Content-Type': 'application/json' }
                        }
                )
        }),

        http.get(`${API_BASE_URL}/admin/profile`, () =>
                HttpResponse.json({ username: 'Admin User', email: 'admin@example.com' })
        ),

        http.get(`${API_BASE_URL}/admin/users`, () =>
                HttpResponse.json({
                        users: [
                                {
                                        id: 1,
                                        username: 'Alice',        // ← use username, not name
                                        email: 'alice@example.com',
                                        request_count: 5,         // provide something for that column
                                        active: true,             // or false, depending on your logic
                                },
                                {
                                        id: 2,
                                        username: 'Bob',
                                        email: 'bob@example.com',
                                        request_count: 2,
                                        active: false,
                                },
                        ],
                })
        ),

        http.post(`${API_BASE_URL}/admin/logout`, () =>
                new HttpResponse(null, { status: 200 })
        ),

        http.get(`${API_BASE_URL}/admin/users`, () =>
                HttpResponse.json({
                        users: [
                                { id: 1, username: 'Alice', email: 'alice@example.com', request_count: 3, active: true },
                                { id: 2, username: 'Bob',   email: 'bob@example.com',   request_count: 1, active: false },
                        ],
                })
        ),

        http.get(`${API_BASE_URL}/admin/extractions`, () =>
                HttpResponse.json({
                        last_updated_on: '2025-05-01T12:00:00Z',
                        sections: [
                                { title: 'Section A', text: 'Initial text A' },
                                { title: 'Section B', text: 'Initial text B' },
                        ],
                })
        ),

        http.post(`${API_BASE_URL}/admin/extract`, async () =>
                HttpResponse.json({
                        message: 'Freshly scraped.',
                        last_updated_on: '2025-05-30T09:00:00Z',
                        sections: [
                                { title: 'Section A', text: 'New text A' },
                                { title: 'Section B', text: 'New text B' },
                                { title: 'Section C', text: 'New text C' },
                        ],
                })
        ),

        http.post(`${API_BASE_URL}/get-security-question`, async ({ request }) => {
                const { email } = await request.json()
                if (email === 'user@example.com') {
                        return HttpResponse.json({ question: "What's your pet's name?" })
                }
                return new HttpResponse(JSON.stringify({ error: 'Email not found' }), {
                        status: 404, headers: { 'Content-Type': 'application/json'
                }})
        }),

        http.post(`${API_BASE_URL}/verify-security-answer`, async ({ request }) => {
                const { email, security_answer } = await request.json()
                if (email === 'user@example.com' && security_answer === 'fluffy') {
                        return new HttpResponse(null, { status: 200 })
                }
                return new HttpResponse(JSON.stringify({ error: 'Incorrect answer' }), {
                        status: 401, headers: { 'Content-Type': 'application/json'
                }})
        }),

        http.post(`${API_BASE_URL}/update-password`, async ({ request }) => {
                const { email, security_answer, new_password } = await request.json()
                if (email === 'user@example.com' && security_answer === 'fluffy' && new_password.length >= 8) {
                        return new HttpResponse(null, {
                                status: 200,
                                headers: { 'Set-Cookie': 'token=reset-token; HttpOnly; Path=/; Secure' }
                        })
                }
                return new HttpResponse(JSON.stringify({ error: 'Reset failed' }), {
                        status: 400, headers: { 'Content-Type': 'application/json'
                }})
        }),

        http.post(`${API_BASE_URL}/admin/add-url`, async ({ request }) => {
                const { email, url } = await request.json()
                if (url && email)
                {
                        return HttpResponse.json({ message: 'URL added' }, { status: 200 });
                }
                return new HttpResponse(JSON.stringify({ error: 'Bad Request' }), {
                        status: 400,
                        headers: { 'Content-Type': 'application/json' }
                });
        }),

        http.post(`${API_BASE_URL}/admin/upload-doc`, async () => {
                return new HttpResponse(null, { status: 200 });
        }),
)
