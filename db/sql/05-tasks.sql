-- Trigger function: checks that vehicle is active and not reserved
CREATE OR REPLACE FUNCTION check_vehicle_availability()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT (SELECT is_active FROM vehicles WHERE id = NEW.vehicle_id) THEN
        RAISE EXCEPTION 'Vehicle is not available for purchase';
    END IF;

    IF EXISTS (
        SELECT 1 FROM orders
        WHERE vehicle_id = NEW.vehicle_id
        AND status NOT IN ('completed', 'cancelled')
        AND id != COALESCE(NEW.id, '00000000-0000-0000-0000-000000000000'::UUID)
    ) THEN
        RAISE EXCEPTION 'Vehicle is already reserved in another active order';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_vehicle_availability
    BEFORE INSERT OR UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION check_vehicle_availability();


-- Trigger function: checks for test drive time conflicts
CREATE OR REPLACE FUNCTION check_test_drive_conflicts()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM test_drive_requests
        WHERE vehicle_id = NEW.vehicle_id
        AND dealership_id = NEW.dealership_id
        AND requested_datetime BETWEEN (NEW.requested_datetime - INTERVAL '1 hour')
                                AND (NEW.requested_datetime + INTERVAL '1 hour')
        AND status IN ('requested', 'confirmed')
        AND id != COALESCE(NEW.id, '00000000-0000-0000-0000-000000000000'::UUID)
    ) THEN
        RAISE EXCEPTION 'Test drive conflict: another test drive is scheduled for this vehicle at a similar time';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_test_drive_conflicts
    BEFORE INSERT OR UPDATE ON test_drive_requests
    FOR EACH ROW EXECUTE FUNCTION check_test_drive_conflicts();


CREATE OR REPLACE FUNCTION search_vehicles(
    p_model_name VARCHAR DEFAULT NULL,
    p_body_type VARCHAR DEFAULT NULL,
    p_fuel_type fuel_type DEFAULT NULL,
    p_transmission_type transmission_type DEFAULT NULL,
    p_min_price DECIMAL DEFAULT 0,
    p_max_price DECIMAL DEFAULT 99999999,
    p_dealership_id INTEGER DEFAULT NULL
) RETURNS TABLE (
    vehicle_id UUID,
    model_name VARCHAR,
    body_type VARCHAR,
    fuel_type fuel_type,
    transmission_type transmission_type,
    exterior_color VARCHAR,
    price DECIMAL(12,2),
    dealership_name VARCHAR,
    city_name VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        v.id,
        m.name,
        bt.name,
        e.fuel_type,
        t.type,
        v.exterior_color,
        v.price,
        d.name,
        c.name
    FROM vehicles v
    JOIN models m ON v.model_id = m.id
    JOIN body_types bt ON m.body_type_id = bt.id
    JOIN engines e ON m.engine_id = e.id
    JOIN transmissions t ON m.transmission_id = t.id
    JOIN dealerships d ON v.dealership_id = d.id
    JOIN cities c ON d.city_id = c.id
    WHERE v.is_active = true
      AND v.price BETWEEN p_min_price AND p_max_price
      AND (p_model_name IS NULL OR m.name ILIKE '%' || p_model_name || '%')
      AND (p_body_type IS NULL OR bt.name = p_body_type)
      AND (p_fuel_type IS NULL OR e.fuel_type = p_fuel_type)
      AND (p_transmission_type IS NULL OR t.type = p_transmission_type)
      AND (p_dealership_id IS NULL OR v.dealership_id = p_dealership_id)
    ORDER BY v.price;
END;
$$ LANGUAGE plpgsql;


-- Procedure: process test drive request
CREATE OR REPLACE PROCEDURE process_test_drive_request(
    p_customer_id UUID,
    p_vehicle_id UUID,
    p_requested_datetime TIMESTAMPTZ
) AS $$
DECLARE
    v_dealership_id INTEGER;
BEGIN
    SELECT dealership_id INTO v_dealership_id
    FROM vehicles
    WHERE id = p_vehicle_id AND is_active = true;

    IF v_dealership_id IS NULL THEN
        RAISE EXCEPTION 'Vehicle not found or not available';
    END IF;

    INSERT INTO test_drive_requests
        (customer_id, vehicle_id, dealership_id, requested_datetime)
    VALUES
        (p_customer_id, p_vehicle_id, v_dealership_id, p_requested_datetime);
END;
$$ LANGUAGE plpgsql;

-- Procedure: updates order status with validation
CREATE OR REPLACE PROCEDURE update_order_status(
    p_order_id UUID,
    p_new_status order_status
) AS $$
DECLARE
    v_current_status order_status;
    v_vehicle_id UUID;
BEGIN
    SELECT status, vehicle_id INTO v_current_status, v_vehicle_id
    FROM orders WHERE id = p_order_id;

    IF v_current_status IS NULL THEN
        RAISE EXCEPTION 'Order not found';
    END IF;

    IF NOT is_valid_status_transition(v_current_status, p_new_status) THEN
        RAISE EXCEPTION 'Invalid status transition from % to %', v_current_status, p_new_status;
    END IF;

    UPDATE orders
    SET status = p_new_status, updated_at = now()
    WHERE id = p_order_id;

    IF p_new_status IN ('completed', 'cancelled') THEN
        UPDATE vehicles
        SET is_active = (p_new_status = 'cancelled'), updated_at = now()
        WHERE id = v_vehicle_id;
    END IF;
END;
$$ LANGUAGE plpgsql;


-- Helper function: validates order status transitions
CREATE OR REPLACE FUNCTION is_valid_status_transition(
    old_status order_status,
    new_status order_status
) RETURNS BOOLEAN AS $$
BEGIN
    RETURN CASE
        WHEN old_status = 'pending_payment' THEN new_status IN ('processing', 'cancelled')
        WHEN old_status = 'processing' THEN new_status IN ('ready_for_pickup', 'cancelled')
        WHEN old_status = 'ready_for_pickup' THEN new_status IN ('completed', 'cancelled')
        WHEN old_status = 'completed' THEN false
        WHEN old_status = 'cancelled' THEN false
        ELSE true
    END;
END;
$$ LANGUAGE plpgsql;


-- Function: Get vehicle with model details (for get_by_id and get_by_vin)
CREATE OR REPLACE FUNCTION get_vehicle_with_details(p_vehicle_id UUID DEFAULT NULL, p_vin VARCHAR DEFAULT NULL)
RETURNS TABLE (
    id UUID,
    model_id UUID,
    dealership_id INTEGER,
    vin VARCHAR,
    production_year INTEGER,
    exterior_color VARCHAR,
    interior_color VARCHAR,
    price DECIMAL,
    is_active BOOLEAN,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    model_name VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        v.id,
        v.model_id,
        v.dealership_id,
        v.vin,
        v.production_year,
        v.exterior_color,
        v.interior_color,
        v.price,
        v.is_active,
        v.created_at,
        v.updated_at,
        m.name AS model_name
    FROM vehicles v
    LEFT JOIN models m ON m.id = v.model_id
    WHERE (p_vehicle_id IS NULL OR v.id = p_vehicle_id)
      AND (p_vin IS NULL OR v.vin = p_vin)
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;


-- Function: Get vehicles with filtering and pagination
CREATE OR REPLACE FUNCTION get_vehicles_filtered(
    p_model_id UUID DEFAULT NULL,
    p_dealership_id INTEGER DEFAULT NULL,
    p_is_active BOOLEAN DEFAULT NULL,
    p_min_price DECIMAL DEFAULT NULL,
    p_max_price DECIMAL DEFAULT NULL,
    p_sort_by VARCHAR DEFAULT 'created_at',
    p_order_direction VARCHAR DEFAULT 'ASC',
    p_offset INTEGER DEFAULT 0,
    p_limit INTEGER DEFAULT 20
)
RETURNS TABLE (
    id UUID,
    model_id UUID,
    dealership_id INTEGER,
    vin VARCHAR,
    production_year INTEGER,
    exterior_color VARCHAR,
    interior_color VARCHAR,
    price DECIMAL,
    is_active BOOLEAN,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    model_name VARCHAR
) AS $$
DECLARE
    v_order_by TEXT;
BEGIN
    -- Validate and sanitize sort_by
    v_order_by := CASE
        WHEN p_sort_by IN ('created_at', 'price', 'production_year') THEN p_sort_by
        ELSE 'created_at'
    END;

    -- Validate order direction
    IF UPPER(p_order_direction) NOT IN ('ASC', 'DESC') THEN
        v_order_by := v_order_by || ' ASC';
    ELSE
        v_order_by := v_order_by || ' ' || UPPER(p_order_direction);
    END IF;

    RETURN QUERY
    EXECUTE format('
        SELECT
            v.id,
            v.model_id,
            v.dealership_id,
            v.vin,
            v.production_year,
            v.exterior_color,
            v.interior_color,
            v.price,
            v.is_active,
            v.created_at,
            v.updated_at,
            m.name AS model_name
        FROM vehicles v
        LEFT JOIN models m ON m.id = v.model_id
        WHERE ($1 IS NULL OR v.model_id = $1)
          AND ($2 IS NULL OR v.dealership_id = $2)
          AND ($3 IS NULL OR v.is_active = $3)
          AND ($4 IS NULL OR v.price >= $4)
          AND ($5 IS NULL OR v.price <= $5)
        ORDER BY v.%s
        OFFSET $6 LIMIT $7',
        v_order_by
    ) USING p_model_id, p_dealership_id, p_is_active, p_min_price, p_max_price, p_offset, p_limit;
END;
$$ LANGUAGE plpgsql;


-- Function: Count vehicles with filtering
CREATE OR REPLACE FUNCTION count_vehicles_filtered(
    p_model_id UUID DEFAULT NULL,
    p_dealership_id INTEGER DEFAULT NULL,
    p_is_active BOOLEAN DEFAULT NULL,
    p_min_price DECIMAL DEFAULT NULL,
    p_max_price DECIMAL DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM vehicles v
    WHERE (p_model_id IS NULL OR v.model_id = p_model_id)
      AND (p_dealership_id IS NULL OR v.dealership_id = p_dealership_id)
      AND (p_is_active IS NULL OR v.is_active = p_is_active)
      AND (p_min_price IS NULL OR v.price >= p_min_price)
      AND (p_max_price IS NULL OR v.price <= p_max_price);

    RETURN v_count;
END;
$$ LANGUAGE plpgsql;


-- Function: Get order with customer and vehicle details
CREATE OR REPLACE FUNCTION get_order_with_details(
    p_order_id UUID DEFAULT NULL,
    p_dealership_id INTEGER DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    customer_id UUID,
    vehicle_id UUID,
    dealership_id INTEGER,
    status order_status,
    final_price DECIMAL,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    customer_first_name VARCHAR,
    customer_second_name VARCHAR,
    customer_email VARCHAR,
    vehicle_vin VARCHAR,
    model_name VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        o.id,
        o.customer_id,
        o.vehicle_id,
        o.dealership_id,
        o.status,
        o.final_price,
        o.created_at,
        o.updated_at,
        u.first_name AS customer_first_name,
        u.second_name AS customer_second_name,
        u.email AS customer_email,
        v.vin AS vehicle_vin,
        m.name AS model_name
    FROM orders o
    LEFT JOIN customers c ON c.id = o.customer_id
    LEFT JOIN users u ON u.id = c.user_id
    LEFT JOIN vehicles v ON v.id = o.vehicle_id
    LEFT JOIN models m ON m.id = v.model_id
    WHERE (p_order_id IS NULL OR o.id = p_order_id)
      AND (p_dealership_id IS NULL OR o.dealership_id = p_dealership_id);
END;
$$ LANGUAGE plpgsql;


-- Function: Get orders with filtering and pagination
CREATE OR REPLACE FUNCTION get_orders_filtered(
    p_customer_id UUID DEFAULT NULL,
    p_dealership_id INTEGER DEFAULT NULL,
    p_status order_status DEFAULT NULL,
    p_sort_by VARCHAR DEFAULT 'created_at',
    p_order_direction VARCHAR DEFAULT 'ASC',
    p_offset INTEGER DEFAULT 0,
    p_limit INTEGER DEFAULT 20
)
RETURNS TABLE (
    id UUID,
    customer_id UUID,
    vehicle_id UUID,
    dealership_id INTEGER,
    status order_status,
    final_price DECIMAL,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
) AS $$
DECLARE
    v_order_by TEXT;
BEGIN
    v_order_by := CASE
        WHEN p_sort_by IN ('created_at', 'final_price', 'status') THEN p_sort_by
        ELSE 'created_at'
    END;

    -- Validate order direction
    IF UPPER(p_order_direction) NOT IN ('ASC', 'DESC') THEN
        v_order_by := v_order_by || ' ASC';
    ELSE
        v_order_by := v_order_by || ' ' || UPPER(p_order_direction);
    END IF;

    RETURN QUERY
    EXECUTE format('
        SELECT
            o.id,
            o.customer_id,
            o.vehicle_id,
            o.dealership_id,
            o.status,
            o.final_price,
            o.created_at,
            o.updated_at
        FROM orders o
        WHERE ($1 IS NULL OR o.customer_id = $1)
          AND ($2 IS NULL OR o.dealership_id = $2)
          AND ($3 IS NULL OR o.status = $3)
        ORDER BY o.%s
        OFFSET $4 LIMIT $5',
        v_order_by
    ) USING p_customer_id, p_dealership_id, p_status, p_offset, p_limit;
END;
$$ LANGUAGE plpgsql;


-- Function: Count orders with filtering
CREATE OR REPLACE FUNCTION count_orders_filtered(
    p_customer_id UUID DEFAULT NULL,
    p_dealership_id INTEGER DEFAULT NULL,
    p_status order_status DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM orders o
    WHERE (p_customer_id IS NULL OR o.customer_id = p_customer_id)
      AND (p_dealership_id IS NULL OR o.dealership_id = p_dealership_id)
      AND (p_status IS NULL OR o.status = p_status);

    RETURN v_count;
END;
$$ LANGUAGE plpgsql;


-- Function: Get models with filtering and pagination
CREATE OR REPLACE FUNCTION get_models_filtered(
    p_name VARCHAR DEFAULT NULL,
    p_is_in_production BOOLEAN DEFAULT NULL,
    p_body_type_id INTEGER DEFAULT NULL,
    p_engine_id INTEGER DEFAULT NULL,
    p_sort_by VARCHAR DEFAULT 'created_at',
    p_order_direction VARCHAR DEFAULT 'ASC',
    p_offset INTEGER DEFAULT 0,
    p_limit INTEGER DEFAULT 20
)
RETURNS TABLE (
    id UUID,
    body_type_id INTEGER,
    engine_id INTEGER,
    transmission_id INTEGER,
    name VARCHAR,
    model_code VARCHAR,
    is_in_production BOOLEAN,
    production_year_start INTEGER,
    production_year_end INTEGER,
    description TEXT,
    drive_type drive_type,
    max_speed_kmh INTEGER,
    acceleration_0_100_sec DECIMAL,
    fuel_tank_capacity_l INTEGER,
    number_of_seats INTEGER,
    number_of_doors INTEGER,
    length_mm INTEGER,
    width_mm INTEGER,
    height_mm INTEGER,
    curb_weight_kg INTEGER,
    gross_weight_kg INTEGER,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
) AS $$
DECLARE
    v_order_by TEXT;
BEGIN
    -- Validate and sanitize sort_by
    v_order_by := CASE
        WHEN p_sort_by IN ('created_at', 'name', 'production_year_start') THEN p_sort_by
        ELSE 'created_at'
    END;

    -- Validate order direction
    IF UPPER(p_order_direction) NOT IN ('ASC', 'DESC') THEN
        v_order_by := v_order_by || ' ASC';
    ELSE
        v_order_by := v_order_by || ' ' || UPPER(p_order_direction);
    END IF;

    RETURN QUERY
    EXECUTE format('
        SELECT
            m.id,
            m.body_type_id,
            m.engine_id,
            m.transmission_id,
            m.name,
            m.model_code,
            m.is_in_production,
            m.production_year_start,
            m.production_year_end,
            m.description,
            m.drive_type,
            m.max_speed_kmh,
            m.acceleration_0_100_sec,
            m.fuel_tank_capacity_l,
            m.number_of_seats,
            m.number_of_doors,
            m.length_mm,
            m.width_mm,
            m.height_mm,
            m.curb_weight_kg,
            m.gross_weight_kg,
            m.created_at,
            m.updated_at
        FROM models m
        WHERE ($1 IS NULL OR m.name ILIKE ''%%'' || $1 || ''%%'')
          AND ($2 IS NULL OR m.is_in_production = $2)
          AND ($3 IS NULL OR m.body_type_id = $3)
          AND ($4 IS NULL OR m.engine_id = $4)
        ORDER BY m.%s
        OFFSET $5 LIMIT $6',
        v_order_by
    ) USING p_name, p_is_in_production, p_body_type_id, p_engine_id, p_offset, p_limit;
END;
$$ LANGUAGE plpgsql;


-- Function: Count models with filtering
CREATE OR REPLACE FUNCTION count_models_filtered(
    p_name VARCHAR DEFAULT NULL,
    p_is_in_production BOOLEAN DEFAULT NULL,
    p_body_type_id INTEGER DEFAULT NULL,
    p_engine_id INTEGER DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM models m
    WHERE (p_name IS NULL OR m.name ILIKE '%' || p_name || '%')
      AND (p_is_in_production IS NULL OR m.is_in_production = p_is_in_production)
      AND (p_body_type_id IS NULL OR m.body_type_id = p_body_type_id)
      AND (p_engine_id IS NULL OR m.engine_id = p_engine_id);

    RETURN v_count;
END;
$$ LANGUAGE plpgsql;


-- Function: Get users with customer data and filtering
CREATE OR REPLACE FUNCTION get_users_filtered(
    p_email VARCHAR DEFAULT NULL,
    p_role user_role DEFAULT NULL,
    p_is_active BOOLEAN DEFAULT NULL,
    p_sort_by VARCHAR DEFAULT 'created_at',
    p_order_direction VARCHAR DEFAULT 'ASC',
    p_offset INTEGER DEFAULT 0,
    p_limit INTEGER DEFAULT 20
)
RETURNS TABLE (
    id UUID,
    first_name VARCHAR,
    second_name VARCHAR,
    phone_number VARCHAR,
    email VARCHAR,
    hashed_password VARCHAR,
    role user_role,
    is_active BOOLEAN,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    date_of_birth DATE
) AS $$
DECLARE
    v_order_by TEXT;
BEGIN
    -- Validate and sanitize sort_by
    v_order_by := CASE
        WHEN p_sort_by IN ('created_at', 'email', 'first_name', 'second_name') THEN p_sort_by
        ELSE 'created_at'
    END;

    -- Validate order direction
    IF UPPER(p_order_direction) NOT IN ('ASC', 'DESC') THEN
        v_order_by := v_order_by || ' ASC';
    ELSE
        v_order_by := v_order_by || ' ' || UPPER(p_order_direction);
    END IF;

    RETURN QUERY
    EXECUTE format('
        SELECT
            u.id,
            u.first_name,
            u.second_name,
            u.phone_number,
            u.email,
            u.hashed_password,
            u.role,
            u.is_active,
            u.created_at,
            u.updated_at,
            c.date_of_birth
        FROM users u
        LEFT JOIN customers c ON c.user_id = u.id
        WHERE ($1 IS NULL OR u.email ILIKE ''%%'' || $1 || ''%%'')
          AND ($2 IS NULL OR u.role = $2)
          AND ($3 IS NULL OR u.is_active = $3)
        ORDER BY u.%s
        OFFSET $4 LIMIT $5',
        v_order_by
    ) USING p_email, p_role, p_is_active, p_offset, p_limit;
END;
$$ LANGUAGE plpgsql;


-- Function: Count users with filtering
CREATE OR REPLACE FUNCTION count_users_filtered(
    p_email VARCHAR DEFAULT NULL,
    p_role user_role DEFAULT NULL,
    p_is_active BOOLEAN DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM users u
    WHERE (p_email IS NULL OR u.email ILIKE '%' || p_email || '%')
      AND (p_role IS NULL OR u.role = p_role)
      AND (p_is_active IS NULL OR u.is_active = p_is_active);

    RETURN v_count;
END;
$$ LANGUAGE plpgsql;


-- Function: Get test drive request with details
CREATE OR REPLACE FUNCTION get_test_drive_with_details(
    p_test_drive_id UUID DEFAULT NULL,
    p_dealership_id INTEGER DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    customer_id UUID,
    vehicle_id UUID,
    dealership_id INTEGER,
    requested_datetime TIMESTAMPTZ,
    status test_drive_status,
    notes TEXT,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    customer_phone_number VARCHAR,
    vehicle_vin VARCHAR,
    model_name VARCHAR,
    dealership_name VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        tdr.id,
        tdr.customer_id,
        tdr.vehicle_id,
        tdr.dealership_id,
        tdr.requested_datetime,
        tdr.status,
        tdr.notes,
        tdr.created_at,
        tdr.updated_at,
        u.phone_number AS customer_phone_number,
        v.vin AS vehicle_vin,
        m.name AS model_name,
        d.name AS dealership_name
    FROM test_drive_requests tdr
    LEFT JOIN customers c ON c.id = tdr.customer_id
    LEFT JOIN users u ON u.id = c.user_id
    LEFT JOIN vehicles v ON v.id = tdr.vehicle_id
    LEFT JOIN models m ON m.id = v.model_id
    LEFT JOIN dealerships d ON d.id = tdr.dealership_id
    WHERE (p_test_drive_id IS NULL OR tdr.id = p_test_drive_id)
      AND (p_dealership_id IS NULL OR tdr.dealership_id = p_dealership_id);
END;
$$ LANGUAGE plpgsql;


-- Function: Get custom order with details
CREATE OR REPLACE FUNCTION get_custom_order_with_details(
    p_custom_order_id UUID DEFAULT NULL,
    p_dealership_id INTEGER DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    customer_id UUID,
    dealership_id INTEGER,
    model_id UUID,
    engine_id INTEGER,
    transmission_id INTEGER,
    exterior_color VARCHAR,
    interior_color VARCHAR,
    status custom_order_status,
    estimated_price DECIMAL,
    final_price DECIMAL,
    notes TEXT,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    customer_first_name VARCHAR,
    customer_second_name VARCHAR,
    customer_email VARCHAR,
    model_name VARCHAR,
    engine_name VARCHAR,
    transmission_name VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        co.id,
        co.customer_id,
        co.dealership_id,
        co.model_id,
        co.engine_id,
        co.transmission_id,
        co.exterior_color,
        co.interior_color,
        co.status,
        co.estimated_price,
        co.final_price,
        co.notes,
        co.created_at,
        co.updated_at,
        u.first_name AS customer_first_name,
        u.second_name AS customer_second_name,
        u.email AS customer_email,
        m.name AS model_name,
        e.name AS engine_name,
        t.name AS transmission_name
    FROM custom_orders co
    LEFT JOIN customers c ON c.id = co.customer_id
    LEFT JOIN users u ON u.id = c.user_id
    LEFT JOIN models m ON m.id = co.model_id
    LEFT JOIN engines e ON e.id = co.engine_id
    LEFT JOIN transmissions t ON t.id = co.transmission_id
    WHERE (p_custom_order_id IS NULL OR co.id = p_custom_order_id)
      AND (p_dealership_id IS NULL OR co.dealership_id = p_dealership_id);
END;
$$ LANGUAGE plpgsql;


-- Procedure: Delete vehicle media by vehicle_id
CREATE OR REPLACE PROCEDURE delete_vehicle_media_by_vehicle(
    p_vehicle_id UUID
) AS $$
BEGIN
    DELETE FROM vehicle_media
    WHERE vehicle_id = p_vehicle_id;
END;
$$ LANGUAGE plpgsql;


-- Procedure: Delete model media by model_id
CREATE OR REPLACE PROCEDURE delete_model_media_by_model(
    p_model_id UUID
) AS $$
BEGIN
    DELETE FROM model_media
    WHERE model_id = p_model_id;
END;
$$ LANGUAGE plpgsql;
