'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  Home, 
  Workflow,
  Info,
  Video,
  Network,
  Eye,
  History,
  Camera,
  Database,
  Play
} from 'lucide-react'

const navigation = [
  { name: 'Dashboard', href: '/dashboard/pipeline', icon: Home },
  { name: 'Pipeline', href: '/dashboard/pipeline', icon: Workflow },
  // { name: 'Parallel Demo', href: '/dashboard/demo/parallel-execution', icon: Play },
]

const debugNavigation = [
  { name: 'Artifacts', href: '/dashboard/artifacts', icon: Database },
  { name: 'Execution History', href: '/dashboard/history', icon: History },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="w-64 bg-primary text-white flex flex-col">
      <div className="p-4 border-b border-primary-dark">
        <h1 className="text-xl font-bold">SDET-GENIE</h1>
        <p className="text-sm text-blue-200">AI QA Automation</p>
      </div>
      
      <nav className="flex-1 p-4">
        <div className="space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon
            const isActive = pathname === item.href
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                  isActive 
                    ? 'bg-primary-dark text-white' 
                    : 'text-blue-100 hover:bg-primary-dark hover:text-white'
                }`}
              >
                <Icon className="mr-3 h-5 w-5" />
                {item.name}
              </Link>
            )
          })}
        </div>
        
        <div className="mt-8">
          <h3 className="px-3 text-xs font-semibold text-blue-200 uppercase tracking-wider">
            Debug & Analysis
          </h3>
          <div className="mt-1 space-y-1">
            {debugNavigation.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                    isActive 
                      ? 'bg-primary-dark text-white' 
                      : 'text-blue-100 hover:bg-primary-dark hover:text-white'
                  }`}
                >
                  <Icon className="mr-3 h-5 w-5" />
                  {item.name}
                </Link>
              )
            })}
          </div>
        </div>
      </nav>
      
      <div className="p-4 border-t border-primary-dark">
        <Link 
          href="/about" 
          className="flex items-center text-blue-200 hover:text-white"
        >
          <Info className="mr-3 h-5 w-5" />
          About WaiGenie
        </Link>
      </div>
    </div>
  )
}