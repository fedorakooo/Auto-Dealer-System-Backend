CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TYPE user_role AS ENUM ('customer', 'employee', 'admin');
CREATE TYPE fuel_type AS ENUM ('gasoline', 'diesel', 'electric', 'hybrid', 'lpg');
CREATE TYPE transmission_type AS ENUM ('automatic', 'manual', 'cvt', 'dct');
CREATE TYPE drive_type AS ENUM ('FWD', 'RWD', 'AWD');
CREATE TYPE order_status AS ENUM ('pending_payment', 'processing', 'ready_for_pickup', 'completed', 'cancelled');
CREATE TYPE custom_order_status AS ENUM ('pending_approval', 'confirmed', 'sent_to_factory', 'in_production', 'shipped', 'delivered', 'cancelled');
CREATE TYPE media_type AS ENUM ('image', 'video');
CREATE TYPE test_drive_status AS ENUM ('requested', 'confirmed', 'completed', 'cancelled');
CREATE TYPE employment_status AS ENUM ('active', 'vacation', 'suspended', 'dismissed');
CREATE TYPE vehicle_lifecycle_status AS ENUM ('in_stock', 'reserved', 'sold', 'service', 'unavailable');
CREATE TYPE payment_method AS ENUM ('cash', 'bank_card', 'bank_transfer', 'loan', 'lease');
CREATE TYPE payment_status AS ENUM ('pending', 'authorized', 'paid', 'failed', 'refunded');
CREATE TYPE service_appointment_status AS ENUM ('requested', 'confirmed', 'in_progress', 'completed', 'cancelled');
CREATE TYPE service_order_status AS ENUM ('opened', 'diagnosis', 'in_progress', 'waiting_parts', 'completed', 'cancelled');
CREATE TYPE outbox_event_status AS ENUM ('pending', 'processing', 'published', 'failed');

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    second_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role user_role NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ
);

CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date_of_birth DATE
);

CREATE TABLE cities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(255) NOT NULL,
    UNIQUE (name, country)
);

CREATE TABLE dealerships (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(512) NOT NULL,
    city_id INTEGER NOT NULL REFERENCES cities(id),
    phone_number VARCHAR(20),
    email VARCHAR(255) UNIQUE,
    opening_hours VARCHAR(255),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    is_active BOOLEAN NOT NULL DEFAULT true,
    updated_at TIMESTAMPTZ
);

CREATE TABLE body_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE engines (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    engine_code VARCHAR(100) UNIQUE,
    displacement_cm3 INTEGER,
    cylinders INTEGER,
    horsepower INTEGER,
    horsepower_electric INTEGER,
    torque_nm INTEGER,
    fuel_type fuel_type NOT NULL,
    configuration VARCHAR,
    induction VARCHAR,
    description TEXT
);

CREATE TABLE transmissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    type transmission_type NOT NULL,
    number_of_gears INTEGER NOT NULL,
    description TEXT
);

CREATE TABLE models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    body_type_id INTEGER NOT NULL REFERENCES body_types(id),
    engine_id INTEGER NOT NULL REFERENCES engines(id),
    transmission_id INTEGER NOT NULL REFERENCES transmissions(id),
    name VARCHAR(100) NOT NULL,
    model_code VARCHAR(100),
    is_in_production BOOLEAN,
    production_year_start INTEGER NOT NULL,
    production_year_end INTEGER,
    description TEXT,
    drive_type drive_type,
    max_speed_kmh INTEGER,
    acceleration_0_100_sec DECIMAL(3,1),
    fuel_tank_capacity_l INTEGER,
    number_of_seats INTEGER,
    number_of_doors INTEGER,
    length_mm INTEGER,
    width_mm INTEGER,
    height_mm INTEGER,
    curb_weight_kg INTEGER,
    gross_weight_kg INTEGER,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ,
    UNIQUE (name, production_year_start)
);

CREATE TABLE features (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE model_features (
    model_id UUID NOT NULL REFERENCES models(id) ON DELETE CASCADE,
    feature_id INTEGER NOT NULL REFERENCES features(id) ON DELETE CASCADE,
    PRIMARY KEY (model_id, feature_id)
);

CREATE TABLE vehicles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID NOT NULL REFERENCES models(id),
    dealership_id INTEGER NOT NULL REFERENCES dealerships(id),
    vin VARCHAR(17) UNIQUE NOT NULL,
    production_year INTEGER NOT NULL,
    exterior_color VARCHAR(50) NOT NULL,
    interior_color VARCHAR(50),
    price DECIMAL(12, 2) NOT NULL CHECK (price > 0),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ
);

CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    vehicle_id UUID UNIQUE NOT NULL REFERENCES vehicles(id),
    dealership_id INTEGER NOT NULL REFERENCES dealerships(id),
    status order_status NOT NULL DEFAULT 'pending_payment',
    final_price DECIMAL(12, 2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ
);

CREATE TABLE custom_orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    dealership_id INTEGER NOT NULL REFERENCES dealerships(id),
    model_id UUID NOT NULL REFERENCES models(id),
    engine_id INTEGER NOT NULL REFERENCES engines(id),
    transmission_id INTEGER NOT NULL REFERENCES transmissions(id),
    exterior_color VARCHAR(50) NOT NULL,
    interior_color VARCHAR(50),
    status custom_order_status NOT NULL DEFAULT 'pending_approval',
    estimated_price DECIMAL(12, 2),
    final_price DECIMAL(12, 2),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ
);

CREATE TABLE custom_order_features (
    custom_order_id UUID NOT NULL REFERENCES custom_orders(id) ON DELETE CASCADE,
    feature_id INTEGER NOT NULL REFERENCES features(id) ON DELETE CASCADE,
    PRIMARY KEY (custom_order_id, feature_id)
);

CREATE TABLE vehicle_media (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    url VARCHAR(512) NOT NULL,
    media_type media_type NOT NULL,
    description TEXT,
    sort_order INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ
);

CREATE TABLE model_media (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID NOT NULL REFERENCES models(id) ON DELETE CASCADE,
    url VARCHAR(512) NOT NULL,
    media_type media_type NOT NULL,
    description TEXT,
    sort_order INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ
);

CREATE TABLE favorites (
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    PRIMARY KEY (customer_id, vehicle_id)
);

CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    model_id UUID NOT NULL REFERENCES models(id),
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(255),
    comment TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ
);

CREATE TABLE test_drive_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id),
    dealership_id INTEGER NOT NULL REFERENCES dealerships(id),
    requested_datetime TIMESTAMPTZ NOT NULL,
    status test_drive_status NOT NULL DEFAULT 'requested',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ
);

CREATE TABLE employee_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    dealership_id INTEGER NOT NULL REFERENCES dealerships(id),
    position VARCHAR(100) NOT NULL,
    hire_date DATE NOT NULL,
    dismissal_date DATE,
    status employment_status NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ,
    CHECK (dismissal_date IS NULL OR dismissal_date >= hire_date)
);

CREATE TABLE customer_addresses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    label VARCHAR(50) NOT NULL,
    country VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    address_line_1 VARCHAR(255) NOT NULL,
    address_line_2 VARCHAR(255),
    postal_code VARCHAR(20),
    is_default BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ,
    UNIQUE (customer_id, label)
);

CREATE TABLE vehicle_status_history (
    id BIGSERIAL PRIMARY KEY,
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    status vehicle_lifecycle_status NOT NULL,
    reason TEXT,
    changed_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE vehicle_price_history (
    id BIGSERIAL PRIMARY KEY,
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    price DECIMAL(12, 2) NOT NULL CHECK (price > 0),
    valid_from TIMESTAMPTZ NOT NULL DEFAULT now(),
    valid_to TIMESTAMPTZ,
    changed_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    CHECK (valid_to IS NULL OR valid_to > valid_from)
);

CREATE TABLE order_payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    amount DECIMAL(12, 2) NOT NULL CHECK (amount > 0),
    method payment_method NOT NULL,
    status payment_status NOT NULL DEFAULT 'pending',
    external_reference VARCHAR(255) UNIQUE,
    paid_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ
);

CREATE TABLE order_status_history (
    id BIGSERIAL PRIMARY KEY,
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    from_status order_status,
    to_status order_status NOT NULL,
    changed_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    comment TEXT,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE test_drive_status_history (
    id BIGSERIAL PRIMARY KEY,
    test_drive_request_id UUID NOT NULL REFERENCES test_drive_requests(id) ON DELETE CASCADE,
    from_status test_drive_status,
    to_status test_drive_status NOT NULL,
    changed_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    comment TEXT,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE service_catalog (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) UNIQUE NOT NULL,
    description TEXT,
    base_price DECIMAL(12, 2) NOT NULL CHECK (base_price >= 0),
    estimated_minutes INTEGER NOT NULL CHECK (estimated_minutes > 0),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ
);

CREATE TABLE service_appointments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    dealership_id INTEGER NOT NULL REFERENCES dealerships(id),
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE SET NULL,
    requested_datetime TIMESTAMPTZ NOT NULL,
    status service_appointment_status NOT NULL DEFAULT 'requested',
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ
);

CREATE TABLE service_orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    appointment_id UUID UNIQUE REFERENCES service_appointments(id) ON DELETE SET NULL,
    customer_id UUID NOT NULL REFERENCES customers(id),
    dealership_id INTEGER NOT NULL REFERENCES dealerships(id),
    vehicle_id UUID NOT NULL REFERENCES vehicles(id),
    assigned_employee_id UUID REFERENCES employee_profiles(id) ON DELETE SET NULL,
    status service_order_status NOT NULL DEFAULT 'opened',
    odometer_km INTEGER CHECK (odometer_km IS NULL OR odometer_km >= 0),
    total_price DECIMAL(12, 2) NOT NULL DEFAULT 0 CHECK (total_price >= 0),
    opened_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    closed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ,
    CHECK (closed_at IS NULL OR closed_at >= opened_at)
);

CREATE TABLE service_order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_order_id UUID NOT NULL REFERENCES service_orders(id) ON DELETE CASCADE,
    service_id INTEGER REFERENCES service_catalog(id) ON DELETE SET NULL,
    description VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    unit_price DECIMAL(12, 2) NOT NULL CHECK (unit_price >= 0),
    line_total DECIMAL(12, 2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE spare_parts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sku VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    manufacturer VARCHAR(150),
    unit_price DECIMAL(12, 2) NOT NULL CHECK (unit_price >= 0),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ
);

CREATE TABLE dealership_part_inventory (
    dealership_id INTEGER NOT NULL REFERENCES dealerships(id) ON DELETE CASCADE,
    part_id UUID NOT NULL REFERENCES spare_parts(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    reserved_quantity INTEGER NOT NULL DEFAULT 0 CHECK (reserved_quantity >= 0),
    reorder_level INTEGER NOT NULL DEFAULT 0 CHECK (reorder_level >= 0),
    updated_at TIMESTAMPTZ,
    PRIMARY KEY (dealership_id, part_id),
    CHECK (reserved_quantity <= quantity)
);

CREATE TABLE outbox_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    aggregate_type VARCHAR(100) NOT NULL,
    aggregate_id VARCHAR(100) NOT NULL,
    event_type VARCHAR(150) NOT NULL,
    payload JSONB NOT NULL,
    status outbox_event_status NOT NULL DEFAULT 'pending',
    attempts INTEGER NOT NULL DEFAULT 0 CHECK (attempts >= 0),
    available_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    published_at TIMESTAMPTZ,
    last_error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE idempotency_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    idempotency_key VARCHAR(255) UNIQUE NOT NULL,
    request_method VARCHAR(10) NOT NULL,
    request_path VARCHAR(512) NOT NULL,
    request_hash VARCHAR(128) NOT NULL,
    response_status INTEGER,
    response_body JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL,
    CHECK (expires_at > created_at)
);

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_dealerships_updated_at BEFORE UPDATE ON dealerships FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_models_updated_at BEFORE UPDATE ON models FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_vehicles_updated_at BEFORE UPDATE ON vehicles FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_orders_updated_at BEFORE UPDATE ON orders FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_custom_orders_updated_at BEFORE UPDATE ON custom_orders FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_vehicle_media_updated_at BEFORE UPDATE ON vehicle_media FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_model_media_updated_at BEFORE UPDATE ON model_media FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_reviews_updated_at BEFORE UPDATE ON reviews FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_test_drive_requests_updated_at BEFORE UPDATE ON test_drive_requests FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_employee_profiles_updated_at BEFORE UPDATE ON employee_profiles FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_customer_addresses_updated_at BEFORE UPDATE ON customer_addresses FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_order_payments_updated_at BEFORE UPDATE ON order_payments FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_service_catalog_updated_at BEFORE UPDATE ON service_catalog FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_service_appointments_updated_at BEFORE UPDATE ON service_appointments FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_service_orders_updated_at BEFORE UPDATE ON service_orders FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_spare_parts_updated_at BEFORE UPDATE ON spare_parts FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_dealership_part_inventory_updated_at BEFORE UPDATE ON dealership_part_inventory FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE FUNCTION record_vehicle_price_history()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.price IS DISTINCT FROM OLD.price THEN
        UPDATE vehicle_price_history
        SET valid_to = now()
        WHERE vehicle_id = NEW.id AND valid_to IS NULL;
        INSERT INTO vehicle_price_history(vehicle_id, price, valid_from)
        VALUES (NEW.id, NEW.price, now());
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_vehicle_price_history
AFTER UPDATE OF price ON vehicles
FOR EACH ROW EXECUTE FUNCTION record_vehicle_price_history();

CREATE OR REPLACE FUNCTION record_order_status_history()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status IS DISTINCT FROM OLD.status THEN
        INSERT INTO order_status_history(order_id, from_status, to_status)
        VALUES (NEW.id, OLD.status, NEW.status);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_order_status_history
AFTER UPDATE OF status ON orders
FOR EACH ROW EXECUTE FUNCTION record_order_status_history();

CREATE OR REPLACE FUNCTION record_test_drive_status_history()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status IS DISTINCT FROM OLD.status THEN
        INSERT INTO test_drive_status_history(test_drive_request_id, from_status, to_status)
        VALUES (NEW.id, OLD.status, NEW.status);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_test_drive_status_history
AFTER UPDATE OF status ON test_drive_requests
FOR EACH ROW EXECUTE FUNCTION record_test_drive_status_history();

CREATE OR REPLACE FUNCTION enforce_order_payment_total()
RETURNS TRIGGER AS $$
DECLARE
    order_total DECIMAL(12, 2);
    paid_total DECIMAL(12, 2);
BEGIN
    SELECT final_price INTO order_total FROM orders WHERE id = NEW.order_id FOR UPDATE;
    SELECT COALESCE(SUM(amount), 0) INTO paid_total
    FROM order_payments
    WHERE order_id = NEW.order_id AND status IN ('authorized', 'paid')
      AND id IS DISTINCT FROM NEW.id;
    IF NEW.status IN ('authorized', 'paid') AND paid_total + NEW.amount > order_total THEN
        RAISE EXCEPTION 'payment total exceeds order final price';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_order_payment_total
BEFORE INSERT OR UPDATE OF amount, status ON order_payments
FOR EACH ROW EXECUTE FUNCTION enforce_order_payment_total();

CREATE OR REPLACE FUNCTION refresh_service_order_total()
RETURNS TRIGGER AS $$
DECLARE
    target_order_id UUID;
BEGIN
    target_order_id := COALESCE(NEW.service_order_id, OLD.service_order_id);
    UPDATE service_orders
    SET total_price = COALESCE((
        SELECT SUM(line_total) FROM service_order_items WHERE service_order_id = target_order_id
    ), 0)
    WHERE id = target_order_id;
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_service_order_total
AFTER INSERT OR UPDATE OR DELETE ON service_order_items
FOR EACH ROW EXECUTE FUNCTION refresh_service_order_total();

INSERT INTO vehicle_price_history(vehicle_id, price, valid_from)
SELECT v.id, v.price, COALESCE(v.created_at, now())
FROM vehicles v
WHERE NOT EXISTS (SELECT 1 FROM vehicle_price_history h WHERE h.vehicle_id = v.id);

INSERT INTO vehicle_status_history(vehicle_id, status, reason, changed_at)
SELECT v.id,
       CASE
           WHEN EXISTS (SELECT 1 FROM orders o WHERE o.vehicle_id = v.id AND o.status = 'completed')
               THEN 'sold'::vehicle_lifecycle_status
           WHEN EXISTS (SELECT 1 FROM orders o WHERE o.vehicle_id = v.id AND o.status <> 'cancelled')
               THEN 'reserved'::vehicle_lifecycle_status
           WHEN v.is_active THEN 'in_stock'::vehicle_lifecycle_status
           ELSE 'unavailable'::vehicle_lifecycle_status
       END,
       'Initial migration backfill', COALESCE(v.created_at, now())
FROM vehicles v
WHERE NOT EXISTS (SELECT 1 FROM vehicle_status_history h WHERE h.vehicle_id = v.id);

INSERT INTO order_status_history(order_id, from_status, to_status, comment, changed_at)
SELECT o.id, NULL, o.status, 'Initial migration backfill', COALESCE(o.created_at, now())
FROM orders o
WHERE NOT EXISTS (SELECT 1 FROM order_status_history h WHERE h.order_id = o.id);

INSERT INTO test_drive_status_history(test_drive_request_id, from_status, to_status, comment, changed_at)
SELECT t.id, NULL, t.status, 'Initial migration backfill', COALESCE(t.created_at, now())
FROM test_drive_requests t
WHERE NOT EXISTS (
    SELECT 1 FROM test_drive_status_history h WHERE h.test_drive_request_id = t.id
);

INSERT INTO service_catalog(name, description, base_price, estimated_minutes)
VALUES
    ('Диагностика автомобиля', 'Комплексная компьютерная диагностика', 80.00, 60),
    ('Замена моторного масла', 'Замена масла и масляного фильтра', 60.00, 45),
    ('Сезонная замена шин', 'Замена комплекта шин с балансировкой', 100.00, 90)
ON CONFLICT (name) DO NOTHING;

INSERT INTO spare_parts(sku, name, manufacturer, unit_price)
VALUES
    ('OIL-FILTER-001', 'Масляный фильтр', 'OEM', 20.00),
    ('BRAKE-PAD-001', 'Комплект тормозных колодок', 'OEM', 120.00),
    ('CABIN-FILTER-001', 'Салонный фильтр', 'OEM', 25.00)
ON CONFLICT (sku) DO NOTHING;

INSERT INTO dealership_part_inventory(dealership_id, part_id, quantity, reserved_quantity, reorder_level)
SELECT d.id, p.id, 10, 0, 3
FROM dealerships d CROSS JOIN spare_parts p
WHERE p.sku IN ('OIL-FILTER-001', 'BRAKE-PAD-001', 'CABIN-FILTER-001')
ON CONFLICT (dealership_id, part_id) DO NOTHING;

CREATE INDEX idx_customers_user_id ON customers(user_id);
CREATE INDEX idx_dealerships_city_id ON dealerships(city_id);
CREATE INDEX idx_models_body_type_id ON models(body_type_id);
CREATE INDEX idx_models_engine_id ON models(engine_id);
CREATE INDEX idx_models_transmission_id ON models(transmission_id);
CREATE INDEX idx_vehicles_model_id ON vehicles(model_id);
CREATE INDEX idx_vehicles_dealership_id ON vehicles(dealership_id);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_dealership_id ON orders(dealership_id);
CREATE INDEX idx_custom_orders_customer_id ON custom_orders(customer_id);
CREATE INDEX idx_custom_orders_model_id ON custom_orders(model_id);
CREATE INDEX idx_reviews_customer_id ON reviews(customer_id);
CREATE INDEX idx_reviews_model_id ON reviews(model_id);
CREATE INDEX idx_test_drive_requests_customer_id ON test_drive_requests(customer_id);
CREATE INDEX idx_test_drive_requests_vehicle_id ON test_drive_requests(vehicle_id);
CREATE INDEX idx_vehicle_media_vehicle_id ON vehicle_media(vehicle_id);
CREATE INDEX idx_model_media_model_id ON model_media(model_id);
CREATE INDEX idx_employee_profiles_dealership_id ON employee_profiles(dealership_id);
CREATE INDEX idx_customer_addresses_customer_id ON customer_addresses(customer_id);
CREATE UNIQUE INDEX uq_customer_addresses_default ON customer_addresses(customer_id) WHERE is_default;
CREATE INDEX idx_vehicle_status_history_vehicle_changed_at ON vehicle_status_history(vehicle_id, changed_at DESC);
CREATE INDEX idx_vehicle_price_history_vehicle_valid_from ON vehicle_price_history(vehicle_id, valid_from DESC);
CREATE INDEX idx_order_payments_order_id ON order_payments(order_id);
CREATE INDEX idx_order_status_history_order_changed_at ON order_status_history(order_id, changed_at DESC);
CREATE INDEX idx_test_drive_status_history_request_changed_at ON test_drive_status_history(test_drive_request_id, changed_at DESC);
CREATE INDEX idx_service_appointments_customer_id ON service_appointments(customer_id);
CREATE INDEX idx_service_appointments_dealership_datetime ON service_appointments(dealership_id, requested_datetime);
CREATE INDEX idx_service_appointments_vehicle_id ON service_appointments(vehicle_id);
CREATE INDEX idx_service_orders_customer_id ON service_orders(customer_id);
CREATE INDEX idx_service_orders_dealership_id ON service_orders(dealership_id);
CREATE INDEX idx_service_orders_vehicle_id ON service_orders(vehicle_id);
CREATE INDEX idx_service_orders_assigned_employee_id ON service_orders(assigned_employee_id);
CREATE INDEX idx_service_order_items_order_id ON service_order_items(service_order_id);
CREATE INDEX idx_service_order_items_service_id ON service_order_items(service_id);
CREATE INDEX idx_dealership_part_inventory_part_id ON dealership_part_inventory(part_id);
CREATE INDEX idx_outbox_events_dispatch ON outbox_events(status, available_at);
CREATE INDEX idx_idempotency_keys_expires_at ON idempotency_keys(expires_at);
