import { useEffect, useRef } from 'react'

export type GlobeConnection = {
  startLat: number
  startLng: number
  endLat: number
  endLng: number
  label?: string
}

type GlobePanelProps = {
  arcs: GlobeConnection[]
}

const GlobePanel = ({ arcs }: GlobePanelProps) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const globeRef = useRef<any>(null)

  useEffect(() => {
    let mounted = true
    const initGlobe = async () => {
      if (!containerRef.current) return
      const module = await import('globe.gl')
      if (!mounted || !containerRef.current) return

      const globeFactory = module.default as unknown as () => any
      globeRef.current = globeFactory()(containerRef.current)
        .globeImageUrl('//unpkg.com/three-globe/example/img/earth-night.jpg')
        .bumpImageUrl('//unpkg.com/three-globe/example/img/earth-topology.png')
        .backgroundColor('rgba(0,0,0,0)')
        .pointOfView({ lat: 20, lng: -20, altitude: 2.1 })
        .arcColor(() => ['#50e6ff', '#ec4fff'])
        .arcDashLength(0.6)
        .arcDashGap(0.25)
        .arcDashAnimateTime(4800)
        .arcsTransitionDuration(0)
        .showAtmosphere(false)
        .enablePointerInteraction(false)
    }

    initGlobe()

    return () => {
      mounted = false
    }
  }, [])

  useEffect(() => {
    if (!globeRef.current) return
    globeRef.current.arcsData(arcs)
  }, [arcs])

  return <div className="globe-view" ref={containerRef} />
}

export default GlobePanel
