'use client'

import { useState } from 'react'

export default function Header() {
  const [isModelSelectorOpen, setIsModelSelectorOpen] = useState(false)
  
  return (
    <header className="bg-white shadow">
      <div className="px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
        <div>
          <h1 className="text-lg font-semibold text-gray-900">SDET-GENIE Dashboard</h1>
          <p className="text-sm text-gray-500">AI-Powered QA Automation Framework</p>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="relative">
            <button
              onClick={() => setIsModelSelectorOpen(!isModelSelectorOpen)}
              className="flex items-center text-sm font-medium text-gray-700 hover:text-gray-900"
            >
              <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-white text-xs">
                G
              </div>
              <span className="ml-2">Google Gemini 2.0 Flash</span>
            </button>
            
            {isModelSelectorOpen && (
              <div className="absolute right-0 mt-2 w-64 bg-white rounded-md shadow-lg py-1 z-10">
                <div className="px-4 py-2 border-b">
                  <h3 className="text-sm font-medium text-gray-900">Select LLM Provider</h3>
                </div>
                <div className="px-4 py-2">
                  <select className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary">
                    <option>Google</option>
                    <option>OpenAI</option>
                    <option>Anthropic</option>
                    <option>Groq</option>
                  </select>
                </div>
                <div className="px-4 py-2">
                  <select className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary">
                    <option>gemini-2.0-flash</option>
                    <option>gemini-2.5-pro</option>
                    <option>gpt-4o</option>
                    <option>claude-3-7-sonnet-latest</option>
                  </select>
                </div>
              </div>
            )}
          </div>
          
          <button className="bg-primary text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-primary-dark">
            Settings
          </button>
        </div>
      </div>
    </header>
  )
}