/**
 * Example Next.js Page using TruckLoadingViewer
 * Shows how to integrate the 3D visualization in a real page
 */

'use client'

import { useEffect, useState } from 'react'
import TruckLoadingViewer from '@/components/TruckLoadingViewer'

// Sample packing data (you'd fetch this from your API)
const SAMPLE_DATA = {
  container: {
    dimensions: { width: 589, height: 235, depth: 239 },
    type: '20ft_shipping_container'
  },
  items: [
    {
      item_id: 'PALLET-001',
      position: { x: 0, y: 0, z: 0 },
      dimensions: { width: 120, height: 100, depth: 80 },
      weight: 500
    },
    {
      item_id: 'PALLET-002',
      position: { x: 120, y: 0, z: 0 },
      dimensions: { width: 120, height: 100, depth: 80 },
      weight: 450
    },
    {
      item_id: 'PALLET-003',
      position: { x: 240, y: 0, z: 0 },
      dimensions: { width: 120, height: 100, depth: 80 },
      weight: 480
    },
    {
      item_id: 'CRATE-001',
      position: { x: 0, y: 100, z: 0 },
      dimensions: { width: 100, height: 80, depth: 60 },
      weight: 200
    },
    {
      item_id: 'CRATE-002',
      position: { x: 100, y: 100, z: 0 },
      dimensions: { width: 100, height: 80, depth: 60 },
      weight: 180
    },
    {
      item_id: 'BOX-001',
      position: { x: 0, y: 0, z: 80 },
      dimensions: { width: 60, height: 50, depth: 40 },
      weight: 50
    },
    {
      item_id: 'BOX-002',
      position: { x: 60, y: 0, z: 80 },
      dimensions: { width: 60, height: 50, depth: 40 },
      weight: 45
    },
    {
      item_id: 'BOX-003',
      position: { x: 120, y: 0, z: 80 },
      dimensions: { width: 50, height: 40, depth: 30 },
      weight: 30
    }
  ],
  stats: {
    utilization: 11.62,
    items_packed: 8,
    total_weight_kg: 1935,
    algorithm: 'deeppack3d-bl',
    computation_ms: 4
  }
}

export default function TruckVisualizationPage() {
  const [packingData, setPackingData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [autoRotate, setAutoRotate] = useState(false)

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setPackingData(SAMPLE_DATA)
      setLoading(false)
    }, 500)

    // Or fetch from real API:
    // fetch('/api/truck-packing')
    //   .then(res => res.json())
    //   .then(data => {
    //     setPackingData(data)
    //     setLoading(false)
    //   })
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading truck optimization...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-4xl font-bold text-gray-900">
            🚚 Truck Loading Optimization
          </h1>
          <p className="mt-2 text-lg text-gray-600">
            AI-powered 3D bin packing visualization
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Controls */}
        <div className="mb-6 flex gap-4">
          <button
            onClick={() => setAutoRotate(!autoRotate)}
            className={`px-6 py-3 rounded-lg font-semibold transition-colors ${
              autoRotate
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-white text-blue-600 border-2 border-blue-600 hover:bg-blue-50'
            }`}
          >
            {autoRotate ? '⏸️ Stop Rotation' : '▶️ Auto Rotate'}
          </button>

          <button
            onClick={() => window.location.reload()}
            className="px-6 py-3 bg-white text-gray-700 border-2 border-gray-300 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
          >
            🔄 Reload
          </button>
        </div>

        {/* 3D Visualization */}
        <div className="bg-white rounded-2xl shadow-2xl overflow-hidden">
          <TruckLoadingViewer
            packingData={packingData}
            width="100%"
            height="600px"
            showStats={true}
            autoRotate={autoRotate}
          />
        </div>

        {/* Item List */}
        <div className="mt-12 bg-white rounded-2xl shadow-xl p-8">
          <h2 className="text-2xl font-bold mb-6 text-gray-900">
            📦 Loaded Items
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {packingData.items.map((item, index) => (
              <div
                key={item.item_id}
                className="border-2 border-gray-200 rounded-lg p-4 hover:border-blue-400 hover:shadow-md transition-all"
              >
                <div className="flex items-center gap-3 mb-2">
                  <div
                    className="w-6 h-6 rounded"
                    style={{ backgroundColor: ['#ff6666', '#66ff66', '#6666ff', '#ffff66', '#ff66ff', '#66ffff', '#ff9966', '#9966ff'][index % 8] }}
                  />
                  <h3 className="font-bold text-gray-900">{item.item_id}</h3>
                </div>

                <div className="text-sm text-gray-600 space-y-1">
                  <div>
                    📏 {item.dimensions.width}×{item.dimensions.height}×{item.dimensions.depth} cm
                  </div>
                  <div>
                    📍 Position: ({item.position.x.toFixed(0)}, {item.position.y.toFixed(0)}, {item.position.z.toFixed(0)})
                  </div>
                  {item.weight && <div>⚖️ {item.weight} kg</div>}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Metrics */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-xl p-6 shadow-lg">
            <div className="text-3xl font-bold mb-2">
              {packingData.stats.utilization.toFixed(1)}%
            </div>
            <div className="text-blue-100">Space Utilization</div>
          </div>

          <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-xl p-6 shadow-lg">
            <div className="text-3xl font-bold mb-2">
              {packingData.stats.items_packed}
            </div>
            <div className="text-green-100">Items Packed</div>
          </div>

          <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-xl p-6 shadow-lg">
            <div className="text-3xl font-bold mb-2">
              {packingData.stats.total_weight_kg}kg
            </div>
            <div className="text-purple-100">Total Weight</div>
          </div>

          <div className="bg-gradient-to-br from-orange-500 to-orange-600 text-white rounded-xl p-6 shadow-lg">
            <div className="text-3xl font-bold mb-2">
              {packingData.stats.computation_ms}ms
            </div>
            <div className="text-orange-100">Computation Time</div>
          </div>
        </div>

        {/* Features */}
        <div className="mt-12 bg-gradient-to-br from-indigo-600 to-purple-600 text-white rounded-2xl p-8 shadow-xl">
          <h2 className="text-3xl font-bold mb-6">✨ Features</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex gap-4">
              <div className="text-3xl">🎯</div>
              <div>
                <h3 className="font-bold text-lg mb-1">Optimal Packing</h3>
                <p className="text-indigo-100">
                  DeepPack3D algorithm finds the best arrangement in milliseconds
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="text-3xl">💰</div>
              <div>
                <h3 className="font-bold text-lg mb-1">Cost Savings</h3>
                <p className="text-indigo-100">
                  Maximize space utilization to reduce fuel costs and trips
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="text-3xl">⚡</div>
              <div>
                <h3 className="font-bold text-lg mb-1">Real-time Visualization</h3>
                <p className="text-indigo-100">
                  Interactive 3D view with smooth 60fps rendering
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="text-3xl">📱</div>
              <div>
                <h3 className="font-bold text-lg mb-1">Mobile Friendly</h3>
                <p className="text-indigo-100">
                  Works perfectly on desktop, tablet, and mobile devices
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 text-center text-gray-600">
          <p>Powered by DeepPack3D + React Three Fiber</p>
          <p className="mt-2 text-sm">
            Interactive 3D visualization for modern freight optimization
          </p>
        </div>
      </footer>
    </div>
  )
}
