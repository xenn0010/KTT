import { useEffect, useMemo, useRef, useState } from 'react'
import ForceGraph2D, { type ForceGraphMethods } from 'react-force-graph-2d'
import type { GraphData, NodeObject } from 'force-graph'

type GraphNode = NodeObject & {
  id: string
  label: string
  group: 'container' | 'manifest' | 'route' | 'sensor' | 'driver' | 'risk'
  metric?: string
}

type GraphPayload = {
  nodes: GraphNode[]
  links: Array<{
    source: string
    target: string
    label: string
  }>
}

const GRAPH_PAYLOAD: GraphPayload = {
  nodes: [
    {
      id: 'container-alpha',
      label: 'Container • ALPHA',
      group: 'container',
      metric: 'Util 94%',
    },
    {
      id: 'container-bravo',
      label: 'Container • BRAVO',
      group: 'container',
      metric: 'Util 72%',
    },
    {
      id: 'manifest-23',
      label: 'Manifest • 23',
      group: 'manifest',
      metric: 'Cold chain',
    },
    {
      id: 'manifest-24',
      label: 'Manifest • 24',
      group: 'manifest',
    },
    {
      id: 'route-atl-nyc',
      label: 'Route • ATL → NYC',
      group: 'route',
      metric: 'Score 0.87',
    },
    {
      id: 'driver-idris',
      label: 'Driver • Idris Cole',
      group: 'driver',
    },
    {
      id: 'sensor-904',
      label: 'Sensor • 904',
      group: 'sensor',
      metric: '−18°C',
    },
    {
      id: 'sensor-910',
      label: 'Sensor • 910',
      group: 'sensor',
      metric: 'Door latch',
    },
    {
      id: 'risk-bio',
      label: 'Bio compliance',
      group: 'risk',
      metric: 'Green',
    },
    {
      id: 'risk-delay',
      label: 'Delay risk',
      group: 'risk',
      metric: '2 flags',
    },
  ],
  links: [
    { source: 'container-alpha', target: 'manifest-23', label: 'Hosts' },
    { source: 'container-alpha', target: 'sensor-904', label: 'Monitored by' },
    { source: 'container-alpha', target: 'route-atl-nyc', label: 'Routed' },
    { source: 'container-alpha', target: 'risk-delay', label: 'Risk' },
    { source: 'container-bravo', target: 'manifest-24', label: 'Hosts' },
    { source: 'container-bravo', target: 'sensor-910', label: 'Monitored by' },
    { source: 'container-bravo', target: 'risk-bio', label: 'Risk' },
    { source: 'manifest-23', target: 'driver-idris', label: 'Assigned' },
    { source: 'manifest-24', target: 'driver-idris', label: 'History' },
    { source: 'manifest-23', target: 'risk-bio', label: 'Compliance' },
    { source: 'sensor-904', target: 'risk-bio', label: 'Feeds' },
    { source: 'route-atl-nyc', target: 'risk-delay', label: 'Latency' },
  ],
}

const groupColors: Record<GraphNode['group'], string> = {
  container: '#7f5dff',
  manifest: '#66c0f4',
  route: '#37f0d3',
  sensor: '#f9c851',
  driver: '#ff9eb5',
  risk: '#ff7b5f',
}

const Neo4jGraph = () => {
  const graphRef = useRef<ForceGraphMethods | undefined>(undefined)
  const containerRef = useRef<HTMLDivElement>(null)
  const [activeNode, setActiveNode] = useState('container-alpha')
  const [dimensions, setDimensions] = useState({ width: 720, height: 420 })
  const data = useMemo<GraphData>(() => GRAPH_PAYLOAD as GraphData, [])

  useEffect(() => {
    if (!containerRef.current) return

    const updateSize = () => {
      const { width, height } = containerRef.current?.getBoundingClientRect() ??
        { width: 720, height: 420 }
      setDimensions({
        width: width || 720,
        height: Math.max(height || 420, 320),
      })
    }

    updateSize()

    const observer = new ResizeObserver(() => updateSize())
    observer.observe(containerRef.current)

    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    if (!graphRef.current) return
    graphRef.current.centerAt(0, 0, 400)
    graphRef.current.zoom(1.2, 400)
  }, [])

  return (
    <div className="graph-wrapper" ref={containerRef}>
      <ForceGraph2D
        ref={graphRef}
        width={dimensions.width}
        height={dimensions.height}
        graphData={data}
        backgroundColor="transparent"
        nodeRelSize={6}
        linkDirectionalParticles={2}
        linkDirectionalParticleSpeed={0.005}
        linkColor={() => '#1f2335'}
        linkWidth={0.8}
        nodeCanvasObject={(node, ctx) => {
          const gNode = node as GraphNode
          const x = gNode.x ?? 0
          const y = gNode.y ?? 0
          const radius = activeNode === gNode.id ? 11 : 7

          const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius)
          gradient.addColorStop(0, `${groupColors[gNode.group]}dd`)
          gradient.addColorStop(1, `${groupColors[gNode.group]}44`)

          ctx.beginPath()
          ctx.fillStyle = gradient
          ctx.arc(x, y, radius, 0, 2 * Math.PI)
          ctx.fill()

          ctx.strokeStyle = activeNode === gNode.id ? '#ffffff' : '#1b1f2e'
          ctx.lineWidth = activeNode === gNode.id ? 2 : 1
          ctx.stroke()

          ctx.font = '500 12px "Space Grotesk", sans-serif'
          ctx.fillStyle = '#e3e7ff'
          ctx.fillText(gNode.label, x + radius + 6, y + 4)

          if (gNode.metric) {
            ctx.font = '400 10px "Space Grotesk", sans-serif'
            ctx.fillStyle = '#6dd5ff'
            ctx.fillText(gNode.metric, x + radius + 6, y + 18)
          }
        }}
        nodePointerAreaPaint={(node, color, ctx) => {
          const gNode = node as GraphNode
          const x = gNode.x ?? 0
          const y = gNode.y ?? 0
          ctx.fillStyle = color
          ctx.beginPath()
          ctx.arc(x, y, 12, 0, 2 * Math.PI, false)
          ctx.fill()
        }}
        onNodeClick={(node) => setActiveNode((node as GraphNode).id)}
      />
    </div>
  )
}

export default Neo4jGraph
