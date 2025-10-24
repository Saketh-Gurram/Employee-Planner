import { useState } from 'react'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import axios from 'axios'
import { RocketLaunchIcon, DocumentTextIcon, ClockIcon } from '@heroicons/react/24/outline'
import { AnalysisForm } from '../components/AnalysisForm'
import { AnalysisResults } from '../components/AnalysisResults'
import { Header } from '../components/Header'

interface ProjectInput {
  description: string
  company_size?: string
  budget_range?: string
  timeline_preference?: string
  industry?: string
}

interface AnalysisResponse {
  analysis_id: string
  status: string
  message: string
}

export default function Home() {
  const [analysisId, setAnalysisId] = useState<string | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const handleAnalysis = async (data: ProjectInput) => {
    setIsAnalyzing(true)

    try {
      const response = await axios.post<AnalysisResponse>(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/analyze`,
        data
      )

      if (response.data.analysis_id) {
        setAnalysisId(response.data.analysis_id)
        toast.success('Analysis started! Please wait while our AI agents work on your project.')
      }
    } catch (error) {
      console.error('Analysis failed:', error)
      toast.error('Failed to start analysis. Please try again.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleNewAnalysis = () => {
    setAnalysisId(null)
  }

  return (
    <div className="min-h-screen relative">
      {/* Animated mesh gradient background */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-100 via-blue-50 to-cyan-100"></div>
        <div className="absolute top-0 left-0 w-full h-full opacity-30">
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-300 rounded-full mix-blend-multiply filter blur-3xl animate-blob"></div>
          <div className="absolute top-0 right-1/4 w-96 h-96 bg-cyan-300 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000"></div>
          <div className="absolute bottom-0 left-1/3 w-96 h-96 bg-blue-300 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-4000"></div>
        </div>
      </div>
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        {!analysisId ? (
          <>
            {/* Hero Section */}
            <div className="text-center mb-16">
              <div className="flex justify-center mb-8">
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-r from-primary-600 via-accent-500 to-secondary-600 rounded-full blur-2xl opacity-30 animate-pulse"></div>
                  <div className="relative bg-gradient-to-r from-primary-600 via-accent-500 to-secondary-600 p-5 rounded-3xl shadow-2xl transform hover:scale-105 transition-transform duration-300">
                    <RocketLaunchIcon className="h-16 w-16 text-white" />
                  </div>
                </div>
              </div>
              <h1 className="text-5xl md:text-6xl font-bold mb-6">
                <span className="gradient-text-ai">ProjectPilot</span>
              </h1>
              <p className="text-xl md:text-2xl text-gray-600 max-w-3xl mx-auto mb-4 leading-relaxed">
                AI-driven project scoping and feasibility analysis
              </p>
              <p className="text-base text-gray-500 max-w-2xl mx-auto mb-8">
                Get comprehensive technical recommendations, cost estimates, and timeline projections in minutes.
              </p>

              {/* Features */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto mb-16">
                <div className="feature-card text-center group">
                  <div className="relative inline-block mb-4">
                    <div className="absolute inset-0 bg-gradient-to-r from-primary-500 to-accent-500 rounded-2xl blur-lg opacity-0 group-hover:opacity-50 transition-opacity"></div>
                    <div className="relative bg-gradient-to-br from-primary-50 to-accent-50 p-4 rounded-2xl">
                      <DocumentTextIcon className="h-8 w-8 text-primary-600 mx-auto" />
                    </div>
                  </div>
                  <h3 className="font-bold text-lg text-gray-900 mb-2">Technical Analysis</h3>
                  <p className="text-sm text-gray-600 leading-relaxed">
                    Get AI-powered tech stack recommendations and architecture designs
                  </p>
                </div>
                <div className="feature-card text-center group">
                  <div className="relative inline-block mb-4">
                    <div className="absolute inset-0 bg-gradient-to-r from-accent-500 to-secondary-500 rounded-2xl blur-lg opacity-0 group-hover:opacity-50 transition-opacity"></div>
                    <div className="relative bg-gradient-to-br from-accent-50 to-secondary-50 p-4 rounded-2xl">
                      <ClockIcon className="h-8 w-8 text-accent-600 mx-auto" />
                    </div>
                  </div>
                  <h3 className="font-bold text-lg text-gray-900 mb-2">Timeline & Cost</h3>
                  <p className="text-sm text-gray-600 leading-relaxed">
                    Accurate project timelines and budget estimates with confidence intervals
                  </p>
                </div>
                <div className="feature-card text-center group">
                  <div className="relative inline-block mb-4">
                    <div className="absolute inset-0 bg-gradient-to-r from-secondary-500 to-primary-500 rounded-2xl blur-lg opacity-0 group-hover:opacity-50 transition-opacity"></div>
                    <div className="relative bg-gradient-to-br from-secondary-50 to-primary-50 p-4 rounded-2xl">
                      <RocketLaunchIcon className="h-8 w-8 text-secondary-600 mx-auto" />
                    </div>
                  </div>
                  <h3 className="font-bold text-lg text-gray-900 mb-2">Team Planning</h3>
                  <p className="text-sm text-gray-600 leading-relaxed">
                    Optimal team composition and resource allocation strategies
                  </p>
                </div>
              </div>
            </div>

            {/* Analysis Form */}
            <AnalysisForm onSubmit={handleAnalysis} isLoading={isAnalyzing} />
          </>
        ) : (
          <AnalysisResults
            analysisId={analysisId}
            onNewAnalysis={handleNewAnalysis}
          />
        )}
      </main>
    </div>
  )
}