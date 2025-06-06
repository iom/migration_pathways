import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi, describe, it, afterEach } from 'vitest'
import { BrowserRouter } from 'react-router-dom'

import AdminLogin from './AdminLogin'
import AdminDashboard from '../AdminDashboard/AdminDashboard'

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
        const actual = await vi.importActual('react-router-dom')
        return {
                ...actual,
                useNavigate: () => mockNavigate,
        }
})

afterEach(() => {
        mockNavigate.mockReset()
})

describe('Admin – login, dashboard display, and logout', () => {
        it('logs in, shows profile, then logs out', async () => {
                const { rerender } = render(
                        <BrowserRouter>
                                <AdminLogin />
                        </BrowserRouter>
                )

                await userEvent.type(screen.getByLabelText(/email/i), 'admin@example.com')
                await userEvent.type(screen.getByLabelText(/password/i), 'Admin123!')
                await userEvent.click(screen.getByRole('button', { name: /login/i }))

                expect(mockNavigate).toHaveBeenCalledWith('/admindashboard')

                rerender(
                        <BrowserRouter>
                                <AdminDashboard />
                        </BrowserRouter>
                )

                await screen.findByText(/Admin User/i)
                expect(screen.getByText('admin@example.com')).toBeInTheDocument()

                await userEvent.click(screen.getByRole('button', { name: /logout/i }))

                expect(mockNavigate).toHaveBeenLastCalledWith('/adminlogin')
        })
})
