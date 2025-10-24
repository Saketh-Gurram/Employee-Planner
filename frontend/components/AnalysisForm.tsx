import { useForm } from 'react-hook-form'
import { PaperAirplaneIcon } from '@heroicons/react/24/outline'

interface ProjectInput {
  description: string
  budget_range?: string
  timeline_preference?: string
  industry?: string
}

interface AnalysisFormProps {
  onSubmit: (data: ProjectInput) => void
  isLoading: boolean
}

export function AnalysisForm({ onSubmit, isLoading }: AnalysisFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset
  } = useForm<ProjectInput>()

  const handleFormSubmit = (data: ProjectInput) => {
    onSubmit(data)
    reset()
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="card-gradient shadow-xl">
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-3">
            <div className="bg-gradient-to-r from-primary-600 to-accent-500 p-2 rounded-xl">
              <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h2 className="text-3xl font-bold gradient-text-ai">
              Describe Your Project Idea
            </h2>
          </div>
          <p className="text-base text-gray-600 leading-relaxed">
            Our AI agents will analyze your project and provide detailed feasibility analysis,
            team recommendations, cost estimates, and technical architecture — all based on your
            company's historical data.
          </p>
        </div>

        <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
          {/* Project Description */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
              Project Description *
            </label>
            <textarea
              id="description"
              rows={6}
              className="textarea-field"
              placeholder="Describe your project idea in detail. Include the problem you're solving, target users, key features, and any specific requirements..."
              {...register('description', {
                required: 'Project description is required',
                minLength: {
                  value: 50,
                  message: 'Please provide a more detailed description (at least 50 characters)'
                }
              })}
            />
            {errors.description && (
              <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
            )}
          </div>

          {/* Optional Context - Collapsible */}
          <details className="bg-gradient-to-br from-primary-50/50 to-accent-50/50 rounded-xl p-5 border border-primary-100">
            <summary className="cursor-pointer text-sm font-semibold text-gray-800 mb-2 hover:text-primary-600 transition-colors flex items-center space-x-2">
              <span>📋</span>
              <span>Optional: Add Context (Budget, Timeline, Industry)</span>
            </summary>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
              <div>
                <label htmlFor="budget_range" className="block text-xs font-medium text-gray-600 mb-1">
                  Budget Range (Optional)
                </label>
                <select
                  id="budget_range"
                  className="input-field text-sm"
                  {...register('budget_range')}
                >
                  <option value="">Not specified</option>
                  <option value="under_25k">Under $25,000</option>
                  <option value="25k_50k">$25,000 - $50,000</option>
                  <option value="50k_100k">$50,000 - $100,000</option>
                  <option value="100k_250k">$100,000 - $250,000</option>
                  <option value="over_250k">Over $250,000</option>
                </select>
              </div>

              <div>
                <label htmlFor="timeline_preference" className="block text-xs font-medium text-gray-600 mb-1">
                  Preferred Timeline (Optional)
                </label>
                <select
                  id="timeline_preference"
                  className="input-field text-sm"
                  {...register('timeline_preference')}
                >
                  <option value="">Not specified</option>
                  <option value="asap">ASAP (Rush job)</option>
                  <option value="1_3_months">1-3 months</option>
                  <option value="3_6_months">3-6 months</option>
                  <option value="6_12_months">6-12 months</option>
                  <option value="over_12_months">Over 12 months</option>
                </select>
              </div>

              <div>
                <label htmlFor="industry" className="block text-xs font-medium text-gray-600 mb-1">
                  Industry (Optional)
                </label>
                <select
                  id="industry"
                  className="input-field text-sm"
                  {...register('industry')}
                >
                  <option value="">Not specified</option>
                  <option value="healthcare">Healthcare</option>
                  <option value="finance">Finance</option>
                  <option value="ecommerce">E-commerce</option>
                  <option value="education">Education</option>
                  <option value="entertainment">Entertainment</option>
                  <option value="productivity">Productivity</option>
                  <option value="iot">IoT</option>
                  <option value="saas">SaaS</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>
          </details>

          {/* Submit Button */}
          <div className="flex justify-center pt-8">
            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary flex items-center space-x-3 px-10 py-4 text-lg font-bold shadow-lg"
            >
              {isLoading ? (
                <>
                  <div className="spinner h-5 w-5"></div>
                  <span>Analyzing Project...</span>
                </>
              ) : (
                <>
                  <PaperAirplaneIcon className="h-5 w-5" />
                  <span>Analyze Project</span>
                </>
              )}
            </button>
          </div>
        </form>

        {/* Example */}
        <div className="mt-10 p-6 bg-gradient-to-br from-gray-50 to-primary-50/30 rounded-xl border-2 border-dashed border-primary-200">
          <div className="flex items-center space-x-2 mb-3">
            <svg className="h-5 w-5 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <h3 className="font-bold text-gray-900">Example Project Description:</h3>
          </div>
          <p className="text-sm text-gray-700 leading-relaxed italic">
            "We want to build a cross-platform mobile app for fitness tracking that integrates
            with popular wearable devices. The app should track workouts, nutrition, sleep patterns,
            and provide AI-powered insights and recommendations. Target users are fitness enthusiasts
            aged 25-45. Key features include social sharing, personal trainer matching, and
            progress analytics."
          </p>
        </div>
      </div>
    </div>
  )
}