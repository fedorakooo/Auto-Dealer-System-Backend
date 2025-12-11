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


-- Procedure: vehicle search
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
CREATE OR REPLACE FUNCTION process_test_drive_request(
    p_customer_id UUID,
    p_vehicle_id UUID,
    p_requested_datetime TIMESTAMPTZ
) RETURNS UUID AS $$
DECLARE
    v_dealership_id INTEGER;
    v_test_drive_id UUID;
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
        (p_customer_id, p_vehicle_id, v_dealership_id, p_requested_datetime)
    RETURNING id INTO v_test_drive_id;

    RETURN v_test_drive_id;
END;
$$ LANGUAGE plpgsql;


-- Procedure: updates order status with validation
CREATE OR REPLACE FUNCTION update_order_status(
    p_order_id UUID,
    p_new_status order_status
) RETURNS BOOLEAN AS $$
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

    RETURN true;
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
