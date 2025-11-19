import type { AIStrategy, PackingPlan, RouteConditions, ShipmentRecord } from './types/kitt'

export const sampleShipments: ShipmentRecord[] = [
  {
    id: 'SH-DEMO-01',
    origin: 'Los Angeles',
    destination: 'New York',
    priority: 'high',
    status: 'packed',
  },
  {
    id: 'SH-DEMO-02',
    origin: 'Miami',
    destination: 'Chicago',
    priority: 'medium',
    status: 'pending',
  },
]

export const samplePacking: PackingPlan = {
  success: true,
  plan_id: 'PLAN-DEMO',
  utilization: 82.4,
  placements: [
    {
      item_id: 'PALLET-001',
      position: { x: 0, y: 0, z: 0 },
      dimensions: { width: 120, height: 110, depth: 80 },
    },
    {
      item_id: 'PALLET-002',
      position: { x: 130, y: 0, z: 0 },
      dimensions: { width: 100, height: 90, depth: 90 },
    },
    {
      item_id: 'CRATE-009',
      position: { x: 0, y: 0, z: 90 },
      dimensions: { width: 80, height: 80, depth: 120 },
    },
  ],
}

export const sampleAnalysis: AIStrategy = {
  loading_strategy: 'Stage heavy pallets near the cab, float fragile items on tier two racks.',
  special_handling_items: ['CRATE-009 requires foam harness', 'PALLET-002 strapped twice'],
  truck_selection_criteria: ['Floor sensors calibrated', 'Rear climate control engaged'],
}

export const sampleRoute: RouteConditions = {
  route_id: 'ROUTE-DEMO',
  origin: 'Los Angeles',
  destination: 'New York',
  current_traffic: { level: 'moderate', delay_minutes: 12 },
  road_quality: { score: 8.7, surface_condition: 'stable' },
  weather_severity: 1,
}
