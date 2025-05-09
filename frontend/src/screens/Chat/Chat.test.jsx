import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { BrowserRouter } from 'react-router-dom'
import Chat from './Chat'

describe('Chatbot interaction', () => {
        it('renders user message, hourglass, then bot reply', async () => {
                render(
                        <BrowserRouter>
                                <Chat />
                        </BrowserRouter>
                )

                const input = screen.getByPlaceholderText(/message migration pathways chatbot/i)
                const sendBtn = screen.getByRole('button', { name: /send/i })

                await userEvent.type(input, 'Hello')
                await userEvent.click(sendBtn)

                const initial = screen.getAllByTestId('chat-message')
                expect(initial).toHaveLength(2)
                expect(initial[0]).toHaveTextContent('Hello')
                expect(initial[1]).toHaveTextContent('⏳')

                await waitFor(() => {
                        const updated = screen.getAllByTestId('chat-message');
                        expect(updated).toHaveLength(2);
                        expect(updated[1]).toHaveTextContent('This is a mock bot reply.');
                }, { timeout: 5000 });
        }, 10000)
})
