// src/screens/Admin/AdminDashboard.test.jsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect } from 'vitest'
import { BrowserRouter } from 'react-router-dom'
import AdminDashboard from './AdminDashboard'

describe('<AdminDashboard />', () => {
        it('fetches and displays users with correct Ban/Unban icons', async () => {
                render(
                        <BrowserRouter>
                                <AdminDashboard />
                        </BrowserRouter>
                )

                const aliceCell = await screen.findByText('Alice')
                const bobCell   = await screen.findByText('Bob')
                expect(aliceCell).toBeInTheDocument()
                expect(bobCell).toBeInTheDocument()

                const banAliceBtn = screen.getByRole('button', { name: /Ban Alice/i })
                expect(banAliceBtn).toBeInTheDocument()

                const unbanBobBtn = screen.getByRole('button', { name: /Unban Bob/i })
                expect(unbanBobBtn).toBeInTheDocument()
        })

        it('shows initial scraped content and updates on re‐scrape', async () => {
                render(
                        <BrowserRouter>
                                <AdminDashboard />
                        </BrowserRouter>
                )

                await screen.findByText('Content fetched.')
                expect(screen.getByText('Last extracted on: 2025-05-01T12:00:00Z')).toBeInTheDocument()
                expect(screen.getByText('Section A')).toBeInTheDocument()
                expect(screen.getByText('Initial text A')).toBeInTheDocument()
                expect(screen.getByText('Section B')).toBeInTheDocument()
                expect(screen.getByText('Initial text B')).toBeInTheDocument()

                const extractBtn = screen.getByRole('button', { name: /Extract New Content/i })
                await userEvent.click(extractBtn)

                await screen.findByText('Freshly scraped.')
                expect(screen.getByText('Last extracted on: 2025-05-30T09:00:00Z')).toBeInTheDocument()
                expect(screen.getByText('Section C')).toBeInTheDocument()
                expect(screen.getByText('New text C')).toBeInTheDocument()
        })
})

describe('AdminDashboard – Knowledge Addition', () => {
        it('adds a website URL successfully', async () => {
                render(
                        <BrowserRouter>
                                <AdminDashboard />
                        </BrowserRouter>
                )

                await screen.findByText('Add Website')

                const urlInput = screen.getByPlaceholderText(/Enter website URL/i)
                const addButton = screen.getByRole('button', { name: /Add$/i })

                await userEvent.type(urlInput, 'https://example.org/data')
                await userEvent.click(addButton)

                const addedButton = await screen.findByRole(
                        'button',
                        { name: /Added!/i },
                        { timeout: 2000 }
                )
                expect(addedButton).toBeInTheDocument()

                expect(urlInput).toHaveValue('')
        })

        it('uploads a file successfully', async () => {
                render(
                        <BrowserRouter>
                                <AdminDashboard />
                        </BrowserRouter>
                )

                await screen.findByText('Add File')

                const file = new File(['hello'], 'hello.txt', { type: 'text/plain' })

                const fileInput = document.querySelector('input[type="file"]')
                await userEvent.upload(fileInput, file)

                const uploadButton = screen.getByRole('button', {
                        name: /Upload 1 file/i
                })
                await userEvent.click(uploadButton)

                const uploadedMsg = await screen.findByText(/Uploaded!/i, {
                        timeout: 2000
                })
                expect(uploadedMsg).toBeInTheDocument()
        })
})
