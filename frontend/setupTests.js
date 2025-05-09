import { server } from './src/mocks/server'
import { beforeAll, afterAll, afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'
import '@testing-library/jest-dom'

beforeAll(() => server.listen())
afterEach(() => {
        server.resetHandlers()
        cleanup()
})
afterAll(() => server.close())
