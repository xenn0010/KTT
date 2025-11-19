export type ShipmentRecord = {
  id: string
  origin: string
  destination: string
  priority?: string
  status?: string
  created_at?: string
}

export type Placement = {
  item_id: string
  position: { x: number; y: number; z: number }
  dimensions: { width: number; height: number; depth: number }
  bin_number?: number
  rotation?: number
}

export type PackingPlan = {
  success?: boolean
  plan_id?: string
  truck_id?: string
  utilization?: number
  utilization_percentage?: number
  items_packed?: number
  packing_method?: string
  placements: Placement[]
  bins_used?: number
}

export type AIStrategy = {
  loading_strategy?: string
  special_handling_items?: string[]
  truck_selection_criteria?: string[]
}

export type RouteConditions = {
  route_id?: string
  origin?: string
  destination?: string
  current_weather?: Record<string, unknown>
  destination_weather?: Record<string, unknown>
  weather_severity?: number
  current_traffic?: { level?: string; delay_minutes?: number }
  road_quality?: { score?: number; surface_condition?: string }
}

export type OptimizeResponse = {
  shipment_id: string
  packing?: PackingPlan
  route_conditions?: RouteConditions
  ai_analysis?: AIStrategy
  risk_assessment?: Record<string, unknown>
  summary?: Record<string, unknown>
}
