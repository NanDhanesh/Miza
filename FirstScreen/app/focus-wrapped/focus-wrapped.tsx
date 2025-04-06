import "./focus-wrapped.css"

interface FocusWrappedProps {
  focusPercentage: number
  checklistPercentage: number
  overallScore: number
  //totalFocusHours: number
  //userName?: string
}

export default function FocusWrapped({
  focusPercentage = 78,
  checklistPercentage = 85,
  overallScore = 82,
  //totalFocusHours = 124,
  //userName = "there",
}: FocusWrappedProps) {
  return (
    <div className="wrapped-container">
      <div className="wrapped-content">
        <div className="wrapped-header">
          <h1>Your Study Session Wrapped</h1>
          <p className="wrapped-subtitle">Hey user, here's how you crushed it this year!</p>
        </div>

        <div className="stats-container">
          <div className="stat-item focus-time">
            <div className="stat-circle">
              <svg viewBox="0 0 100 100">
                <circle className="stat-circle-bg" cx="50" cy="50" r="40"></circle>
                <circle
                  className="stat-circle-progress"
                  cx="50"
                  cy="50"
                  r="40"
                  style={{
                    strokeDashoffset: 251.2 - (251.2 * focusPercentage) / 100,
                  }}
                ></circle>
              </svg>
              <div className="stat-circle-text">
                <span className="stat-value">{focusPercentage}%</span>
                <span className="stat-label">Productivity Ratio</span>
              </div>
            </div>
            <p className="stat-description">This much of your browser activity was productive</p>
          </div>

          <div className="stat-item checklist">
            <div className="stat-circle">
              <svg viewBox="0 0 100 100">
                <circle className="stat-circle-bg" cx="50" cy="50" r="40"></circle>
                <circle
                  className="stat-circle-progress checklist-progress"
                  cx="50"
                  cy="50"
                  r="40"
                  style={{
                    strokeDashoffset: 251.2 - (251.2 * checklistPercentage) / 100,
                  }}
                ></circle>
              </svg>
              <div className="stat-circle-text">
                <span className="stat-value">{checklistPercentage}%</span>
                <span className="stat-label">Tasks Completed</span>
              </div>
            </div>
            <p className="stat-description">You're a checklist champion!</p>
          </div>

          <div className="stat-item overall-score">
            <div className="stat-circle">
              <svg viewBox="0 0 100 100">
                <circle className="stat-circle-bg" cx="50" cy="50" r="40"></circle>
                <circle
                  className="stat-circle-progress overall-progress"
                  cx="50"
                  cy="50"
                  r="40"
                  style={{
                    strokeDashoffset: 251.2 - (251.2 * overallScore) / 100,
                  }}
                ></circle>
              </svg>
              <div className="stat-circle-text">
                <span className="stat-value">{overallScore}</span>
                <span className="stat-label">Visual Focus</span>
              </div>
            </div>
            <p className="stat-description">Did you keep your eyes on the prize?</p>
          </div>
        </div>

        <div className="wrapped-footer">
          <p className="footer-text">Keep up the great work next time!</p>
        </div>
      </div>
    </div>
  )
}
