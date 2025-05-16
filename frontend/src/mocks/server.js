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

        http.post(`${API_BASE_URL}/chat`, async () => {
                await new Promise((r) => setTimeout(r, 200))
                return new HttpResponse(
                        JSON.stringify({ text: 'This is a mock bot reply.' }),
                        { status: 200, headers: { 'Content-Type': 'application/json' } }
                )
        })
)
