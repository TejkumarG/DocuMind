import { NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'

// GET /api/chat/messages - Retrieve all chat messages
export async function GET() {
  try {
    const messages = await prisma.chatMessage.findMany({
      orderBy: {
        createdAt: 'asc',
      },
    })
    return NextResponse.json(messages)
  } catch (error) {
    console.error('Error fetching messages:', error)
    return NextResponse.json(
      { error: 'Failed to fetch messages' },
      { status: 500 }
    )
  }
}

// POST /api/chat/messages - Save a new chat message
export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { role, content } = body

    if (!role || !content) {
      return NextResponse.json(
        { error: 'Role and content are required' },
        { status: 400 }
      )
    }

    if (role !== 'user' && role !== 'assistant') {
      return NextResponse.json(
        { error: 'Role must be either "user" or "assistant"' },
        { status: 400 }
      )
    }

    const message = await prisma.chatMessage.create({
      data: {
        role,
        content,
      },
    })

    return NextResponse.json(message, { status: 201 })
  } catch (error) {
    console.error('Error saving message:', error)
    return NextResponse.json(
      { error: 'Failed to save message' },
      { status: 500 }
    )
  }
}

// DELETE /api/chat/messages - Clear all chat history
export async function DELETE() {
  try {
    await prisma.chatMessage.deleteMany()
    return NextResponse.json({ message: 'Chat history cleared' })
  } catch (error) {
    console.error('Error clearing messages:', error)
    return NextResponse.json(
      { error: 'Failed to clear messages' },
      { status: 500 }
    )
  }
}
