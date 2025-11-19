import { Suspense, useMemo } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, OrthographicCamera } from '@react-three/drei'
import type { PackingPlan, Placement } from '../types/kitt'

type TruckVisualizerProps = {
  plan: PackingPlan | null
}

type ContainerDimensions = {
  width: number
  height: number
  depth: number
}

const GRAYS = ['#ffffff', '#dcdcdc', '#c0c0c0', '#a6a6a6', '#8c8c8c']

function computeContainer(placements: Placement[]): ContainerDimensions {
  if (!placements.length) {
    return { width: 200, height: 200, depth: 200 }
  }

  const maxX = Math.max(
    ...placements.map((p) => p.position.x + p.dimensions.width),
  )
  const maxY = Math.max(
    ...placements.map((p) => p.position.y + p.dimensions.height),
  )
  const maxZ = Math.max(
    ...placements.map((p) => p.position.z + p.dimensions.depth),
  )

  return {
    width: maxX + 20,
    height: maxY + 20,
    depth: maxZ + 20,
  }
}

const CargoBox = ({
  placement,
  container,
  color,
}: {
  placement: Placement
  container: ContainerDimensions
  color: string
}) => {
  const { position, dimensions } = placement
  const maxDimension = Math.max(container.width, container.depth)
  const scale = 2.5 / maxDimension

  const offsetX = position.x + dimensions.width / 2 - container.width / 2
  const offsetY = position.y + dimensions.height / 2
  const offsetZ = position.z + dimensions.depth / 2 - container.depth / 2

  return (
    <mesh
      position={[offsetX * scale, offsetY * scale, offsetZ * scale]}
      castShadow
      receiveShadow
    >
      <boxGeometry
        args={[
          dimensions.width * scale,
          dimensions.height * scale,
          dimensions.depth * scale,
        ]}
      />
      <meshStandardMaterial color={color} metalness={0.05} roughness={0.65} />
    </mesh>
  )
}

const ContainerWire = ({ container }: { container: ContainerDimensions }) => {
  const scale = 2.5 / Math.max(container.width, container.depth)

  return (
    <mesh position={[0, (container.height * scale) / 2, 0]}>
      <boxGeometry
        args={[
          container.width * scale,
          container.height * scale,
          container.depth * scale,
        ]}
      />
      <meshBasicMaterial color="#f8f8f8" wireframe transparent opacity={0.2} />
    </mesh>
  )
}

const GroundPlane = () => (
  <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.01, 0]} receiveShadow>
    <planeGeometry args={[10, 10]} />
    <meshStandardMaterial color="#050505" />
  </mesh>
)

const TruckVisualizer = ({ plan }: TruckVisualizerProps) => {
  const placements = plan?.placements ?? []
  const container = useMemo(() => computeContainer(placements), [placements])

  return (
    <Canvas shadows className="truck-canvas">
      <Suspense fallback={null}>
        <OrthographicCamera makeDefault position={[4, 4, 4]} zoom={90} />
        <ambientLight intensity={0.7} />
        <directionalLight
          position={[5, 6, 3]}
          intensity={0.8}
          castShadow
          color="#ffffff"
        />
        <ContainerWire container={container} />
        {placements.map((placement, idx) => (
          <CargoBox
            key={placement.item_id ?? idx}
            placement={placement}
            container={container}
            color={GRAYS[idx % GRAYS.length]}
          />
        ))}
        <GroundPlane />
        <OrbitControls enablePan={false} minZoom={40} maxZoom={140} />
      </Suspense>
    </Canvas>
  )
}

export default TruckVisualizer
