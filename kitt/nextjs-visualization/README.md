# Next.js Truck Loading Visualization

**Interactive 3D visualization using React Three Fiber** - Perfect for modern Next.js websites!

## ✨ Features

- ✅ **Fully Interactive**: Rotate, zoom, pan with mouse/touch
- ✅ **Real-time 3D**: Smooth 60fps rendering
- ✅ **Responsive**: Works on desktop, tablet, mobile
- ✅ **Modern**: Built with React Three Fiber
- ✅ **Beautiful**: Metallic materials, shadows, lighting
- ✅ **Lightweight**: Renders in browser, no backend needed
- ✅ **TypeScript**: Fully typed for better DX

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install three @react-three/fiber @react-three/drei
# or
yarn add three @react-three/fiber @react-three/drei
# or
pnpm add three @react-three/fiber @react-three/drei
```

### 2. Copy Component

Copy `TruckLoadingViewer.tsx` to your Next.js project:

```
your-nextjs-app/
├── app/
│   └── components/
│       └── TruckLoadingViewer.tsx  ← Copy here
```

### 3. Use in Your Page

```tsx
// app/page.tsx
'use client'

import { useEffect, useState } from 'react'
import TruckLoadingViewer from '@/components/TruckLoadingViewer'

export default function HomePage() {
  const [packingData, setPackingData] = useState(null)

  useEffect(() => {
    // Fetch packing data from your API
    fetch('/api/truck-packing')
      .then(res => res.json())
      .then(data => setPackingData(data))
  }, [])

  if (!packingData) {
    return <div>Loading...</div>
  }

  return (
    <div className="min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-8">Truck Loading Optimization</h1>

      <TruckLoadingViewer
        packingData={packingData}
        width="100%"
        height="600px"
        showStats={true}
        autoRotate={false}
      />
    </div>
  )
}
```

## 📊 API Integration

### Create API Endpoint

```typescript
// app/api/truck-packing/route.ts
import { NextResponse } from 'next/server'
import { exec } from 'child_process'
import { promisify } from 'util'
import fs from 'fs/promises'

const execAsync = promisify(exec)

export async function POST(request: Request) {
  const { items, containerDimensions } = await request.json()

  // Run DeepPack3D packing algorithm
  // (You can call your Python script here)
  const { stdout } = await execAsync(
    `cd /home/yab/KTT/kitt && python3 tests/test_real_truck_packing.py`
  )

  // Read the generated packing data
  const packingData = await fs.readFile('/tmp/truck_loading_plan.json', 'utf-8')

  return NextResponse.json(JSON.parse(packingData))
}

export async function GET() {
  // Or just return sample data for demo
  const packingData = await fs.readFile('/tmp/truck_loading_plan.json', 'utf-8')
  return NextResponse.json(JSON.parse(packingData))
}
```

## 🎨 Customization

### Change Colors

```tsx
// In TruckLoadingViewer.tsx, modify COLORS array:
const COLORS = [
  '#1e40af', // Navy blue
  '#0891b2', // Cyan
  '#16a34a', // Green
  '#ea580c', // Orange
  '#dc2626', // Red
]
```

### Adjust Camera Angle

```tsx
<PerspectiveCamera
  makeDefault
  position={[cameraDistance, cameraDistance * 0.8, cameraDistance]}
  fov={50}  // ← Change field of view (30-70)
/>
```

### Material Settings

```tsx
<meshStandardMaterial
  color={color}
  metalness={0.3}  // ← 0=plastic, 1=metal
  roughness={0.4}  // ← 0=shiny, 1=matte
  opacity={0.7}    // ← 0=invisible, 1=opaque
  emissiveIntensity={0.1}  // ← Glow strength
/>
```

### Auto-Rotation Speed

```tsx
<OrbitControls
  autoRotate={true}
  autoRotateSpeed={0.5}  // ← Speed (default: 2.0)
/>
```

### Show/Hide Labels

```tsx
<TruckLoadingViewer
  packingData={packingData}
  showStats={false}  // ← Hide stats overlay
/>

// Or modify CargoBox component:
<CargoBox
  item={item}
  color={color}
  showLabel={false}  // ← Hide item labels
/>
```

## 📱 Responsive Design

The component is fully responsive. Use Tailwind classes for layout:

```tsx
<div className="w-full h-[400px] md:h-[600px] lg:h-[800px]">
  <TruckLoadingViewer
    packingData={packingData}
    width="100%"
    height="100%"
  />
</div>
```

## 🎯 Use Cases

### 1. Landing Page Hero

```tsx
export default function LandingPage() {
  return (
    <section className="h-screen">
      <div className="container mx-auto py-20">
        <h1 className="text-6xl font-bold mb-4">
          Optimize Your Freight Loading
        </h1>
        <p className="text-xl mb-8">
          AI-powered 3D bin packing saves you 30% on fuel costs
        </p>

        <TruckLoadingViewer
          packingData={demoPackingData}
          width="100%"
          height="500px"
          autoRotate={true}
        />
      </div>
    </section>
  )
}
```

### 2. Dashboard Widget

```tsx
export default function Dashboard() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Stats */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-2xl font-bold mb-4">Shipment #12345</h2>
        {/* Stats here */}
      </div>

      {/* 3D Visualization */}
      <div className="bg-white p-6 rounded-lg shadow">
        <TruckLoadingViewer
          packingData={shipmentData}
          width="100%"
          height="400px"
        />
      </div>
    </div>
  )
}
```

### 3. Client Proposal Generator

```tsx
export default function ProposalPage({ clientId }: { clientId: string }) {
  const [beforeData, setBeforeData] = useState(null)
  const [afterData, setAfterData] = useState(null)

  return (
    <div className="max-w-7xl mx-auto p-8">
      <h1 className="text-4xl font-bold mb-8">
        Optimization Proposal for {clientName}
      </h1>

      {/* Before */}
      <section className="mb-12">
        <h2 className="text-2xl font-bold mb-4">Current State</h2>
        <TruckLoadingViewer
          packingData={beforeData}
          height="400px"
        />
        <p className="mt-4 text-red-600">
          ❌ Only 45% utilization - wasting space!
        </p>
      </section>

      {/* After */}
      <section>
        <h2 className="text-2xl font-bold mb-4">With KITT Optimization</h2>
        <TruckLoadingViewer
          packingData={afterData}
          height="400px"
        />
        <p className="mt-4 text-green-600">
          ✅ 82% utilization - save $50K/year!
        </p>
      </section>
    </div>
  )
}
```

## 🔧 Performance Tips

### 1. Use Dynamic Import for Better Loading

```tsx
// app/page.tsx
import dynamic from 'next/dynamic'

const TruckLoadingViewer = dynamic(
  () => import('@/components/TruckLoadingViewer'),
  { ssr: false, loading: () => <LoadingSpinner /> }
)
```

### 2. Optimize for Mobile

```tsx
'use client'

import { useEffect, useState } from 'react'

export default function ResponsiveViewer({ packingData }) {
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    setIsMobile(window.innerWidth < 768)
  }, [])

  return (
    <TruckLoadingViewer
      packingData={packingData}
      height={isMobile ? '300px' : '600px'}
      autoRotate={isMobile}  // Auto-rotate on mobile
    />
  )
}
```

### 3. Lazy Load for Better Performance

```tsx
'use client'

import { useInView } from 'react-intersection-observer'

export default function LazyVisualization() {
  const { ref, inView } = useInView({ triggerOnce: true })

  return (
    <div ref={ref} className="h-[600px]">
      {inView && <TruckLoadingViewer packingData={data} />}
    </div>
  )
}
```

## 🎨 Styling Options

### Dark Mode Support

```tsx
// Add to TruckLoadingViewer.tsx
const isDark = document.documentElement.classList.contains('dark')

<Canvas style={{ background: isDark ? '#1a1a1a' : '#f0f0f0' }}>
  {/* ... */}
</Canvas>
```

### Custom Overlay Styling

```tsx
// Modify StatsOverlay component
<div className="absolute top-4 left-4 bg-gradient-to-br from-blue-600 to-purple-600 text-white p-6 rounded-2xl shadow-2xl">
  {/* Your custom design */}
</div>
```

## 📦 Data Format

The component expects this JSON structure:

```typescript
{
  "container": {
    "dimensions": {
      "width": 589,
      "height": 235,
      "depth": 239
    },
    "type": "20ft_shipping_container"
  },
  "items": [
    {
      "item_id": "PALLET-001",
      "position": { "x": 0, "y": 0, "z": 0 },
      "dimensions": { "width": 120, "height": 100, "depth": 80 },
      "weight": 500,
      "rotation": 0
    }
  ],
  "stats": {
    "utilization": 11.62,
    "items_packed": 8,
    "total_weight_kg": 1935,
    "algorithm": "deeppack3d-bl",
    "computation_ms": 4
  }
}
```

## 🚀 Deployment

### Vercel (Recommended)

```bash
# Push to GitHub
git add .
git commit -m "Add 3D truck visualization"
git push

# Deploy to Vercel
vercel --prod
```

### Build Optimization

```javascript
// next.config.js
module.exports = {
  webpack: (config) => {
    config.externals.push({
      'three': 'three'
    })
    return config
  }
}
```

## 📸 Screenshots

The viewer includes:
- ✅ Interactive 3D boxes with hover effects
- ✅ Container wireframe outline
- ✅ Real-time stats overlay
- ✅ Smooth controls with damping
- ✅ Shadows and lighting
- ✅ Mobile touch support
- ✅ Auto-rotation option
- ✅ Responsive design

## 🔗 Live Demo

```bash
# Clone and run locally
git clone <your-repo>
cd your-nextjs-app
npm install
npm run dev
# Open http://localhost:3000
```

## 📝 Comparison

| Feature | React Three Fiber | Blender | PIL |
|---------|-------------------|---------|-----|
| Interactive | ✅ Yes | ❌ No | ❌ No |
| Real-time | ✅ 60fps | ❌ Static | ❌ Static |
| Setup | Easy | Complex | Easy |
| Quality | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Mobile | ✅ Yes | ⚠️ Image only | ⚠️ Image only |
| Backend | ❌ No | ✅ Yes | ✅ Yes |
| Best for | **Websites** | Print | Testing |

## ✅ Summary

**For a Next.js website, use React Three Fiber (this component)**:

- ✅ Easy integration with Next.js
- ✅ Interactive and engaging
- ✅ No backend rendering needed
- ✅ Mobile-friendly
- ✅ Modern and professional
- ✅ Fast loading (client-side)

**Installation**: `npm install three @react-three/fiber @react-three/drei`

**Usage**: Copy component → Import → Pass data → Done!

**Result**: Beautiful, interactive 3D visualization that runs smoothly in any browser.
