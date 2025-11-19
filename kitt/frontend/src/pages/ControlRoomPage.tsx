import type { FormEvent } from 'react'
import { useEffect, useMemo, useState } from 'react'
import TruckVisualizer from '../components/TruckVisualizer'
import GlobePanel, { type GlobeConnection } from '../components/GlobePanel'
import {
  fetchShipments,
  fetchPackingPlan,
  fetchAIAnalysis,
  fetchRoute,
  runOptimize,
} from '../lib/api'
import type {
  AIStrategy,
  PackingPlan,
  RouteConditions,
  ShipmentRecord,
} from '../types/kitt'
import {
  sampleShipments,
  samplePacking,
  sampleAnalysis,
  sampleRoute,
} from '../sample-data'

const CITY_COORDS: Record<string, { lat: number; lng: number }> = {
  'los angeles': { lat: 34.05, lng: -118.24 },
  'new york': { lat: 40.71, lng: -74.01 },
  chicago: { lat: 41.87, lng: -87.62 },
  miami: { lat: 25.76, lng: -80.19 },
  'san francisco': { lat: 37.77, lng: -122.42 },
  dallas: { lat: 32.78, lng: -96.8 },
  atlanta: { lat: 33.75, lng: -84.39 },
  denver: { lat: 39.74, lng: -104.99 },
  seattle: { lat: 47.61, lng: -122.33 },
  boston: { lat: 42.36, lng: -71.05 },
}

const ControlRoomPage = () => {
  const [shipments, setShipments] = useState<ShipmentRecord[]>([])
  const [activeShipment, setActiveShipment] = useState<ShipmentRecord | null>(
    null,
  )
  const [packingPlan, setPackingPlan] = useState<PackingPlan | null>(null)
  const [aiStrategy, setAIStrategy] = useState<AIStrategy | null>(null)
  const [routeConditions, setRouteConditions] = useState<RouteConditions | null>(
    null,
  )
  const [promptInput, setPromptInput] = useState('')
  const [promptStatus, setPromptStatus] = useState<
    'idle' | 'loading' | 'success' | 'error'
  >('idle')
  const [promptMessage, setPromptMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadShipments = async () => {
      setLoading(true)
      try {
        const response = await fetchShipments(4)
        setShipments(response)
        setActiveShipment(response[0] ?? null)
        setError(null)
      } catch (err) {
        console.warn('Falling back to sample shipments', err)
        setShipments(sampleShipments)
        setActiveShipment(sampleShipments[0] ?? null)
        setError('Live API unreachable, using sample manifest')
      } finally {
        setLoading(false)
      }
    }

    loadShipments()
  }, [])

  useEffect(() => {
    if (!activeShipment) return
    let canceled = false

    const loadDetail = async () => {
      try {
        const [packing, analysis, route] = await Promise.all([
          fetchPackingPlan(activeShipment.id).catch(() => samplePacking),
          fetchAIAnalysis(activeShipment.id).catch(() => sampleAnalysis),
          fetchRoute(activeShipment.origin, activeShipment.destination).catch(
            () => sampleRoute,
          ),
        ])
        if (canceled) return
        setPackingPlan(packing)
        setAIStrategy(analysis)
        setRouteConditions(route)
      } catch (err) {
        if (canceled) return
        console.warn('Detail fetch failed, using samples', err)
        setPackingPlan(samplePacking)
        setAIStrategy(sampleAnalysis)
        setRouteConditions(sampleRoute)
      }
    }

    loadDetail()
    return () => {
      canceled = true
    }
  }, [activeShipment])

  const arcs = useMemo<GlobeConnection[]>(() => {
    return shipments
      .map((shipment) => {
        const origin = CITY_COORDS[shipment.origin?.toLowerCase() ?? '']
        const dest = CITY_COORDS[shipment.destination?.toLowerCase() ?? '']
        if (!origin || !dest) return null
        return {
          startLat: origin.lat,
          startLng: origin.lng,
          endLat: dest.lat,
          endLng: dest.lng,
          label: shipment.id,
        }
      })
      .filter(Boolean) as GlobeConnection[]
  }, [shipments])

  const analysisHighlights = useMemo(() => {
    if (!aiStrategy) return []
    return [
      aiStrategy.loading_strategy,
      ...(aiStrategy.special_handling_items ?? []),
      ...(aiStrategy.truck_selection_criteria ?? []),
    ].filter(Boolean)
  }, [aiStrategy])

  const utilization =
    packingPlan?.utilization_percentage ?? packingPlan?.utilization ?? 0

  const handlePromptSubmit = async (event: FormEvent) => {
    event.preventDefault()
    if (!activeShipment || !promptInput.trim()) return

    const command = parseCommand(promptInput)
    const shipmentId = extractShipmentId(promptInput, activeShipment.id)

    setPromptStatus('loading')
    setPromptMessage('Transmitting to KITT core...')

    try {
      if (command === 'optimize') {
        const result = await runOptimize(shipmentId)
        if (result.packing) setPackingPlan(result.packing)
        if (result.ai_analysis) setAIStrategy(result.ai_analysis)
        if (result.route_conditions) setRouteConditions(result.route_conditions)
        setPromptMessage(`Optimization triggered for ${shipmentId}`)
      } else if (command === 'pack') {
        const result = await fetchPackingPlan(shipmentId)
        setPackingPlan(result)
        setPromptMessage(`Packing refresh complete for ${shipmentId}`)
      } else if (command === 'route' && activeShipment.origin) {
        const route = await fetchRoute(
          activeShipment.origin,
          activeShipment.destination,
        )
        setRouteConditions(route)
        setPromptMessage(`Route diagnostics updated for ${shipmentId}`)
      } else {
        const analysis = await fetchAIAnalysis(shipmentId)
        setAIStrategy(analysis)
        setPromptMessage(`AI analysis regenerated for ${shipmentId}`)
      }
      setPromptStatus('success')
      setPromptInput('')
    } catch (err) {
      console.error(err)
      setPromptStatus('error')
      setPromptMessage(
        (err as Error).message ||
          'Prompt dispatch failed. Confirm API server availability.',
      )
    }
  }

  return (
    <div className="control-room">
      <header className="kitt-header">
        <span>Autonomous Freight Console</span>
        <div className="kitt-title">KITT</div>
        <span>Blackline logistics · real-time load intelligence</span>
        {error && <span className="failure">{error}</span>}
      </header>

      <div className="kitt-grid">
        <section className="panel truck-panel">
          <div className="panel-headline">
            <h2>Truck Container</h2>
            <span>
              {activeShipment
                ? `${activeShipment.origin} → ${activeShipment.destination}`
                : 'Awaiting manifest'}
            </span>
          </div>

          <div className="metrics-row">
            <div className="metric-card">
              Utilization
              <strong>{utilization ? `${utilization.toFixed(1)}%` : '--'}</strong>
            </div>
            <div className="metric-card">
              Items Packed
              <strong>{packingPlan?.placements.length ?? 0}</strong>
            </div>
            <div className="metric-card">
              Priority
              <strong>{activeShipment?.priority ?? '—'}</strong>
            </div>
          </div>

          <div className="truck-view">
            <TruckVisualizer plan={packingPlan ?? samplePacking} />
          </div>
        </section>

        <section className="panel info-panel">
          <div>
            <div className="panel-headline">
              <h2>Active Shipments</h2>
            </div>
            <div className="shipments-list">
              {loading && <span>Syncing manifest…</span>}
              {!loading &&
                shipments.map((shipment) => (
                  <button
                    key={shipment.id}
                    className={`shipment-card ${
                      shipment.id === activeShipment?.id ? 'active' : ''
                    }`}
                    onClick={() => setActiveShipment(shipment)}
                  >
                    <small>{shipment.id}</small>
                    <strong>
                      {shipment.origin} → {shipment.destination}
                    </strong>
                    <small>{shipment.status ?? 'unknown status'}</small>
                  </button>
                ))}
            </div>
          </div>

          <div className="prompt-panel">
            <label>Prompt Base</label>
            <form className="prompt-row" onSubmit={handlePromptSubmit}>
              <input
                className="prompt-input"
                placeholder="e.g. Optimize SH-001 or Analyze shipment"
                value={promptInput}
                onChange={(event) => setPromptInput(event.target.value)}
              />
              <button className="prompt-button" type="submit">
                Send
              </button>
            </form>
            <div className={`prompt-status ${promptStatus}`}>
              {promptMessage}
            </div>
          </div>

          <div>
            <div className="panel-headline">
              <h2>Neo Threads</h2>
              <span>globe telemetry</span>
            </div>
            <div className="panel panel--globe">
              <GlobePanel arcs={arcs} />
            </div>
          </div>
        </section>
      </div>

      <section className="panel">
        <div className="panel-headline">
          <h2>Loading Instructions</h2>
          {routeConditions?.current_traffic?.level && (
            <span>
              Traffic {routeConditions.current_traffic.level} · Delay{' '}
              {routeConditions.current_traffic.delay_minutes ?? 0}m
            </span>
          )}
        </div>

        <div className="analysis-list">
          {analysisHighlights.length === 0 && (
            <span>No AI instructions available yet.</span>
          )}
          {analysisHighlights.map((entry, index) => (
            <div key={index} className="analysis-item">
              <span>Directive {index + 1}</span>
              <strong>{entry}</strong>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}

export default ControlRoomPage

function parseCommand(text: string): 'optimize' | 'pack' | 'analyze' | 'route' {
  const normalized = text.toLowerCase()
  if (normalized.includes('optimize')) return 'optimize'
  if (normalized.includes('route')) return 'route'
  if (normalized.includes('pack')) return 'pack'
  if (normalized.includes('load')) return 'pack'
  return 'analyze'
}

function extractShipmentId(text: string, fallback?: string) {
  const match = text.toUpperCase().match(/SH-[A-Z0-9-]+/)
  return match ? match[0] : fallback ?? ''
}
