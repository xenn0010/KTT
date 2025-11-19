# Next.js Visualization - The Easy & Beautiful Way

## 🎯 Best Solution for Next.js Websites

**React Three Fiber** - Interactive 3D visualization that's:
- ✅ **Easy to integrate** - Just 3 commands
- ✅ **Beautiful** - Smooth 3D rendering with shadows & lighting
- ✅ **Interactive** - Rotate, zoom, pan with mouse/touch
- ✅ **Fast** - 60fps performance in browser
- ✅ **Mobile-friendly** - Works on all devices
- ✅ **No backend needed** - Renders client-side

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies (30 seconds)

```bash
cd your-nextjs-app
npm install three @react-three/fiber @react-three/drei
```

### Step 2: Copy Component (10 seconds)

Copy `TruckLoadingViewer.tsx` to your components folder:

```
your-nextjs-app/
└── app/
    └── components/
        └── TruckLoadingViewer.tsx  ← Copy here
```

### Step 3: Use It (20 seconds)

```tsx
// app/page.tsx
'use client'

import TruckLoadingViewer from '@/components/TruckLoadingViewer'

export default function Page() {
  const packingData = {
    // Your packing data from API or DeepPack3D
  }

  return (
    <TruckLoadingViewer
      packingData={packingData}
      width="100%"
      height="600px"
    />
  )
}
```

**That's it!** You now have an interactive 3D visualization.

---

## 🎨 What You Get

### Visual Features

✅ **Interactive 3D Scene**
- Drag to rotate camera
- Scroll to zoom in/out
- Right-click to pan
- Touch gestures on mobile

✅ **Beautiful Materials**
- Metallic boxes with reflections
- Smooth shadows
- Professional lighting
- Color-coded items

✅ **Hover Effects**
- Boxes scale up on hover
- Show dimensions tooltip
- Highlight selected item

✅ **Stats Overlay**
- Container dimensions
- Items packed
- Utilization percentage
- Weight and algorithm info

✅ **Controls Guide**
- Built-in instructions
- Mouse/touch controls
- Auto-rotation option

---

## 📊 Comparison: React Three Fiber vs Blender

| Feature | React Three Fiber | Blender |
|---------|-------------------|---------|
| **Setup** | 3 npm packages | Install Blender |
| **Time to Implement** | 1 minute | 10 minutes |
| **Interactive** | ✅ Yes (rotate, zoom) | ❌ Static image |
| **Real-time** | ✅ 60fps | ❌ Pre-rendered |
| **Quality** | ⭐⭐⭐⭐ Very Good | ⭐⭐⭐⭐⭐ Excellent |
| **Mobile Support** | ✅ Native | ⚠️ Image only |
| **Backend Required** | ❌ No | ✅ Yes (rendering) |
| **File Size** | ~100KB JS | ~5MB PNG |
| **Loading Time** | Instant | Load image |
| **User Engagement** | ⭐⭐⭐⭐⭐ High | ⭐⭐⭐ Medium |
| **Best For** | **Websites** | Print/presentations |

---

## 💡 Why React Three Fiber for Next.js?

### 1. **Easy Integration**
```tsx
// Just import and use - no backend setup
import TruckLoadingViewer from '@/components/TruckLoadingViewer'

<TruckLoadingViewer packingData={data} />
```

### 2. **Better User Experience**
- Users can **interact** with the visualization
- Rotate to see all angles
- Zoom to see details
- Much more engaging than static images

### 3. **Faster Loading**
- No large image files to download
- Geometry loads as JSON (small)
- Renders on user's GPU
- Progressive loading

### 4. **Responsive Design**
```tsx
// Automatically adapts to screen size
<div className="w-full h-[300px] md:h-[600px]">
  <TruckLoadingViewer packingData={data} />
</div>
```

### 5. **Modern & Professional**
- Smooth animations
- Real-time shadows and lighting
- Looks cutting-edge
- Impresses clients

---

## 🎯 Use Cases

### 1. Landing Page Hero

```tsx
export default function HomePage() {
  return (
    <section className="h-screen bg-gradient-to-br from-blue-600 to-purple-600">
      <div className="container mx-auto py-20 text-white">
        <h1 className="text-6xl font-bold mb-4">
          Optimize Your Freight Loading
        </h1>
        <p className="text-2xl mb-8">
          Save 30% on fuel costs with AI-powered 3D packing
        </p>

        {/* Interactive 3D visualization */}
        <TruckLoadingViewer
          packingData={demoData}
          autoRotate={true}
          height="500px"
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
    <div className="grid grid-cols-2 gap-8">
      <div>
        <h2 className="text-2xl font-bold mb-4">Shipment #12345</h2>
        {/* Stats */}
      </div>

      <div>
        {/* Live 3D preview */}
        <TruckLoadingViewer packingData={shipment} height="400px" />
      </div>
    </div>
  )
}
```

### 3. Client Proposal (Before/After)

```tsx
export default function Proposal() {
  return (
    <div className="max-w-7xl mx-auto">
      {/* Before */}
      <section className="mb-12">
        <h2 className="text-3xl font-bold mb-4">Current State</h2>
        <TruckLoadingViewer packingData={beforeData} />
        <p className="text-red-600 text-xl mt-4">
          ❌ Only 45% utilization - wasting space!
        </p>
      </section>

      {/* After */}
      <section>
        <h2 className="text-3xl font-bold mb-4">With Our Solution</h2>
        <TruckLoadingViewer packingData={afterData} />
        <p className="text-green-600 text-xl mt-4">
          ✅ 82% utilization - save $50K/year!
        </p>
      </section>
    </div>
  )
}
```

---

## ⚙️ Customization

### Change Colors

```tsx
// In TruckLoadingViewer.tsx
const COLORS = [
  '#1e40af', // Navy blue
  '#0891b2', // Cyan
  '#16a34a', // Green
  '#ea580c', // Orange
]
```

### Auto-Rotation

```tsx
<TruckLoadingViewer
  packingData={data}
  autoRotate={true}  // ← Slowly rotates
/>
```

### Hide Stats

```tsx
<TruckLoadingViewer
  packingData={data}
  showStats={false}  // ← No overlay
/>
```

### Adjust Materials

```tsx
// In CargoBox component
<meshStandardMaterial
  metalness={0.8}  // ← More metallic (0-1)
  roughness={0.2}  // ← More shiny (0-1)
  opacity={0.9}    // ← More opaque (0-1)
/>
```

---

## 📱 Mobile Optimization

```tsx
'use client'

import { useEffect, useState } from 'react'

export default function ResponsiveViewer() {
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    setIsMobile(window.innerWidth < 768)
  }, [])

  return (
    <TruckLoadingViewer
      packingData={data}
      height={isMobile ? '300px' : '600px'}
      autoRotate={isMobile}  // Auto-rotate on mobile
    />
  )
}
```

---

## 🚀 Performance

### Bundle Size
- three.js: ~600KB (gzipped: ~150KB)
- @react-three/fiber: ~80KB (gzipped: ~25KB)
- @react-three/drei: ~100KB (gzipped: ~30KB)
- **Total: ~800KB (~200KB gzipped)**

### Loading Time
- First load: ~1 second
- Subsequent loads: Instant (cached)
- 3D rendering: 60fps smooth

### Optimization Tips

```tsx
// 1. Dynamic import (load only when needed)
import dynamic from 'next/dynamic'

const TruckLoadingViewer = dynamic(
  () => import('@/components/TruckLoadingViewer'),
  { ssr: false }
)

// 2. Lazy load (load when visible)
import { useInView } from 'react-intersection-observer'

export default function LazyViewer() {
  const { ref, inView } = useInView({ triggerOnce: true })

  return (
    <div ref={ref} className="h-[600px]">
      {inView && <TruckLoadingViewer packingData={data} />}
    </div>
  )
}
```

---

## 🔗 API Integration

### Fetch from Backend

```tsx
// app/page.tsx
'use client'

import { useEffect, useState } from 'react'
import TruckLoadingViewer from '@/components/TruckLoadingViewer'

export default function Page() {
  const [packingData, setPackingData] = useState(null)

  useEffect(() => {
    // Fetch from your API
    fetch('/api/truck-packing')
      .then(res => res.json())
      .then(data => setPackingData(data))
  }, [])

  if (!packingData) return <div>Loading...</div>

  return <TruckLoadingViewer packingData={packingData} />
}
```

### API Route Example

```typescript
// app/api/truck-packing/route.ts
import { NextResponse } from 'next/server'
import { exec } from 'child_process'
import { promisify } from 'util'
import fs from 'fs/promises'

const execAsync = promisify(exec)

export async function GET() {
  // Run DeepPack3D
  await execAsync('python3 /path/to/test_real_truck_packing.py')

  // Read result
  const data = await fs.readFile('/tmp/truck_loading_plan.json', 'utf-8')

  return NextResponse.json(JSON.parse(data))
}
```

---

## 📦 Complete Files

I've created:

1. **[TruckLoadingViewer.tsx](nextjs-visualization/TruckLoadingViewer.tsx)** - Main component (400 lines)
2. **[README.md](nextjs-visualization/README.md)** - Detailed documentation
3. **[example-page.tsx](nextjs-visualization/example-page.tsx)** - Complete demo page

---

## ✅ Summary

**For Next.js websites, use React Three Fiber:**

### Why?
- ✅ Easy setup (3 npm packages)
- ✅ Interactive & engaging
- ✅ Fast & smooth (60fps)
- ✅ Mobile-friendly
- ✅ No backend rendering
- ✅ Modern & professional

### Installation
```bash
npm install three @react-three/fiber @react-three/drei
```

### Usage
```tsx
<TruckLoadingViewer packingData={data} height="600px" />
```

### Result
Beautiful, interactive 3D visualization that:
- Rotates, zooms, pans
- Shows hover tooltips
- Displays real-time stats
- Works on all devices
- Impresses users

---

## 🎯 Quick Decision Matrix

**Choose React Three Fiber (Next.js) if:**
- ✅ Building a website
- ✅ Want interactivity
- ✅ Need mobile support
- ✅ Want easy integration
- ✅ Prefer client-side rendering

**Choose Blender if:**
- ✅ Creating print materials
- ✅ Need absolute best quality
- ✅ Making investor deck slides
- ✅ Don't need interactivity
- ✅ Want photorealistic renders

---

**For your Next.js website: React Three Fiber is the perfect choice!**

Fast, beautiful, interactive, and easy to integrate. 🚀
