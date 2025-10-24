import { RocketLaunchIcon, SparklesIcon } from '@heroicons/react/24/outline'

export function Header() {
  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-2xl border-b border-gray-200/50 shadow-lg shadow-gray-200/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center space-x-3 group">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-primary-600 to-accent-500 rounded-xl blur-md opacity-50 group-hover:opacity-75 transition-opacity"></div>
              <div className="relative bg-gradient-to-r from-primary-600 to-accent-500 p-2 rounded-xl">
                <RocketLaunchIcon className="h-6 w-6 text-white" />
              </div>
            </div>
            <div>
              <h1 className="text-xl font-bold gradient-text-ai">ProjectPilot</h1>
              <div className="flex items-center space-x-1">
                <SparklesIcon className="h-3 w-3 text-primary-500" />
                <p className="text-xs font-medium text-gray-600">AI Project Analysis</p>
              </div>
            </div>
          </div>

          <nav className="hidden md:flex items-center space-x-6">
            <a href="#" className="text-gray-600 hover:text-primary-600 font-medium text-sm transition-colors">
              How it Works
            </a>
            <a href="#" className="text-gray-600 hover:text-primary-600 font-medium text-sm transition-colors">
              Examples
            </a>
            <a href="#" className="text-gray-600 hover:text-primary-600 font-medium text-sm transition-colors">
              Pricing
            </a>
            <button className="btn-primary text-sm">
              Get Started
            </button>
          </nav>
        </div>
      </div>
    </header>
  )
}