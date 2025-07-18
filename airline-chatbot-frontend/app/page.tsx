"use client"

import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/button"
import ChatInterface from "@/components/ChatInterface"
import { useState } from "react"

export default function MainPage() {
  const [isOpen, setIsOpen] = useState<boolean>(false)

  return (
    <main className="relative flex flex-col items-center justify-center min-h-screen p-4">
      {/* Hero Section or Chat */}
      {isOpen ? (
        <>
          <ChatInterface onClose={() => setIsOpen(false)} />
        </>
      ) : (
        <AnimatePresence>
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            transition={{ duration: 0.5 }}
            className="text-center p-8 max-w-4xl space-y-6"
          >
            <h1 className="text-4xl sm:text-6xl font-bold text-white bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-cyan-300 leading-tight font-orbitron">
              Your Journey, Simplified.
            </h1>
            <p className="text-lg sm:text-xl text-white/80 max-w-2xl mx-auto font-sans">
              Experience seamless travel with our AI-powered airline assistant. From booking to boarding, we're here to
              help.
            </p>
            <Button
              onClick={() => setIsOpen(true)}
              className="mt-8 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-full text-lg shadow-lg transition-all duration-300 ease-in-out transform hover:scale-105"
            >
              Book Your Seat Now
            </Button>
          </motion.div>
        </AnimatePresence>
      )}
    </main>
  )
}
