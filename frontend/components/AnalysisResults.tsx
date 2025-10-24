import { useState, useEffect } from 'react'
import axios from 'axios'
import toast from 'react-hot-toast'
import {
  DocumentArrowDownIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  Squares2X2Icon,
  TableCellsIcon,
  FunnelIcon,
  ArrowsUpDownIcon
} from '@heroicons/react/24/outline'

interface AnalysisData {
  analysis_id: string
  status: string
  created_at: string
  completed_at?: string

  // Raw agent outputs
  intake_analysis?: any
  technical_analysis?: any
  estimation_analysis?: any
  summary_analysis?: any

  // Legacy flat fields
  executive_summary?: string
  tech_stack?: any
  team_composition?: any[]
  timeline_breakdown?: any
  cost_estimate?: any
  risks_and_dependencies?: any[]
}

interface AnalysisResultsProps {
  analysisId: string
  onNewAnalysis: () => void
}

interface CollapsibleSectionProps {
  title: string
  badge?: string
  badgeColor?: string
  children: React.ReactNode
  defaultOpen?: boolean
}

function CollapsibleSection({ title, badge, badgeColor, children, defaultOpen = false }: CollapsibleSectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen)

  return (
    <div className="card mb-6 hover:shadow-2xl">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex justify-between items-center text-left focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-lg"
      >
        <div className="flex items-center space-x-3">
          <h3 className="text-xl font-bold text-gray-900">{title}</h3>
          {badge && (
            <span className={`px-3 py-1 text-xs font-medium rounded-full ${badgeColor || 'bg-blue-100 text-blue-800'}`}>
              {badge}
            </span>
          )}
        </div>
        {isOpen ? (
          <ChevronUpIcon className="h-5 w-5 text-gray-500" />
        ) : (
          <ChevronDownIcon className="h-5 w-5 text-gray-500" />
        )}
      </button>

      {isOpen && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          {children}
        </div>
      )}
    </div>
  )
}

export function AnalysisResults({ analysisId, onNewAnalysis }: AnalysisResultsProps) {
  const [analysis, setAnalysis] = useState<AnalysisData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isPolling, setIsPolling] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')

  // Employee filtering and sorting state
  const [employeeViewMode, setEmployeeViewMode] = useState<'cards' | 'table'>('cards')
  const [filterMinMatch, setFilterMinMatch] = useState(0)
  const [filterMaxRate, setFilterMaxRate] = useState(999999)
  const [filterMinAvailability, setFilterMinAvailability] = useState(0)
  const [sortBy, setSortBy] = useState<'match' | 'rate' | 'availability' | 'name'>('match')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')
  const [showFilters, setShowFilters] = useState(false)

  useEffect(() => {
    fetchAnalysis()

    const interval = setInterval(() => {
      if (isPolling) {
        fetchAnalysis()
      }
    }, 3000)

    return () => clearInterval(interval)
  }, [analysisId, isPolling])

  const fetchAnalysis = async () => {
    try {
      const response = await axios.get<AnalysisData>(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/analysis/${analysisId}`
      )

      setAnalysis(response.data)

      if (response.data.status === 'completed' || response.data.status === 'failed') {
        setIsPolling(false)
      }

      if (response.data.status === 'completed') {
        toast.success('Analysis completed!')
      } else if (response.data.status === 'failed') {
        toast.error('Analysis failed. Please try again.')
      }
    } catch (error) {
      console.error('Failed to fetch analysis:', error)
      toast.error('Failed to fetch analysis results')
    } finally {
      setIsLoading(false)
    }
  }

  const downloadReport = async (format: 'pdf' | 'markdown') => {
    try {
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/analysis/${analysisId}/report/${format}`,
        { responseType: 'blob' }
      )

      const blob = new Blob([response.data])
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `project_report_${analysisId}.${format}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      toast.success(`${format.toUpperCase()} report downloaded!`)
    } catch (error) {
      console.error('Failed to download report:', error)
      toast.error('Failed to download report')
    }
  }

  // Helper function to get all unique employees across all roles
  const getAllEmployees = () => {
    const estimation = analysis?.estimation_analysis || {}
    const teamComposition = estimation.team_composition || []
    const allEmployees: any[] = []
    const seenIds = new Set<string>()

    teamComposition.forEach((member: any) => {
      if (member.recommended_employees) {
        member.recommended_employees.forEach((emp: any) => {
          const empId = emp.employee_id || emp.name
          if (!seenIds.has(empId)) {
            seenIds.add(empId)
            allEmployees.push({
              ...emp,
              role: member.role // Add role context
            })
          }
        })
      }
    })

    return allEmployees
  }

  // Helper function to filter and sort employees
  const filterAndSortEmployees = (employees: any[]) => {
    let filtered = employees.filter((emp: any) => {
      const matchPct = emp.match_percentage || 0
      const rate = emp.hourly_rate || 0
      const availability = parseInt(emp.availability) || 0

      return (
        matchPct >= filterMinMatch &&
        rate <= filterMaxRate &&
        availability >= filterMinAvailability
      )
    })

    // Sort employees
    filtered.sort((a: any, b: any) => {
      let compareValue = 0

      switch (sortBy) {
        case 'match':
          compareValue = (b.match_percentage || 0) - (a.match_percentage || 0)
          break
        case 'rate':
          compareValue = (a.hourly_rate || 0) - (b.hourly_rate || 0)
          break
        case 'availability':
          compareValue = parseInt(b.availability || '0') - parseInt(a.availability || '0')
          break
        case 'name':
          compareValue = (a.name || '').localeCompare(b.name || '')
          break
      }

      return sortOrder === 'asc' ? -compareValue : compareValue
    })

    return filtered
  }

  // Get tech stack for employee matching summary
  const getTechStack = () => {
    const technical = analysis?.technical_analysis || {}
    const techStack = technical.recommended_tech_stack || {}
    const technologies: string[] = []

    Object.entries(techStack).forEach(([category, details]: [string, any]) => {
      if (details?.primary) technologies.push(details.primary)
      if (details?.ui_framework) technologies.push(details.ui_framework)
      if (details?.state_management) technologies.push(details.state_management)
    })

    return technologies
  }

  if (isLoading && !analysis) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <span className="ml-2 text-gray-600">Loading analysis...</span>
      </div>
    )
  }

  const summary = analysis?.summary_analysis || {}
  const intake = analysis?.intake_analysis || {}
  const technical = analysis?.technical_analysis || {}
  const estimation = analysis?.estimation_analysis || {}

  return (
    <div className="max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="card-gradient mb-8 sticky top-20 z-10 shadow-2xl">
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              📊 Project Analysis Results
            </h2>
            <p className="text-sm text-gray-600">Analysis ID: {analysisId}</p>
            <p className="text-sm text-gray-500">Created: {new Date(analysis?.created_at || '').toLocaleString()}</p>
          </div>

          <div className="flex items-center space-x-3">
            {/* Status Badge */}
            <div className={`flex items-center space-x-2 px-4 py-2 rounded-full text-sm font-medium ${
              analysis?.status === 'completed'
                ? 'bg-success-100 text-success-800'
                : analysis?.status === 'failed'
                ? 'bg-error-100 text-error-800'
                : 'bg-warning-100 text-warning-800'
            }`}>
              {analysis?.status === 'completed' && <CheckCircleIcon className="h-5 w-5" />}
              {analysis?.status === 'failed' && <ExclamationTriangleIcon className="h-5 w-5" />}
              {analysis?.status === 'processing' && <ClockIcon className="h-5 w-5 animate-pulse" />}
              <span className="capitalize">{analysis?.status}</span>
            </div>

            <button
              onClick={onNewAnalysis}
              className="btn-secondary flex items-center space-x-2"
            >
              <ArrowPathIcon className="h-4 w-4" />
              <span>New Analysis</span>
            </button>
          </div>
        </div>

        {analysis?.status === 'processing' && (
          <div className="mt-6 p-6 bg-gradient-to-r from-info-50 to-primary-50 rounded-2xl border-2 border-info-200 shadow-lg">
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-info-600"></div>
              <span className="text-info-800 font-medium">
                🤖 Our AI agents are analyzing your project...
              </span>
            </div>
            <p className="text-info-600 text-sm mt-1">
              This typically takes 2-5 minutes. The page will update automatically.
            </p>
          </div>
        )}
      </div>

      {/* Results */}
      {analysis?.status === 'completed' && (
        <>
          {/* Download Options */}
          <div className="card mb-8 bg-gradient-to-br from-primary-50 via-white to-accent-50 border-2 border-primary-200 shadow-xl">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              📥 Download Complete Report
            </h3>
            <div className="flex space-x-4">
              <button
                onClick={() => downloadReport('pdf')}
                className="btn-primary flex items-center space-x-2"
              >
                <DocumentArrowDownIcon className="h-5 w-5" />
                <span>Download PDF</span>
              </button>
              <button
                onClick={() => downloadReport('markdown')}
                className="btn-secondary flex items-center space-x-2"
              >
                <DocumentArrowDownIcon className="h-5 w-5" />
                <span>Download Markdown</span>
              </button>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="mb-8">
            <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-2 shadow-lg border-2 border-gray-200 inline-flex gap-2">
              <button
                onClick={() => setActiveTab('overview')}
                className={`px-6 py-3 rounded-2xl font-semibold transition-all duration-300 ${
                  activeTab === 'overview'
                    ? 'bg-gradient-to-r from-primary-600 to-accent-600 text-white shadow-lg shadow-primary-500/50'
                    : 'text-gray-600 hover:text-primary-600 hover:bg-gray-50'
                }`}
              >
                📊 Overview
              </button>
              <button
                onClick={() => setActiveTab('technical')}
                className={`px-6 py-3 rounded-2xl font-semibold transition-all duration-300 ${
                  activeTab === 'technical'
                    ? 'bg-gradient-to-r from-primary-600 to-accent-600 text-white shadow-lg shadow-primary-500/50'
                    : 'text-gray-600 hover:text-primary-600 hover:bg-gray-50'
                }`}
              >
                💻 Technical
              </button>
              <button
                onClick={() => setActiveTab('team')}
                className={`px-6 py-3 rounded-2xl font-semibold transition-all duration-300 ${
                  activeTab === 'team'
                    ? 'bg-gradient-to-r from-primary-600 to-accent-600 text-white shadow-lg shadow-primary-500/50'
                    : 'text-gray-600 hover:text-primary-600 hover:bg-gray-50'
                }`}
              >
                👥 Team & Budget
              </button>
              <button
                onClick={() => setActiveTab('risks')}
                className={`px-6 py-3 rounded-2xl font-semibold transition-all duration-300 ${
                  activeTab === 'risks'
                    ? 'bg-gradient-to-r from-primary-600 to-accent-600 text-white shadow-lg shadow-primary-500/50'
                    : 'text-gray-600 hover:text-primary-600 hover:bg-gray-50'
                }`}
              >
                ⚠️ Risks
              </button>
              <button
                onClick={() => setActiveTab('recommendations')}
                className={`px-6 py-3 rounded-2xl font-semibold transition-all duration-300 ${
                  activeTab === 'recommendations'
                    ? 'bg-gradient-to-r from-primary-600 to-accent-600 text-white shadow-lg shadow-primary-500/50'
                    : 'text-gray-600 hover:text-primary-600 hover:bg-gray-50'
                }`}
              >
                💡 Recommendations
              </button>
            </div>
          </div>

          {/* OVERVIEW TAB CONTENT */}
          {activeTab === 'overview' && (
            <>
              {/* Executive Summary */}
              {summary.executive_summary && (
                <CollapsibleSection
                  title="📋 Executive Summary"
                  badge="Key Insights"
                  badgeColor="bg-purple-100 text-purple-800"
                  defaultOpen={true}
                >
              <div className="space-y-6">
                {summary.executive_summary.project_overview && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-500 uppercase mb-2">Project Overview</h4>
                    <p className="text-gray-800 leading-relaxed text-lg">{summary.executive_summary.project_overview}</p>
                  </div>
                )}

                {summary.executive_summary.go_no_go_recommendation && (
                  <div className="bg-gradient-to-r from-success-50 to-success-100 p-6 rounded-2xl border-l-4 border-success-600 shadow-md">
                    <h4 className="text-sm font-semibold text-success-800 uppercase mb-2">Recommendation</h4>
                    <p className="text-success-900 font-medium">{summary.executive_summary.go_no_go_recommendation}</p>
                  </div>
                )}

                {summary.executive_summary.key_findings && Array.isArray(summary.executive_summary.key_findings) && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-500 uppercase mb-3">Key Findings</h4>
                    <ul className="space-y-3">
                      {summary.executive_summary.key_findings.map((finding: string, idx: number) => (
                        <li key={idx} className="flex items-start space-x-3 p-4 bg-white rounded-2xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
                          <span className="text-primary-600 font-bold">•</span>
                          <span className="text-gray-700">{finding}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {summary.executive_summary.recommended_approach && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-500 uppercase mb-2">Recommended Approach</h4>
                    <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">{summary.executive_summary.recommended_approach}</p>
                  </div>
                )}

                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {summary.executive_summary.success_probability && (
                    <div className="bg-white p-5 rounded-2xl border-2 border-gray-200 shadow-lg hover:shadow-xl hover:border-primary-300 transition-all">
                      <p className="text-xs text-gray-500 uppercase font-semibold">Success Probability</p>
                      <p className="text-xl font-bold text-gray-900 mt-1">{summary.executive_summary.success_probability}</p>
                    </div>
                  )}
                  {summary.executive_summary.strategic_value && (
                    <div className="bg-white p-5 rounded-2xl border-2 border-gray-200 shadow-lg hover:shadow-xl hover:border-primary-300 transition-all">
                      <p className="text-xs text-gray-500 uppercase font-semibold">Strategic Value</p>
                      <p className="text-sm text-gray-700 mt-1">{summary.executive_summary.strategic_value}</p>
                    </div>
                  )}
                </div>
              </div>
            </CollapsibleSection>
          )}

          {/* Project Highlights */}
          {summary.project_highlights && (
            <CollapsibleSection
              title="⭐ Project Highlights"
              badge="Quick Stats"
              badgeColor="bg-yellow-100 text-yellow-800"
              defaultOpen={true}
            >
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {summary.project_highlights.estimated_cost && (
                  <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-6 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 border border-green-200">
                    <p className="text-xs text-gray-600 uppercase font-semibold">Estimated Cost</p>
                    <p className="text-2xl font-bold text-green-700 mt-2">{summary.project_highlights.estimated_cost}</p>
                  </div>
                )}
                {summary.project_highlights.estimated_timeline && (
                  <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-6 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 border border-blue-200">
                    <p className="text-xs text-gray-600 uppercase font-semibold">Timeline</p>
                    <p className="text-2xl font-bold text-blue-700 mt-2">{summary.project_highlights.estimated_timeline}</p>
                  </div>
                )}
                {summary.project_highlights.team_size && (
                  <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-6 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 border border-purple-200">
                    <p className="text-xs text-gray-600 uppercase font-semibold">Team Size</p>
                    <p className="text-2xl font-bold text-purple-700 mt-2">{summary.project_highlights.team_size}</p>
                  </div>
                )}
                {summary.project_highlights.complexity_level && (
                  <div className="bg-gradient-to-br from-orange-50 to-red-50 p-6 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 border border-orange-200">
                    <p className="text-xs text-gray-600 uppercase font-semibold">Complexity</p>
                    <p className="text-2xl font-bold text-orange-700 mt-2 capitalize">{summary.project_highlights.complexity_level.split(' ')[0]}</p>
                  </div>
                )}
              </div>

              {summary.project_highlights.primary_technology_stack && (
                <div className="mt-6">
                  <h4 className="text-sm font-semibold text-gray-500 uppercase mb-2">Technology Stack</h4>
                  <p className="text-gray-700">{summary.project_highlights.primary_technology_stack}</p>
                </div>
              )}

              {summary.project_highlights.main_business_benefits && Array.isArray(summary.project_highlights.main_business_benefits) && (
                <div className="mt-6">
                  <h4 className="text-sm font-semibold text-gray-500 uppercase mb-3">Main Business Benefits</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {summary.project_highlights.main_business_benefits.map((benefit: string, idx: number) => (
                      <div key={idx} className="flex items-start space-x-2 p-3 bg-white rounded-lg border border-gray-200">
                        <span className="text-green-500 text-xl">✓</span>
                        <span className="text-gray-700 text-sm">{benefit}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CollapsibleSection>
          )}

              {/* Project Intake Details */}
              {intake.project_summary && (
                <CollapsibleSection title="🎯 Project Understanding" badge="Intake Analysis">
              <div className="space-y-6">
                <div>
                  <h4 className="text-sm font-semibold text-gray-500 uppercase mb-2">Project Summary</h4>
                  <p className="text-gray-700 leading-relaxed">{intake.project_summary}</p>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {intake.project_type && (
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <p className="text-xs text-gray-600 uppercase font-semibold">Project Type</p>
                      <p className="text-sm font-medium text-blue-900 mt-1 capitalize">{intake.project_type.replace('_', ' ')}</p>
                    </div>
                  )}
                  {intake.domain && (
                    <div className="bg-purple-50 p-4 rounded-lg">
                      <p className="text-xs text-gray-600 uppercase font-semibold">Domain</p>
                      <p className="text-sm font-medium text-purple-900 mt-1 capitalize">{intake.domain}</p>
                    </div>
                  )}
                </div>

                {intake.core_features && Array.isArray(intake.core_features) && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-500 uppercase mb-3">Core Features</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {intake.core_features.map((feature: string, idx: number) => (
                        <div key={idx} className="flex items-start space-x-2 p-3 bg-indigo-50 rounded-lg">
                          <span className="text-indigo-600 font-bold">→</span>
                          <span className="text-gray-800 text-sm">{feature}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {intake.target_users && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-500 uppercase mb-2">Target Users</h4>
                    <p className="text-gray-700">{intake.target_users}</p>
                  </div>
                )}

                {intake.user_personas && Array.isArray(intake.user_personas) && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-500 uppercase mb-3">User Personas</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {intake.user_personas.map((persona: any, idx: number) => (
                        <div key={idx} className="bg-gradient-to-br from-purple-50 to-pink-50 p-4 rounded-lg border-l-4 border-purple-500">
                          <h5 className="font-bold text-gray-900 mb-2">{persona.persona_name}</h5>
                          <p className="text-sm text-gray-700 mb-2">{persona.description}</p>
                          {persona.needs && (
                            <div className="text-xs text-gray-600">
                              <strong>Needs:</strong> {persona.needs.join(', ')}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {intake.business_value && (
                  <div className="bg-yellow-50 p-5 rounded-lg border-l-4 border-yellow-500">
                    <h4 className="text-sm font-semibold text-yellow-900 uppercase mb-3">Business Value</h4>
                    {intake.business_value.problem_being_solved && (
                      <p className="text-gray-800 mb-2"><strong>Problem:</strong> {intake.business_value.problem_being_solved}</p>
                    )}
                    {intake.business_value.market_opportunity && (
                      <p className="text-gray-800 mb-2"><strong>Market Opportunity:</strong> {intake.business_value.market_opportunity}</p>
                    )}
                    {intake.business_value.competitive_advantages && Array.isArray(intake.business_value.competitive_advantages) && (
                      <div className="mt-2">
                        <strong className="text-gray-800">Competitive Advantages:</strong>
                        <ul className="list-disc list-inside ml-2 text-gray-700">
                          {intake.business_value.competitive_advantages.map((adv: string, idx: number) => (
                            <li key={idx}>{adv}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                {intake.questions_for_clarification && Array.isArray(intake.questions_for_clarification) && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-500 uppercase mb-3">Questions for Clarification</h4>
                    <ul className="space-y-2">
                      {intake.questions_for_clarification.map((question: string, idx: number) => (
                        <li key={idx} className="flex items-start space-x-2 p-3 bg-amber-50 rounded-lg border-l-4 border-amber-400">
                          <span className="text-amber-600 font-bold">?</span>
                          <span className="text-gray-800 text-sm">{question}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
                </CollapsibleSection>
              )}
            </>
          )}

          {/* TECHNICAL TAB CONTENT */}
          {activeTab === 'technical' && (
            <>
              {/* Technical Analysis */}
              {technical.recommended_tech_stack && (
              <div className="card mb-6">
                <h3 className="text-2xl font-bold text-gray-900 mb-2 flex items-center gap-3">
                  <span>💻 Technical Architecture</span>
                  <span className="px-3 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                    Technology Recommendations
                  </span>
                </h3>
              <div className="space-y-6 mt-6">
                {/* Tech Stack */}
                <div>
                  <h4 className="text-sm font-semibold text-gray-500 uppercase mb-4">Recommended Technology Stack</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {Object.entries(technical.recommended_tech_stack).map(([category, details]: [string, any]) => (
                      <div key={category} className="bg-gradient-to-br from-blue-50 to-indigo-50 p-5 rounded-xl border-2 border-blue-200">
                        <h5 className="font-bold text-indigo-900 capitalize mb-3">
                          {category.replace('_', ' ')}
                        </h5>
                        {details.primary && (
                          <p className="text-sm mb-2">
                            <strong className="text-gray-700">Choice:</strong> <span className="text-indigo-700 font-semibold">{details.primary}</span>
                          </p>
                        )}
                        {details.reasoning && (
                          <p className="text-xs text-gray-600 mt-2">{details.reasoning}</p>
                        )}
                        {details.ui_framework && (
                          <p className="text-xs text-gray-700 mt-2"><strong>UI:</strong> {details.ui_framework}</p>
                        )}
                        {details.state_management && (
                          <p className="text-xs text-gray-700 mt-1"><strong>State:</strong> {details.state_management}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Architecture Overview */}
                {technical.architecture_overview && (
                  <div className="bg-white p-6 rounded-lg border-2 border-gray-200">
                    <h4 className="text-sm font-semibold text-gray-500 uppercase mb-4">Architecture Overview</h4>
                    {technical.architecture_overview.pattern && (
                      <p className="mb-3"><strong className="text-gray-700">Pattern:</strong> <span className="text-gray-800 capitalize">{technical.architecture_overview.pattern}</span></p>
                    )}
                    {technical.architecture_overview.data_flow && (
                      <p className="mb-3 text-gray-700"><strong>Data Flow:</strong> {technical.architecture_overview.data_flow}</p>
                    )}
                    {technical.architecture_overview.scalability_approach && (
                      <p className="mb-3 text-gray-700"><strong>Scalability:</strong> {technical.architecture_overview.scalability_approach}</p>
                    )}
                    {technical.architecture_overview.security_architecture && (
                      <p className="text-gray-700"><strong>Security:</strong> {technical.architecture_overview.security_architecture}</p>
                    )}
                  </div>
                )}

                {/* Integration Requirements */}
                {technical.integration_requirements && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-500 uppercase mb-3">Integration Requirements</h4>
                    <div className="space-y-3">
                      {technical.integration_requirements.third_party_apis && Array.isArray(technical.integration_requirements.third_party_apis) && (
                        <div className="bg-purple-50 p-4 rounded-lg">
                          <h5 className="font-semibold text-purple-900 mb-2">Third-Party APIs</h5>
                          <ul className="space-y-1 text-sm text-gray-700">
                            {technical.integration_requirements.third_party_apis.map((api: string, idx: number) => (
                              <li key={idx}>• {api}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {technical.integration_requirements.authentication_providers && Array.isArray(technical.integration_requirements.authentication_providers) && (
                        <div className="bg-green-50 p-4 rounded-lg">
                          <h5 className="font-semibold text-green-900 mb-2">Authentication Providers</h5>
                          <ul className="space-y-1 text-sm text-gray-700">
                            {technical.integration_requirements.authentication_providers.map((provider: string, idx: number) => (
                              <li key={idx}>• {provider}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Technical Challenges */}
                {technical.technical_complexity?.technical_challenges && Array.isArray(technical.technical_complexity.technical_challenges) && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-500 uppercase mb-3">Technical Challenges</h4>
                    <div className="space-y-2">
                      {technical.technical_complexity.technical_challenges.map((challenge: string, idx: number) => (
                        <div key={idx} className="bg-red-50 p-3 rounded-lg border-l-4 border-red-400">
                          <p className="text-sm text-gray-800">{challenge}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              </div>
              )}
            </>
          )}

          {/* TEAM & BUDGET TAB CONTENT */}
          {activeTab === 'team' && (
            <>
              {/* Estimation & Cost */}
              {estimation.team_composition && (
              <div className="card mb-6">
                <h3 className="text-2xl font-bold text-gray-900 mb-2 flex items-center gap-3">
                  <span>👥 Team & Budget</span>
                  <span className="px-3 py-1 text-xs font-medium rounded-full bg-purple-100 text-purple-800">
                    Resource Planning
                  </span>
                </h3>
              <div className="space-y-6 mt-6">
                {/* Employee Talent Pool Summary */}
                {getAllEmployees().length > 0 && (
                  <div className="bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6 rounded-2xl border-2 border-indigo-300 shadow-xl">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h4 className="text-lg font-bold text-indigo-900 mb-1">
                          🎯 Available Talent Pool
                        </h4>
                        <p className="text-sm text-indigo-700">
                          {getAllEmployees().length} matching employees found for your tech stack
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => setShowFilters(!showFilters)}
                          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                            showFilters
                              ? 'bg-indigo-600 text-white shadow-lg'
                              : 'bg-white text-indigo-700 hover:bg-indigo-100'
                          }`}
                        >
                          <FunnelIcon className="h-4 w-4" />
                          Filters
                        </button>
                        <button
                          onClick={() => setEmployeeViewMode(employeeViewMode === 'cards' ? 'table' : 'cards')}
                          className="flex items-center gap-2 px-4 py-2 bg-white text-indigo-700 rounded-lg text-sm font-semibold hover:bg-indigo-100 transition-all"
                        >
                          {employeeViewMode === 'cards' ? (
                            <>
                              <TableCellsIcon className="h-4 w-4" />
                              Table
                            </>
                          ) : (
                            <>
                              <Squares2X2Icon className="h-4 w-4" />
                              Cards
                            </>
                          )}
                        </button>
                      </div>
                    </div>

                    {/* Tech Stack Tags */}
                    <div className="mb-4">
                      <p className="text-xs font-semibold text-indigo-800 uppercase mb-2">Required Tech Stack:</p>
                      <div className="flex flex-wrap gap-2">
                        {getTechStack().slice(0, 8).map((tech: string, idx: number) => (
                          <span key={idx} className="px-3 py-1 bg-white text-indigo-800 rounded-full text-sm font-medium shadow-sm">
                            {tech}
                          </span>
                        ))}
                        {getTechStack().length > 8 && (
                          <span className="px-3 py-1 bg-indigo-200 text-indigo-900 rounded-full text-sm font-semibold">
                            +{getTechStack().length - 8} more
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Filters */}
                    {showFilters && (
                      <div className="bg-white p-5 rounded-xl border-2 border-indigo-200 mb-4 space-y-5">
                        {/* Match Percentage Pills */}
                        <div>
                          <label className="text-xs font-bold text-gray-700 uppercase mb-3 block tracking-wide">
                            🎯 Match Quality
                          </label>
                          <div className="flex flex-wrap gap-2">
                            {[
                              { label: 'All', value: 0 },
                              { label: '50%+ Good', value: 50 },
                              { label: '70%+ Great', value: 70 },
                              { label: '80%+ Excellent', value: 80 },
                              { label: '90%+ Perfect', value: 90 }
                            ].map((option) => (
                              <button
                                key={option.value}
                                onClick={() => setFilterMinMatch(option.value)}
                                className={`px-4 py-2 rounded-full text-sm font-semibold transition-all ${
                                  filterMinMatch === option.value
                                    ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-lg'
                                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                }`}
                              >
                                {option.label}
                              </button>
                            ))}
                          </div>
                        </div>

                        {/* Hourly Rate Pills */}
                        <div>
                          <label className="text-xs font-bold text-gray-700 uppercase mb-3 block tracking-wide">
                            💰 Max Rate
                          </label>
                          <div className="flex flex-wrap gap-2">
                            {[
                              { label: 'Any Rate', value: 999999 },
                              { label: '< $50/hr', value: 50 },
                              { label: '< $75/hr', value: 75 },
                              { label: '< $100/hr', value: 100 },
                              { label: '< $150/hr', value: 150 },
                              { label: '< $200/hr', value: 200 }
                            ].map((option) => (
                              <button
                                key={option.value}
                                onClick={() => setFilterMaxRate(option.value)}
                                className={`px-4 py-2 rounded-full text-sm font-semibold transition-all ${
                                  filterMaxRate === option.value
                                    ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white shadow-lg'
                                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                }`}
                              >
                                {option.label}
                              </button>
                            ))}
                          </div>
                        </div>

                        {/* Availability Pills */}
                        <div>
                          <label className="text-xs font-bold text-gray-700 uppercase mb-3 block tracking-wide">
                            ⏰ Min Availability
                          </label>
                          <div className="flex flex-wrap gap-2">
                            {[
                              { label: 'Any', value: 0 },
                              { label: '25%+', value: 25 },
                              { label: '50%+', value: 50 },
                              { label: '75%+', value: 75 },
                              { label: '100% Full', value: 100 }
                            ].map((option) => (
                              <button
                                key={option.value}
                                onClick={() => setFilterMinAvailability(option.value)}
                                className={`px-4 py-2 rounded-full text-sm font-semibold transition-all ${
                                  filterMinAvailability === option.value
                                    ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg'
                                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                }`}
                              >
                                {option.label}
                              </button>
                            ))}
                          </div>
                        </div>

                        {/* Sort Controls */}
                        <div className="pt-4 border-t-2 border-gray-200">
                          <label className="text-xs font-bold text-gray-700 uppercase mb-3 block tracking-wide">
                            📊 Sort By
                          </label>
                          <div className="flex items-center gap-3">
                            <div className="flex flex-wrap gap-2 flex-1">
                              {[
                                { label: 'Match %', value: 'match', icon: '🎯' },
                                { label: 'Rate', value: 'rate', icon: '💰' },
                                { label: 'Availability', value: 'availability', icon: '⏰' },
                                { label: 'Name', value: 'name', icon: '👤' }
                              ].map((option) => (
                                <button
                                  key={option.value}
                                  onClick={() => setSortBy(option.value as any)}
                                  className={`px-4 py-2 rounded-full text-sm font-semibold transition-all ${
                                    sortBy === option.value
                                      ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg'
                                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                  }`}
                                >
                                  {option.icon} {option.label}
                                </button>
                              ))}
                            </div>
                            <button
                              onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                              className={`px-4 py-2 rounded-full font-semibold transition-all ${
                                sortOrder === 'desc'
                                  ? 'bg-gradient-to-r from-orange-500 to-red-500 text-white shadow-lg'
                                  : 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white shadow-lg'
                              }`}
                            >
                              {sortOrder === 'desc' ? '↓ High to Low' : '↑ Low to High'}
                            </button>
                            <button
                              onClick={() => {
                                setFilterMinMatch(0)
                                setFilterMaxRate(999999)
                                setFilterMinAvailability(0)
                                setSortBy('match')
                                setSortOrder('desc')
                              }}
                              className="px-4 py-2 rounded-full bg-gray-200 text-gray-700 text-sm font-semibold hover:bg-gray-300 transition-all"
                            >
                              ✕ Reset All
                            </button>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Top Matching Employees Preview */}
                    <div className="bg-white p-5 rounded-xl border-2 border-indigo-200">
                      <h5 className="text-sm font-bold text-gray-900 mb-3 flex items-center gap-2">
                        <span className="text-2xl">⭐</span>
                        Top Matching Team Members
                      </h5>
                      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                        {filterAndSortEmployees(getAllEmployees()).slice(0, 8).map((emp: any, idx: number) => (
                          <div key={idx} className="bg-gradient-to-br from-green-50 to-emerald-50 p-3 rounded-lg border-2 border-green-200 hover:border-green-400 hover:shadow-lg transition-all duration-200">
                            <div className="flex items-start justify-between mb-2">
                              <div className="flex-1">
                                <p className="font-bold text-gray-900 text-sm truncate">{emp.name}</p>
                                <p className="text-xs text-gray-600 truncate">{emp.title}</p>
                              </div>
                              <span className={`px-2 py-0.5 rounded-full text-xs font-bold whitespace-nowrap ml-1 ${
                                emp.match_percentage >= 80 ? 'bg-green-500 text-white' :
                                emp.match_percentage >= 60 ? 'bg-yellow-500 text-white' :
                                'bg-gray-400 text-white'
                              }`}>
                                {emp.match_percentage}%
                              </span>
                            </div>
                            <div className="text-xs text-gray-700 space-y-0.5">
                              <p><strong>${emp.hourly_rate}/hr</strong></p>
                              <p>{emp.availability} available</p>
                            </div>
                          </div>
                        ))}
                      </div>
                      {filterAndSortEmployees(getAllEmployees()).length > 8 && (
                        <p className="text-center text-sm text-indigo-700 mt-3 font-semibold">
                          +{filterAndSortEmployees(getAllEmployees()).length - 8} more employees below
                        </p>
                      )}
                    </div>
                  </div>
                )}

                {/* Team Composition */}
                <div>
                  <h4 className="text-sm font-semibold text-gray-500 uppercase mb-4">Recommended Team Composition by Role</h4>
                  <div className="space-y-6">
                    {estimation.team_composition.map((member: any, index: number) => (
                      <div key={index} className="bg-white rounded-xl border-2 border-gray-200 overflow-hidden hover:border-primary-300 transition-all">
                        {/* Role Header */}
                        <div className="bg-gradient-to-r from-primary-50 to-accent-50 p-5 border-b-2 border-gray-200">
                          <div className="flex justify-between items-start">
                            <div>
                              <h5 className="text-lg font-bold text-gray-900 mb-1">{member.role}</h5>
                              <div className="flex gap-2 items-center flex-wrap">
                                <span className="px-3 py-1 text-xs font-semibold rounded-full bg-primary-100 text-primary-800">
                                  {member.seniority}
                                </span>
                                <span className="text-sm text-gray-600">{member.duration_weeks} weeks</span>
                                <span className="text-sm font-semibold text-primary-700">${member.hourly_rate}/hr</span>
                              </div>
                            </div>
                            <div className="text-right">
                              <p className="text-xs text-gray-500 uppercase font-semibold">Total Cost</p>
                              <p className="text-2xl font-bold text-primary-700">
                                ${member.total_cost?.toLocaleString() || 'N/A'}
                              </p>
                            </div>
                          </div>
                          {member.justification && (
                            <p className="text-sm text-gray-700 mt-3 italic">{member.justification}</p>
                          )}
                        </div>

                        {/* Recommended Employees */}
                        {member.recommended_employees && member.recommended_employees.length > 0 && (
                          <div className="p-5 bg-gradient-to-br from-gray-50 to-gray-100">
                            <div className="flex items-center justify-between mb-4">
                              <h6 className="text-sm font-semibold text-gray-700 uppercase flex items-center">
                                <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                  <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
                                </svg>
                                Recommended Team Members ({filterAndSortEmployees(member.recommended_employees).length})
                              </h6>
                            </div>

                            {/* Cards View */}
                            {employeeViewMode === 'cards' ? (
                              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                {filterAndSortEmployees(member.recommended_employees).map((emp: any, empIdx: number) => (
                                  <div key={empIdx} className="bg-white rounded-xl p-5 border-2 border-gray-200 hover:border-green-400 transition-all hover:shadow-xl">
                                    {/* Employee Header */}
                                    <div className="flex justify-between items-start mb-3">
                                      <div className="flex-1 pr-2">
                                        <h6 className="font-bold text-gray-900 text-base mb-1">{emp.name}</h6>
                                        <p className="text-xs text-gray-600 font-medium">{emp.title}</p>
                                      </div>
                                      <div className="text-right">
                                        <div className={`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-bold shadow-md ${
                                          emp.match_percentage >= 80 ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white' :
                                          emp.match_percentage >= 60 ? 'bg-gradient-to-r from-yellow-400 to-orange-400 text-white' :
                                          'bg-gradient-to-r from-gray-400 to-gray-500 text-white'
                                        }`}>
                                          {emp.match_percentage}%
                                        </div>
                                      </div>
                                    </div>

                                    {/* Employee Details */}
                                    <div className="space-y-2 mb-3">
                                      <div className="flex items-center justify-between p-2 bg-green-50 rounded-lg">
                                        <span className="text-xs font-semibold text-gray-700">Rate:</span>
                                        <span className="text-sm font-bold text-green-700">${emp.hourly_rate}/hr</span>
                                      </div>
                                      <div className="flex items-center justify-between p-2 bg-blue-50 rounded-lg">
                                        <span className="text-xs font-semibold text-gray-700">Availability:</span>
                                        <span className="text-sm font-bold text-blue-700">{emp.availability}</span>
                                      </div>
                                      {emp.location && (
                                        <div className="flex items-center justify-between p-2 bg-purple-50 rounded-lg">
                                          <span className="text-xs font-semibold text-gray-700">Location:</span>
                                          <span className="text-sm font-bold text-purple-700">{emp.location}</span>
                                        </div>
                                      )}
                                    </div>

                                    {/* Matching Skills */}
                                    {emp.matching_skills && emp.matching_skills.length > 0 && (
                                      <div className="pt-3 border-t-2 border-gray-200">
                                        <p className="text-xs font-bold text-gray-700 mb-2 uppercase tracking-wide">Matching Skills:</p>
                                        <div className="flex flex-wrap gap-1.5">
                                          {emp.matching_skills.slice(0, 5).map((skill: any, skillIdx: number) => (
                                            <span key={skillIdx} className="px-2.5 py-1 bg-gradient-to-r from-indigo-100 to-purple-100 text-indigo-800 rounded-lg text-xs font-bold border border-indigo-200">
                                              {skill.skill} <span className="text-indigo-600">({skill.proficiency}/5)</span>
                                            </span>
                                          ))}
                                          {emp.matching_skills.length > 5 && (
                                            <span className="px-2.5 py-1 bg-gray-200 text-gray-700 rounded-lg text-xs font-bold">
                                              +{emp.matching_skills.length - 5}
                                            </span>
                                          )}
                                        </div>
                                      </div>
                                    )}
                                  </div>
                                ))}
                              </div>
                            ) : (
                              /* Table View */
                              <div className="bg-white rounded-xl overflow-hidden border-2 border-gray-200 shadow-lg">
                                <table className="w-full">
                                  <thead className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
                                    <tr>
                                      <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide">Name</th>
                                      <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide">Title</th>
                                      <th className="px-4 py-3 text-center text-xs font-bold uppercase tracking-wide">Match</th>
                                      <th className="px-4 py-3 text-center text-xs font-bold uppercase tracking-wide">Rate</th>
                                      <th className="px-4 py-3 text-center text-xs font-bold uppercase tracking-wide">Availability</th>
                                      <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide">Top Skills</th>
                                    </tr>
                                  </thead>
                                  <tbody className="divide-y divide-gray-200">
                                    {filterAndSortEmployees(member.recommended_employees).map((emp: any, empIdx: number) => (
                                      <tr key={empIdx} className="hover:bg-indigo-50 transition-colors">
                                        <td className="px-4 py-3">
                                          <p className="font-bold text-gray-900 text-sm">{emp.name}</p>
                                          {emp.location && <p className="text-xs text-gray-500">{emp.location}</p>}
                                        </td>
                                        <td className="px-4 py-3 text-sm text-gray-700">{emp.title}</td>
                                        <td className="px-4 py-3 text-center">
                                          <span className={`inline-flex px-3 py-1 rounded-full text-xs font-bold ${
                                            emp.match_percentage >= 80 ? 'bg-green-100 text-green-800' :
                                            emp.match_percentage >= 60 ? 'bg-yellow-100 text-yellow-800' :
                                            'bg-gray-100 text-gray-800'
                                          }`}>
                                            {emp.match_percentage}%
                                          </span>
                                        </td>
                                        <td className="px-4 py-3 text-center">
                                          <span className="font-bold text-green-700 text-sm">${emp.hourly_rate}/hr</span>
                                        </td>
                                        <td className="px-4 py-3 text-center">
                                          <span className="font-semibold text-blue-700 text-sm">{emp.availability}</span>
                                        </td>
                                        <td className="px-4 py-3">
                                          <div className="flex flex-wrap gap-1">
                                            {emp.matching_skills?.slice(0, 3).map((skill: any, skillIdx: number) => (
                                              <span key={skillIdx} className="px-2 py-0.5 bg-indigo-100 text-indigo-800 rounded text-xs font-medium">
                                                {skill.skill}
                                              </span>
                                            ))}
                                            {emp.matching_skills?.length > 3 && (
                                              <span className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs">
                                                +{emp.matching_skills.length - 3}
                                              </span>
                                            )}
                                          </div>
                                        </td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </div>
                            )}

                            {/* Filtered Count Message */}
                            {filterAndSortEmployees(member.recommended_employees).length === 0 && member.recommended_employees.length > 0 && (
                              <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-4 text-center">
                                <p className="text-sm text-yellow-800 font-semibold">
                                  No employees match the current filters. Try adjusting your filter criteria above.
                                </p>
                              </div>
                            )}
                          </div>
                        )}

                        {/* No Employees Available Message */}
                        {(!member.recommended_employees || member.recommended_employees.length === 0) && (
                          <div className="p-5 bg-gray-50 text-center text-sm text-gray-500 italic">
                            No matching employees found. Consider external hiring or upskilling current team members.
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Cost Breakdown */}
                {estimation.cost_breakdown && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-500 uppercase mb-4">Cost Breakdown</h4>
                    <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-6 rounded-xl border-2 border-green-200">
                      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                        {Object.entries(estimation.cost_breakdown).map(([key, value]: [string, any]) => {
                          if (key === 'cost_range') return null
                          return (
                            <div key={key} className="bg-white p-4 rounded-lg">
                              <p className="text-xs text-gray-600 capitalize mb-1">
                                {key.replace('_', ' ')}
                              </p>
                              <p className={`font-semibold ${key === 'total_cost' ? 'text-2xl text-green-700' : 'text-lg text-gray-900'}`}>
                                {typeof value === 'number' ? `$${value.toLocaleString()}` : value}
                              </p>
                            </div>
                          )
                        })}
                      </div>
                      {estimation.cost_breakdown.cost_range && (
                        <div className="mt-4 pt-4 border-t border-green-200">
                          <p className="text-sm text-gray-700">
                            <strong>Cost Range:</strong> ${estimation.cost_breakdown.cost_range.minimum?.toLocaleString()} - ${estimation.cost_breakdown.cost_range.maximum?.toLocaleString()}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Timeline */}
                {estimation.timeline_breakdown && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-500 uppercase mb-4">Project Timeline</h4>
                    <div className="space-y-3">
                      {Object.entries(estimation.timeline_breakdown).map(([phase, details]: [string, any]) => {
                        if (phase === 'total_duration_weeks') return null
                        return (
                          <div key={phase} className="bg-white p-4 rounded-lg border-2 border-gray-200 hover:border-primary-300 transition-colors">
                            <div className="flex justify-between items-start mb-2">
                              <h5 className="font-semibold text-gray-900 capitalize">
                                {phase.replace(/_/g, ' ')}
                              </h5>
                              <span className="px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-xs font-semibold">
                                {details.duration_weeks || details} weeks
                              </span>
                            </div>
                            {details.activities && Array.isArray(details.activities) && (
                              <ul className="text-sm text-gray-600 space-y-1 mt-2">
                                {details.activities.map((activity: string, idx: number) => (
                                  <li key={idx} className="flex items-start space-x-2">
                                    <span className="text-primary-500">→</span>
                                    <span>{activity}</span>
                                  </li>
                                ))}
                              </ul>
                            )}
                          </div>
                        )
                      })}
                    </div>
                    {estimation.timeline_breakdown.total_duration_weeks && (
                      <div className="mt-4 bg-gradient-to-r from-indigo-50 to-purple-50 p-5 rounded-lg border-2 border-indigo-200 text-center">
                        <p className="text-sm text-gray-600 uppercase font-semibold">Total Duration</p>
                        <p className="text-3xl font-bold text-indigo-700 mt-2">{estimation.timeline_breakdown.total_duration_weeks} weeks</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Alternative Scenarios */}
                {estimation.alternative_scenarios && Array.isArray(estimation.alternative_scenarios) && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-500 uppercase mb-3">Alternative Scenarios</h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {estimation.alternative_scenarios.map((scenario: any, idx: number) => (
                        <div key={idx} className="bg-gradient-to-br from-yellow-50 to-amber-50 p-4 rounded-lg border-2 border-yellow-200">
                          <h5 className="font-bold text-yellow-900 mb-2">{scenario.scenario}</h5>
                          <p className="text-sm text-gray-700 mb-2">{scenario.changes}</p>
                          <div className="text-xs text-gray-600 space-y-1">
                            {scenario.impact_on_cost && <p><strong>Cost:</strong> {scenario.impact_on_cost}</p>}
                            {scenario.impact_on_timeline && <p><strong>Timeline:</strong> {scenario.impact_on_timeline}</p>}
                            {scenario.trade_offs && <p><strong>Trade-offs:</strong> {scenario.trade_offs}</p>}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              </div>
              )}
            </>
          )}

          {/* RECOMMENDATIONS TAB CONTENT */}
          {activeTab === 'recommendations' && (
            <>
              {/* Key Recommendations */}
              {summary.key_recommendations && Array.isArray(summary.key_recommendations) && (
              <div className="card mb-6">
                <h3 className="text-2xl font-bold text-gray-900 mb-2 flex items-center gap-3">
                  <span>💡 Key Recommendations</span>
                  <span className="px-3 py-1 text-xs font-medium rounded-full bg-indigo-100 text-indigo-800">
                    {summary.key_recommendations.length} Items
                  </span>
                </h3>
              <div className="space-y-3 mt-6">
                {summary.key_recommendations.map((rec: any, idx: number) => (
                  <div key={idx} className={`p-4 rounded-lg border-l-4 ${
                    rec.priority === 'critical' || rec.priority === 'high'
                      ? 'bg-red-50 border-red-500'
                      : rec.priority === 'medium'
                      ? 'bg-yellow-50 border-yellow-500'
                      : 'bg-green-50 border-green-500'
                  }`}>
                    <div className="flex justify-between items-start mb-2">
                      <h5 className="font-semibold text-gray-900">{rec.recommendation}</h5>
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                        rec.priority === 'critical' || rec.priority === 'high'
                          ? 'bg-red-200 text-red-800'
                          : rec.priority === 'medium'
                          ? 'bg-yellow-200 text-yellow-800'
                          : 'bg-green-200 text-green-800'
                      }`}>
                        {rec.priority} priority
                      </span>
                    </div>
                    {rec.rationale && <p className="text-sm text-gray-700 mb-2">{rec.rationale}</p>}
                    <div className="flex flex-wrap gap-2 text-xs text-gray-600">
                      {rec.category && <span className="bg-white px-2 py-1 rounded">📂 {rec.category}</span>}
                      {rec.estimated_effort && <span className="bg-white px-2 py-1 rounded">⏱ {rec.estimated_effort}</span>}
                      {rec.implementation_timeline && <span className="bg-white px-2 py-1 rounded">📅 {rec.implementation_timeline}</span>}
                    </div>
                  </div>
                ))}
              </div>
              </div>
              )}
            </>
          )}

          {/* RISKS TAB CONTENT */}
          {activeTab === 'risks' && (
            <>
              {/* Risks & Dependencies */}
              {(summary.major_risks || summary.dependencies) && (
              <div className="card mb-6">
                <h3 className="text-2xl font-bold text-gray-900 mb-2 flex items-center gap-3">
                  <span>⚠️ Risks & Dependencies</span>
                  <span className="px-3 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800">
                    Risk Assessment
                  </span>
                </h3>
              <div className="space-y-6 mt-6">
                {/* Major Risks */}
                {summary.major_risks && Array.isArray(summary.major_risks) && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-500 uppercase mb-3">Major Risks</h4>
                    <div className="space-y-3">
                      {summary.major_risks.map((risk: any, idx: number) => (
                        <div key={idx} className="bg-red-50 p-4 rounded-lg border-l-4 border-red-500">
                          <div className="flex justify-between items-start mb-2">
                            <h5 className="font-semibold text-gray-900">{risk.risk || risk.description}</h5>
                            {risk.priority && (
                              <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                                risk.priority === 'high' ? 'bg-red-200 text-red-800' : 'bg-yellow-200 text-yellow-800'
                              }`}>
                                {risk.priority}
                              </span>
                            )}
                          </div>
                          {risk.impact && <p className="text-sm text-gray-700 mb-1"><strong>Impact:</strong> {risk.impact}</p>}
                          {risk.mitigation && <p className="text-sm text-gray-700"><strong>Mitigation:</strong> {risk.mitigation}</p>}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Dependencies */}
                {summary.dependencies && Array.isArray(summary.dependencies) && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-500 uppercase mb-3">Dependencies</h4>
                    <div className="space-y-3">
                      {summary.dependencies.map((dep: any, idx: number) => (
                        <div key={idx} className="bg-amber-50 p-4 rounded-lg border-l-4 border-amber-500">
                          <h5 className="font-semibold text-gray-900 mb-2">{dep.dependency}</h5>
                          <div className="text-sm text-gray-700 space-y-1">
                            {dep.type && <p><strong>Type:</strong> {dep.type}</p>}
                            {dep.timeline_impact && <p><strong>Timeline Impact:</strong> {dep.timeline_impact}</p>}
                            {dep.mitigation && <p><strong>Mitigation:</strong> {dep.mitigation}</p>}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              </div>
              )}

              {/* Next Steps */}
              {summary.next_steps && Array.isArray(summary.next_steps) && (
              <div className="card mb-6">
                <h3 className="text-2xl font-bold text-gray-900 mb-2 flex items-center gap-3">
                  <span>🚀 Next Steps</span>
                  <span className="px-3 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                    Action Items
                  </span>
                </h3>
              <div className="space-y-3 mt-6">
                {summary.next_steps.map((step: any, idx: number) => (
                  <div key={idx} className="flex items-start space-x-4 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border-2 border-blue-200">
                    <div className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold">
                      {idx + 1}
                    </div>
                    <div className="flex-grow">
                      <h5 className="font-semibold text-gray-900 mb-1">{step.step}</h5>
                      <div className="flex flex-wrap gap-2 text-xs text-gray-600">
                        {step.owner && <span className="bg-white px-2 py-1 rounded">👤 {step.owner}</span>}
                        {step.timeline && <span className="bg-white px-2 py-1 rounded">📅 {step.timeline}</span>}
                        {step.importance && (
                          <span className={`px-2 py-1 rounded font-semibold ${
                            step.importance === 'high' ? 'bg-red-200 text-red-800' : 'bg-gray-200 text-gray-800'
                          }`}>
                            {step.importance} importance
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              </div>
              )}
            </>
          )}
        </>
      )}

      {analysis?.status === 'failed' && (
        <div className="card">
          <div className="text-center py-8">
            <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Analysis Failed
            </h3>
            <p className="text-gray-600 mb-4">
              We encountered an issue while analyzing your project. Please try again.
            </p>
            <button
              onClick={onNewAnalysis}
              className="btn-primary"
            >
              Start New Analysis
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
