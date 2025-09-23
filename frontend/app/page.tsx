'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Button } from "@/app/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/app/components/ui/card"
import { 
  FileText, 
  BrainCircuit, 
  MonitorPlay, 
  Code, 
  Download,
  Bot,
  Zap,
  MousePointerClick,
  Layers,
  Eye,
  Palette
} from 'lucide-react'

export default function Home() {
  const features = [
    {
      title: "AI-Powered Agents",
      description: "Specialized AI agents handle each step of the QA automation process, from story enhancement to code generation.",
      icon: Bot,
    },
    {
      title: "End-to-End Automation",
      description: "Transform user stories to production-ready test scripts with a single click through our automated pipeline.",
      icon: Zap,
    },
    {
      title: "Browser-Use Integration",
      description: "Live browser interaction for data gathering and real-time execution tracking with detailed debugging capabilities.",
      icon: MousePointerClick,
    },
    {
      title: "Multi-Framework Support",
      description: "Generate test scripts for Playwright, Selenium, Cypress, Robot Framework, and more.",
      icon: Layers,
    },
    {
      title: "Detailed Debugging",
      description: "Access recordings, screenshots, network traces, and AI vision analysis for comprehensive debugging.",
      icon: Eye,
    },
    {
      title: "Professional UI",
      description: "Modern interface built with shadcn/ui for a seamless and intuitive user experience.",
      icon: Palette,
    },
  ]

  const pipelineSteps = [
    {
      title: "Provide User Story",
      description: "Start by entering your user story or Jira ticket for automation",
      icon: FileText,
    },
    {
      title: "AI-Powered Enhancement & Test Generation",
      description: "Our AI agents enhance your story and generate comprehensive manual test cases",
      icon: BrainCircuit,
    },
    {
      title: "Automated Browser Execution",
      description: "Execute Gherkin scenarios in real browsers with detailed tracking",
      icon: MonitorPlay,
    },
    {
      title: "Multi-Framework Code Generation",
      description: "Generate ready-to-run automation code in your preferred framework",
      icon: Code,
    },
    {
      title: "Receive Production-Ready Code",
      description: "Get clean, professional test automation code ready for integration",
      icon: Download,
    },
  ]

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="relative overflow-hidden bg-gradient-to-br from-primary to-secondary py-20">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTAgMGg2MHY2MEgweiIgZmlsbD0iI2ZmZiIgZmlsbC1vcGFjaXR5PSIwLjA1Ii8+CjxwYXRoIGQ9Ik0zMCAzMGMtOC4yODQzIDAtMTUgNi43MTU3LTE1IDE1cy02LjcxNTcgMTUtMTUgMTVzMTEuNzE1NyAxNSAxNSAxNSAxNS02LjcxNTcgMTUtMTVjMC04LjI4NDMtNi43MTU3LTE1LTE1LTE1eiIgZmlsbD0iI2ZmZiIgZmlsbC1vcGFjaXR5PSIwLjEiLz4KPC9zdmc+')]"></div>
        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-6">
              From User Story to Test Code in a Single Click
            </h1>
            <p className="text-xl text-blue-100 mb-10 max-w-2xl mx-auto">
              Leverage a suite of specialized AI agents to automate your entire QA workflow, from requirements to ready-to-run test scripts.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button asChild size="lg" className="bg-white text-primary hover:bg-blue-50">
                <Link href="/dashboard/pipeline">
                  Get Started
                </Link>
              </Button>
              <Button asChild size="lg" variant="outline" className="border-white text-white hover:bg-white/10">
                <Link href="/about">
                  Learn More
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* How It Works Section */}
      <section className="py-20 bg-background-light">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">How It Works</h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Our automated pipeline transforms your user stories into production-ready test automation code through 5 simple steps
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
            {pipelineSteps.map((step, index) => {
              const Icon = step.icon
              return (
                <Card key={index} className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300 bg-white/40 backdrop-blur-lg rounded-2xl">
                  <CardHeader className="text-center pb-4">
                    <div className="mx-auto bg-primary/10 p-3 rounded-full w-16 h-16 flex items-center justify-center mb-4">
                      <Icon className="h-8 w-8 text-primary" />
                    </div>
                    <CardTitle className="text-lg">{step.title}</CardTitle>
                  </CardHeader>
                  <CardContent className="text-center pt-0">
                    <p className="text-sm text-muted-foreground">{step.description}</p>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>
      </section>

      {/* Key Features Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Key Features</h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Everything you need to revolutionize your QA automation process
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <Card key={index} className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300 bg-white/40 backdrop-blur-lg rounded-2xl">
                  <CardHeader>
                    <div className="flex items-center space-x-4">
                      <div className="bg-primary/10 p-2 rounded-lg">
                        <Icon className="h-6 w-6 text-primary" />
                      </div>
                      <CardTitle>{feature.title}</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground">{feature.description}</p>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-20 bg-gradient-to-r from-primary to-secondary">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Ready to Revolutionize Your QA?
          </h2>
          <p className="text-xl text-blue-100 mb-10 max-w-2xl mx-auto">
            Join forward-thinking teams who have transformed their testing workflow with SDET-GENIE
          </p>
          <Button asChild size="lg" className="bg-white text-primary hover:bg-blue-50 text-lg px-8 py-3">
            <Link href="/dashboard/pipeline">
              Launch the Pipeline
            </Link>
          </Button>
        </div>
      </section>
    </div>
  )
}