"use client"

import type React from "react"
import { useState, useRef, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Send, Download, X } from "lucide-react"

interface Message {
  id: string
  text: string
  sender: "user" | "ai"
  type: "text" | "pdf-download"
  pdfUrl?: string
  isTyping?: boolean
  agentName?: string
}

interface ChatInterfaceProps {
  onClose?: () => void;
}

const SkeletonLoader = () => (
  <motion.div
    initial={{ opacity: 0, filter: "blur(10px)", y: 20 }}
    animate={{ opacity: 1, filter: "blur(0)", y: 0 }}
    exit={{ opacity: 0, filter: "blur(10px)", y: 20 }}
    transition={{ duration: 0.3 }}
    className="p-3 bg-white/10 backdrop-blur-md rounded-xl w-56 animate-pulse self-start"
  >
    <div className="h-4 bg-white/20 rounded mb-2 w-3/4" />
    <div className="h-4 bg-white/10 rounded w-1/2" />
  </motion.div>
)

const MessageBubble = ({ message }: { message: Message }) => {
  const isUser = message.sender === "user"
  const bubbleClass = isUser
    ? "self-end bg-slate-100 text-black"
    : "self-start bg-slate-800 text-white"

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
      className={`${bubbleClass} rounded-xl p-3 max-w-[70%]`}
    >
      {!isUser && message.agentName && <p className="text-xs text-white/60 mb-1">{message.agentName}</p>}
      {message.type === "text" && <p className="font-sans">{message.text}</p>}
      {message.type === "pdf-download" && message.pdfUrl && (
        <div className="flex flex-col items-center gap-2">
          <p className="text-center font-sans">{message.text}</p>
          <Button
            asChild
            className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-full shadow-md transition-all duration-300 ease-in-out transform hover:scale-105"
          >
            <a href={message.pdfUrl} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2">
              <Download className="h-5 w-5" />
              Download Ticket
            </a>
          </Button>
        </div>
      )}
    </motion.div>
  )
}

const Header = ({ onCloseChat }: { onCloseChat: () => void }) => (
  <header className="p-6 border-b border-white/10 flex items-center justify-between bg-black/30 backdrop-blur-md rounded-t-3xl">
    <h1 className="text-3xl font-bold text-white font-orbitron">AI Airline Assistant ✈️</h1>
    <Button
      variant="ghost"
      size="icon"
      onClick={onCloseChat}
      className="text-white/70 hover:text-white transition-colors"
      aria-label="Close chat"
    >
      <X className="h-6 w-6" />
    </Button>
  </header>
)

const Footer = () => (
  <footer className="p-4 border-t border-white/10 text-center bg-black/30 backdrop-blur-md rounded-b-3xl">
    <p className="text-sm text-white/70 font-sans">
      © 2024 AI Airline Assistant. All rights reserved. |{" "}
      <a href="#" className="hover:underline">
        Privacy Policy
      </a>{" "}|{" "}
      <a href="#" className="hover:underline">
        Terms of Service
      </a>
    </p>
  </footer>
)

export default function ChatInterface({ onClose }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isChatOpen, setIsChatOpen] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(scrollToBottom, [messages])

  useEffect(() => {
    if (isChatOpen && messages.length === 0) {
      setMessages([
        {
          id: "ai-greeting",
          text: "Hello, I am your travel assistant. Wanna book your seat?",
          sender: "ai",
          type: "text",
          agentName: "Travel Assistant",
        },
      ])
    }
  }, [isChatOpen, messages.length])

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMsg: Message = {
      id: Date.now().toString(),
      text: input,
      sender: "user",
      type: "text",
    }
    setMessages((m) => [...m, userMsg])
    setInput("")
    setIsLoading(true)

    const loaderId = `loader-${Date.now()}`
    setMessages((m) => [...m, { id: loaderId, text: "", sender: "ai", type: "text", isTyping: true }])

    try {
      const res = await fetch("http://localhost:8000/triage/send", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg.text }),
      })
      const data = await res.json()

      setMessages((m) => m.filter((msg) => msg.id !== loaderId))

      data.responses?.forEach((r: any) => {
        if (r.type === "message")
          setMessages((m) => [
            ...m,
            {
              id: `ai-${Date.now()}-${Math.random()}`,
              text: r.content,
              sender: "ai",
              type: "text",
              agentName: r.agent,
            },
          ])
      })

      if (data.pdf_url)
        setMessages((m) => [
          ...m,
          {
            id: `pdf-${Date.now()}`,
            text: "Your booking is confirmed! Download your ticket:",
            sender: "ai",
            type: "pdf-download",
            pdfUrl: `http://localhost:8000${data.pdf_url}`,
            agentName: "Booking Agent",
          },
        ])
    } catch {
      setMessages((m) => [
        ...m,
        {
          id: `err-${Date.now()}`,
          text: "Something went wrong. Try again.",
          sender: "ai",
          type: "text",
          agentName: "System",
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <AnimatePresence>
      {isChatOpen && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          transition={{ duration: 0.3 }}
          className="w-full max-w-3xl bg-black/30 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/10 flex flex-col h-[calc(100vh-2rem)] md:h-[80vh] z-40"
        >
          <Header onCloseChat={onClose ? onClose : () => setIsChatOpen(false)} />

          <div className="flex-1 p-6 overflow-y-auto space-y-4 chat-scroll-area">
            <AnimatePresence initial={false}>
              {messages.map((m) => (
                <motion.div
                  key={m.id}
                  layout
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                  className={`flex ${m.sender === "user" ? "justify-end" : "justify-start"}`}
                >
                  {m.isTyping ? <SkeletonLoader /> : <MessageBubble message={m} />}
                </motion.div>
              ))}
            </AnimatePresence>
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={sendMessage} className="p-6 border-t border-white/10 flex gap-3">
            <Input
              placeholder="Ask about your flight or book a seat..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="flex-1 bg-white/10 border-white/20 text-white placeholder:text-white/50 rounded-full px-5 py-3 focus:ring-2 focus:ring-blue-500 font-sans"
              disabled={isLoading}
            />
            <Button
              type="submit"
              disabled={isLoading}
              className="bg-blue-500 text-white rounded-full p-3 hover:bg-blue-600 transition-colors"
            >
              <Send className="h-5 w-5" />
              <span className="sr-only">Send</span>
            </Button>
          </form>

          <Footer />
        </motion.div>
      )}
      {!isChatOpen && (
        <motion.div
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -50 }}
          transition={{ duration: 0.5 }}
          className="text-center p-8 max-w-4xl space-y-6"
        >
          <Button
            onClick={() => setIsChatOpen(true)}
            className="mt-8 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-full text-lg shadow-lg transition-all duration-300 ease-in-out transform hover:scale-105"
          >
            Book Your Seat Now
          </Button>
        </motion.div>
      )}
    </AnimatePresence>
  )
} 