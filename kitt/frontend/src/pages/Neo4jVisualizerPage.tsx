import Neo4jGraph from '../components/Neo4jGraph'

const filters = ['Shipments', 'Containers', 'Sensors', 'Risks']

const insights = [
  {
    title: 'Manifest-23',
    detail: 'Linked to 3 refrigerated cubes · 92% utilization',
    status: 'Synced 2s ago',
  },
  {
    title: 'Route ATL → NYC',
    detail: 'Neo4j path score 0.87 · 2 anomaly flags cleared',
    status: 'Green corridor',
  },
  {
    title: 'Driver Idris Cole',
    detail: 'Bio-scan verified · Connected to Manifest-21 + 23',
    status: 'Authenticated',
  },
]

const Neo4jVisualizerPage = () => {
  return (
    <div className="neo4j-page">
      <section className="panel">
        <div className="page-header">
          <div>
            <p className="eyebrow">Graph intelligence</p>
            <h1>Neo4j knowledge fabric</h1>
          </div>
          <p className="muted max-420">
            Visualize how containers, manifests, drivers, and IoT sensors connect
            in real time. Every relationship is queryable, auditable, and ready
            for autonomous decisioning.
          </p>
        </div>

        <div className="neo4j-toolbar">
          <div className="chip-group">
            {filters.map((chip, index) => (
              <button
                key={chip}
                className={`chip ${index === 0 ? 'chip--active' : ''}`}
              >
                {chip}
              </button>
            ))}
          </div>
          <div className="chip status-chip">
            Density map <span>live</span>
          </div>
        </div>

        <div className="neo4j-content">
          <div className="graph-card">
            <Neo4jGraph />
          </div>

          <div className="neo4j-sidebar">
            <h3>Relationship insights</h3>
            <p className="muted">
              Summaries generated from live Neo4j cypher queries.
            </p>

            <div className="insight-list">
              {insights.map((insight) => (
                <div key={insight.title} className="insight-item">
                  <p className="label">{insight.title}</p>
                  <p>{insight.detail}</p>
                  <small>{insight.status}</small>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

export default Neo4jVisualizerPage
