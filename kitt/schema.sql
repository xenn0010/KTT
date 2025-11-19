-- KITT Database Schema
-- SQLite Database for freight optimization system

-- Shipments table
CREATE TABLE IF NOT EXISTS shipments (
    id TEXT PRIMARY KEY,
    origin TEXT NOT NULL,
    destination TEXT NOT NULL,
    priority TEXT CHECK(priority IN ('low', 'medium', 'high', 'critical')) DEFAULT 'medium',
    status TEXT CHECK(status IN ('pending', 'optimizing', 'packed', 'in_transit', 'delivered', 'cancelled')) DEFAULT 'pending',
    deadline TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Items table
CREATE TABLE IF NOT EXISTS items (
    id TEXT PRIMARY KEY,
    shipment_id TEXT NOT NULL,
    width REAL NOT NULL CHECK(width > 0),
    height REAL NOT NULL CHECK(height > 0),
    depth REAL NOT NULL CHECK(depth > 0),
    weight REAL NOT NULL CHECK(weight > 0),
    fragile BOOLEAN DEFAULT FALSE,
    stackable BOOLEAN DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (shipment_id) REFERENCES shipments(id) ON DELETE CASCADE
);

-- Packing plans table
CREATE TABLE IF NOT EXISTS packing_plans (
    id TEXT PRIMARY KEY,
    shipment_id TEXT NOT NULL,
    truck_id TEXT NOT NULL,
    plan_data JSON NOT NULL,
    utilization REAL CHECK(utilization >= 0 AND utilization <= 100),
    risk_score REAL CHECK(risk_score >= 0 AND risk_score <= 100),
    algorithm_used TEXT,
    computation_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (shipment_id) REFERENCES shipments(id) ON DELETE CASCADE
);

-- Route analytics table
CREATE TABLE IF NOT EXISTS route_analytics (
    id TEXT PRIMARY KEY,
    route_id TEXT NOT NULL,
    origin TEXT NOT NULL,
    destination TEXT NOT NULL,
    distance_km REAL,
    duration_minutes INTEGER,
    weather_condition TEXT,
    weather_severity INTEGER CHECK(weather_severity >= 1 AND weather_severity <= 5),
    traffic_level TEXT CHECK(traffic_level IN ('low', 'medium', 'high', 'severe')),
    road_quality_score REAL CHECK(road_quality_score >= 0 AND road_quality_score <= 10),
    estimated_damage_risk REAL CHECK(estimated_damage_risk >= 0 AND estimated_damage_risk <= 100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trucks table
CREATE TABLE IF NOT EXISTS trucks (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    width REAL NOT NULL CHECK(width > 0),
    height REAL NOT NULL CHECK(height > 0),
    depth REAL NOT NULL CHECK(depth > 0),
    max_weight REAL NOT NULL CHECK(max_weight > 0),
    status TEXT CHECK(status IN ('available', 'in_use', 'maintenance', 'retired')) DEFAULT 'available',
    current_location TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Damage incidents table
CREATE TABLE IF NOT EXISTS damage_incidents (
    id TEXT PRIMARY KEY,
    shipment_id TEXT NOT NULL,
    route_id TEXT,
    incident_type TEXT NOT NULL,
    severity INTEGER CHECK(severity >= 1 AND severity <= 5),
    description TEXT,
    contributing_factors JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (shipment_id) REFERENCES shipments(id)
);

-- AI predictions table
CREATE TABLE IF NOT EXISTS ai_predictions (
    id TEXT PRIMARY KEY,
    shipment_id TEXT NOT NULL,
    prediction_type TEXT NOT NULL,
    model_version TEXT,
    prediction_data JSON NOT NULL,
    confidence REAL CHECK(confidence >= 0 AND confidence <= 1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (shipment_id) REFERENCES shipments(id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_shipments_status ON shipments(status);
CREATE INDEX IF NOT EXISTS idx_shipments_created_at ON shipments(created_at);
CREATE INDEX IF NOT EXISTS idx_items_shipment_id ON items(shipment_id);
CREATE INDEX IF NOT EXISTS idx_packing_plans_shipment_id ON packing_plans(shipment_id);
CREATE INDEX IF NOT EXISTS idx_route_analytics_route_id ON route_analytics(route_id);
CREATE INDEX IF NOT EXISTS idx_route_analytics_timestamp ON route_analytics(timestamp);
CREATE INDEX IF NOT EXISTS idx_trucks_status ON trucks(status);
CREATE INDEX IF NOT EXISTS idx_damage_incidents_shipment_id ON damage_incidents(shipment_id);
CREATE INDEX IF NOT EXISTS idx_ai_predictions_shipment_id ON ai_predictions(shipment_id);

-- Insert sample trucks for testing
INSERT OR IGNORE INTO trucks (id, name, width, height, depth, max_weight, status, current_location) VALUES
    ('TRK-001', 'Fleet Truck 1', 240, 120, 100, 5000, 'available', 'Chicago Warehouse'),
    ('TRK-002', 'Fleet Truck 2', 240, 120, 100, 5000, 'available', 'Dallas Warehouse'),
    ('TRK-003', 'Fleet Truck 3', 300, 150, 120, 7500, 'available', 'Chicago Warehouse'),
    ('TRK-004', 'Container Truck 1', 600, 240, 240, 20000, 'available', 'Port of LA');
