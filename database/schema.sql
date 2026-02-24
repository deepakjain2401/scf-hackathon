-- Multi-Tier Supply Chain Fraud Detection Database Schema

-- Companies table (buyers and suppliers)
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    tier INTEGER NOT NULL CHECK (tier IN (0, 1, 2, 3)), -- 0 = buyer, 1-3 = suppliers
    industry VARCHAR(100),
    annual_revenue DECIMAL(15, 2),
    country VARCHAR(50),
    city VARCHAR(100),
    registration_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Lenders/Financial Institutions
CREATE TABLE lenders (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(50),
    lending_capacity DECIMAL(15, 2),
    interest_rate DECIMAL(5, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Buyer-Supplier relationships
CREATE TABLE relationships (
    id SERIAL PRIMARY KEY,
    buyer_id INTEGER REFERENCES companies(id),
    supplier_id INTEGER REFERENCES companies(id),
    relationship_type VARCHAR(50), -- 'direct', 'indirect', 'preferred', etc.
    start_date DATE,
    credit_limit DECIMAL(15, 2),
    payment_terms INTEGER, -- days
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Purchase Orders
CREATE TABLE purchase_orders (
    id SERIAL PRIMARY KEY,
    po_number VARCHAR(100) UNIQUE NOT NULL,
    buyer_id INTEGER REFERENCES companies(id),
    supplier_id INTEGER REFERENCES companies(id),
    amount DECIMAL(15, 2) NOT NULL,
    quantity INTEGER,
    description TEXT,
    po_date DATE NOT NULL,
    expected_delivery_date DATE,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'confirmed', 'delivered', 'cancelled'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Good Receipt Notes
CREATE TABLE grns (
    id SERIAL PRIMARY KEY,
    grn_number VARCHAR(100) UNIQUE NOT NULL,
    po_id INTEGER REFERENCES purchase_orders(id),
    quantity_received INTEGER,
    quality_status VARCHAR(20), -- 'approved', 'rejected', 'partial'
    received_date DATE,
    received_by VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Invoices
CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,
    invoice_number VARCHAR(100) UNIQUE NOT NULL,
    po_id INTEGER REFERENCES purchase_orders(id), -- Can be NULL for phantom invoices
    supplier_id INTEGER REFERENCES companies(id),
    lender_id INTEGER REFERENCES lenders(id),
    amount DECIMAL(15, 2) NOT NULL,
    invoice_date DATE NOT NULL,
    due_date DATE,
    description TEXT,
    invoice_fingerprint VARCHAR(64), -- Hash for duplicate detection
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'approved', 'paid', 'disputed'
    is_fraudulent BOOLEAN DEFAULT FALSE, -- For training/testing
    fraud_type VARCHAR(50), -- 'phantom', 'duplicate', 'over_invoice', 'carousel', 'dilution'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Payments
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    payment_number VARCHAR(100) UNIQUE NOT NULL,
    invoice_id INTEGER REFERENCES invoices(id),
    amount DECIMAL(15, 2) NOT NULL,
    payment_date DATE,
    payment_method VARCHAR(50),
    collection_rate DECIMAL(5, 4), -- Percentage of invoice amount collected
    days_overdue INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fraud detection alerts
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    alert_type VARCHAR(50) NOT NULL, -- 'phantom_invoice', 'duplicate', 'over_invoice', 'carousel', 'velocity', 'dilution'
    severity VARCHAR(10) NOT NULL, -- 'low', 'medium', 'high', 'critical'
    entity_type VARCHAR(20), -- 'invoice', 'company', 'relationship'
    entity_id INTEGER,
    description TEXT,
    fraud_score DECIMAL(5, 4),
    investigation_status VARCHAR(20) DEFAULT 'open', -- 'open', 'investigating', 'confirmed', 'false_positive', 'closed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- Invoice processing log (for velocity analysis)
CREATE TABLE invoice_processing_log (
    id SERIAL PRIMARY KEY,
    invoice_id INTEGER REFERENCES invoices(id),
    processing_stage VARCHAR(50), -- 'submitted', 'validated', 'approved', 'disbursed'
    processing_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_duration INTEGER, -- milliseconds
    fraud_checks_passed INTEGER,
    fraud_checks_failed INTEGER
);

-- Carousel detection tracking
CREATE TABLE carousel_patterns (
    id SERIAL PRIMARY KEY,
    pattern_id VARCHAR(100),
    companies_involved TEXT, -- JSON array of company IDs
    transaction_flow TEXT, -- JSON representation of the circular flow
    total_amount DECIMAL(15, 2),
    detection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confidence_score DECIMAL(5, 4)
);

-- Indexes for performance
CREATE INDEX idx_companies_tier ON companies(tier);
CREATE INDEX idx_invoices_supplier_date ON invoices(supplier_id, invoice_date);
CREATE INDEX idx_invoices_fingerprint ON invoices(invoice_fingerprint);
CREATE INDEX idx_payments_invoice_date ON payments(invoice_id, payment_date);
CREATE INDEX idx_alerts_type_severity ON alerts(alert_type, severity);
CREATE INDEX idx_po_buyer_supplier ON purchase_orders(buyer_id, supplier_id);
CREATE INDEX idx_relationships_buyer_supplier ON relationships(buyer_id, supplier_id);

-- Views for analysis
CREATE VIEW v_invoice_summary AS
SELECT 
    i.id,
    i.invoice_number,
    i.amount,
    i.invoice_date,
    c.name as supplier_name,
    c.tier as supplier_tier,
    l.name as lender_name,
    po.po_number,
    po.amount as po_amount,
    grn.grn_number,
    i.is_fraudulent,
    i.fraud_type,
    p.amount as paid_amount,
    p.collection_rate
FROM invoices i
LEFT JOIN companies c ON i.supplier_id = c.id
LEFT JOIN lenders l ON i.lender_id = l.id
LEFT JOIN purchase_orders po ON i.po_id = po.id
LEFT JOIN grns grn ON po.id = grn.po_id
LEFT JOIN payments p ON i.id = p.invoice_id;

CREATE VIEW v_supplier_metrics AS
SELECT 
    c.id,
    c.name,
    c.tier,
    c.annual_revenue,
    COUNT(i.id) as invoice_count,
    SUM(i.amount) as total_invoice_amount,
    AVG(i.amount) as avg_invoice_amount,
    COUNT(CASE WHEN i.is_fraudulent THEN 1 END) as fraud_count,
    (COUNT(CASE WHEN i.is_fraudulent THEN 1 END)::float / COUNT(i.id)) as fraud_rate
FROM companies c
LEFT JOIN invoices i ON c.id = i.supplier_id
WHERE c.tier > 0
GROUP BY c.id, c.name, c.tier, c.annual_revenue;