/**
 * Interactive 3D Truck Loading Visualization for Next.js
 * Uses React Three Fiber for smooth 3D rendering
 *
 * Installation:
 *   npm install three @react-three/fiber @react-three/drei
 *
 * Usage:
 *   import TruckLoadingViewer from '@/components/TruckLoadingViewer'
 *
 *   <TruckLoadingViewer
 *     packingData={packingData}  // From your API
 *     width="100%"
 *     height="600px"
 *   />
 */

'use client'

import { useRef, useState, Suspense } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera, Text, Box, Line } from '@react-three/drei'
import * as THREE from 'three'

// TypeScript interfaces
interface Position {
  x: number
  y: number
  z: number
}

interface Dimensions {
  width: number
  height: number
  depth: number
}

interface PackingItem {
  item_id: string
  position: Position
  dimensions: Dimensions
  weight?: number
  rotation?: number
}

interface Container {
  dimensions: Dimensions
  type?: string
}

interface PackingStats {
  utilization: number
  items_packed: number
  total_weight_kg?: number
  algorithm: string
  computation_ms?: number
}

interface PackingData {
  container: Container
  items: PackingItem[]
  stats: PackingStats
}

interface TruckLoadingViewerProps {
  packingData: PackingData
  width?: string | number
  height?: string | number
  showStats?: boolean
  autoRotate?: boolean
}

// Color palette for boxes
const COLORS = [
  '#ff6666', // Red
  '#66ff66', // Green
  '#6666ff', // Blue
  '#ffff66', // Yellow
  '#ff66ff', // Magenta
  '#66ffff', // Cyan
  '#ff9966', // Orange
  '#9966ff', // Purple
]

// Container wireframe component
function ContainerWireframe({ dimensions }: { dimensions: Dimensions }) {
  const { width, height, depth } = dimensions

  // Create edges for wireframe
  const points = [
    // Bottom face
    new THREE.Vector3(0, 0, 0),
    new THREE.Vector3(width, 0, 0),
    new THREE.Vector3(width, 0, depth),
    new THREE.Vector3(0, 0, depth),
    new THREE.Vector3(0, 0, 0),
    // Go up to top face
    new THREE.Vector3(0, height, 0),
    new THREE.Vector3(width, height, 0),
    new THREE.Vector3(width, 0, 0),
    new THREE.Vector3(width, height, 0),
    new THREE.Vector3(width, height, depth),
    new THREE.Vector3(width, 0, depth),
    new THREE.Vector3(width, height, depth),
    new THREE.Vector3(0, height, depth),
    new THREE.Vector3(0, 0, depth),
    new THREE.Vector3(0, height, depth),
    new THREE.Vector3(0, height, 0),
  ]

  return (
    <Line
      points={points}
      color="#888888"
      lineWidth={2}
      opacity={0.5}
      transparent
    />
  )
}

// Individual cargo box component
function CargoBox({
  item,
  color,
  showLabel = true
}: {
  item: PackingItem
  color: string
  showLabel?: boolean
}) {
  const meshRef = useRef<THREE.Mesh>(null)
  const [hovered, setHovered] = useState(false)

  // Subtle hover animation
  useFrame(() => {
    if (meshRef.current && hovered) {
      meshRef.current.scale.setScalar(1.05)
    } else if (meshRef.current) {
      meshRef.current.scale.setScalar(1.0)
    }
  })

  const { position, dimensions } = item
  const { width, height, depth } = dimensions

  // Center the box at its position
  const centerPos: [number, number, number] = [
    position.x + width / 2,
    position.y + height / 2,
    position.z + depth / 2,
  ]

  return (
    <group>
      {/* The box */}
      <mesh
        ref={meshRef}
        position={centerPos}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
        castShadow
        receiveShadow
      >
        <boxGeometry args={[width, height, depth]} />
        <meshStandardMaterial
          color={color}
          metalness={0.3}
          roughness={0.4}
          transparent
          opacity={hovered ? 0.9 : 0.7}
          emissive={color}
          emissiveIntensity={hovered ? 0.3 : 0.1}
        />
      </mesh>

      {/* Box edges for clarity */}
      <lineSegments position={centerPos}>
        <edgesGeometry args={[new THREE.BoxGeometry(width, height, depth)]} />
        <lineBasicMaterial color="#000000" linewidth={1} />
      </lineSegments>

      {/* Label */}
      {showLabel && (
        <Text
          position={[centerPos[0], centerPos[1] + height / 2 + 10, centerPos[2]]}
          fontSize={12}
          color="white"
          anchorX="center"
          anchorY="middle"
          outlineWidth={2}
          outlineColor="#000000"
        >
          {item.item_id}
        </Text>
      )}

      {/* Tooltip on hover */}
      {hovered && (
        <Text
          position={[centerPos[0], centerPos[1] + height / 2 + 25, centerPos[2]]}
          fontSize={10}
          color="#ffff00"
          anchorX="center"
          anchorY="middle"
          outlineWidth={1}
          outlineColor="#000000"
        >
          {`${width.toFixed(0)}×${height.toFixed(0)}×${depth.toFixed(0)} cm`}
          {item.weight && `\n${item.weight} kg`}
        </Text>
      )}
    </group>
  )
}

// Main 3D scene
function Scene({ packingData, autoRotate }: { packingData: PackingData; autoRotate: boolean }) {
  const { container, items } = packingData
  const containerDims = container.dimensions

  // Calculate center for camera focus
  const center: [number, number, number] = [
    containerDims.width / 2,
    containerDims.height / 2,
    containerDims.depth / 2,
  ]

  // Calculate optimal camera distance
  const maxDim = Math.max(containerDims.width, containerDims.height, containerDims.depth)
  const cameraDistance = maxDim * 2

  return (
    <>
      {/* Camera */}
      <PerspectiveCamera
        makeDefault
        position={[cameraDistance, cameraDistance * 0.8, cameraDistance]}
        fov={50}
      />

      {/* Lights */}
      <ambientLight intensity={0.5} />
      <directionalLight
        position={[containerDims.width, containerDims.height * 2, containerDims.depth]}
        intensity={1}
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
      />
      <pointLight position={[-containerDims.width / 2, containerDims.height, 0]} intensity={0.5} />

      {/* Container wireframe */}
      <ContainerWireframe dimensions={containerDims} />

      {/* Cargo boxes */}
      {items.map((item, index) => (
        <CargoBox
          key={item.item_id}
          item={item}
          color={COLORS[index % COLORS.length]}
        />
      ))}

      {/* Ground plane (optional) */}
      <mesh position={[containerDims.width / 2, -5, containerDims.depth / 2]} receiveShadow>
        <planeGeometry args={[containerDims.width * 2, containerDims.depth * 2]} />
        <meshStandardMaterial color="#f0f0f0" />
      </mesh>

      {/* Controls */}
      <OrbitControls
        target={center}
        enableDamping
        dampingFactor={0.05}
        autoRotate={autoRotate}
        autoRotateSpeed={0.5}
        maxPolarAngle={Math.PI / 2}
        minDistance={maxDim * 0.5}
        maxDistance={maxDim * 5}
      />
    </>
  )
}

// Stats overlay component
function StatsOverlay({ stats, containerDims }: { stats: PackingStats; containerDims: Dimensions }) {
  return (
    <div className="absolute top-4 left-4 bg-black/70 text-white p-4 rounded-lg font-mono text-sm backdrop-blur-sm">
      <h3 className="text-lg font-bold mb-2">📦 Packing Stats</h3>
      <div className="space-y-1">
        <div>Container: {containerDims.width}×{containerDims.height}×{containerDims.depth} cm</div>
        <div>Items: {stats.items_packed}</div>
        <div>Utilization: <span className="text-green-400 font-bold">{stats.utilization.toFixed(1)}%</span></div>
        {stats.total_weight_kg && <div>Weight: {stats.total_weight_kg} kg</div>}
        <div>Algorithm: {stats.algorithm}</div>
        {stats.computation_ms && <div>Computed in: {stats.computation_ms}ms</div>}
      </div>
    </div>
  )
}

// Controls overlay
function ControlsOverlay() {
  return (
    <div className="absolute bottom-4 right-4 bg-black/70 text-white p-3 rounded-lg text-xs backdrop-blur-sm">
      <div className="space-y-1">
        <div>🖱️ <strong>Left Click + Drag:</strong> Rotate</div>
        <div>🖱️ <strong>Right Click + Drag:</strong> Pan</div>
        <div>🖱️ <strong>Scroll:</strong> Zoom</div>
        <div>📱 <strong>Touch:</strong> Pinch to zoom</div>
      </div>
    </div>
  )
}

// Loading fallback
function LoadingFallback() {
  return (
    <div className="w-full h-full flex items-center justify-center bg-gray-100">
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading 3D visualization...</p>
      </div>
    </div>
  )
}

// Main component
export default function TruckLoadingViewer({
  packingData,
  width = '100%',
  height = '600px',
  showStats = true,
  autoRotate = false,
}: TruckLoadingViewerProps) {
  return (
    <div style={{ width, height }} className="relative">
      <Canvas shadows>
        <Suspense fallback={null}>
          <Scene packingData={packingData} autoRotate={autoRotate} />
        </Suspense>
      </Canvas>

      {showStats && (
        <StatsOverlay stats={packingData.stats} containerDims={packingData.container.dimensions} />
      )}

      <ControlsOverlay />
    </div>
  )
}
