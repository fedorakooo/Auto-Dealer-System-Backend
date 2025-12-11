CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TYPE user_role AS ENUM ('customer', 'employee', 'admin');
CREATE TYPE fuel_type AS ENUM ('gasoline', 'diesel', 'electric', 'hybrid', 'lpg');
CREATE TYPE transmission_type AS ENUM ('automatic', 'manual', 'cvt', 'dct');
CREATE TYPE drive_type AS ENUM ('FWD', 'RWD', 'AWD');
CREATE TYPE order_status AS ENUM ('pending_payment', 'processing', 'ready_for_pickup', 'completed', 'cancelled');
CREATE TYPE custom_order_status AS ENUM ('pending_approval', 'confirmed', 'sent_to_factory', 'in_production', 'shipped', 'delivered', 'cancelled');
CREATE TYPE media_type AS ENUM ('image', 'video');
CREATE TYPE test_drive_status AS ENUM ('requested', 'confirmed', 'completed', 'cancelled');

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
CREATE TRIGGER trg_reviews_updated_at BEFORE UPDATE ON reviews FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_test_drive_requests_updated_at BEFORE UPDATE ON test_drive_requests FOR EACH ROW EXECUTE FUNCTION set_updated_at();

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
