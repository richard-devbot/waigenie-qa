'use client'

import Sidebar from '@/app/layout/Sidebar'
import Header from '@/app/layout/Header'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="flex-1 p-6 bg-background-light">
          {children}
        </main>
      </div>
    </div>
  )
}