import { describe, it, expect, vi, afterEach } from "vitest"
import { streamChat } from "../services/api"

function sseResponse(chunks: string[]) {
  const enc = new TextEncoder()
  const body = new ReadableStream({
    start(c) { chunks.forEach(x => c.enqueue(enc.encode(x))); c.close() },
  })
  return new Response(body, { status: 200 })
}

afterEach(() => vi.unstubAllGlobals())

describe("streamChat", () => {
  it("throws on a non-OK response", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("", { status: 500 })))
    await expect(streamChat("hi").next()).rejects.toThrow("HTTP 500")
  })

  it("posts the question to /api/chat/stream", async () => {
    const f = vi.fn().mockResolvedValue(sseResponse([]))
    vi.stubGlobal("fetch", f)
    for await (const _ of streamChat("hello", "c1")) { /* drain */ }
    expect(f.mock.calls[0][0]).toBe("/api/chat/stream")
    expect(JSON.parse(f.mock.calls[0][1].body)).toEqual({ question: "hello", conversation_id: "c1" })
  })
})
