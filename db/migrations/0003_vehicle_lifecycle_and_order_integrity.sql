-- Vehicle lifecycle status replaces is_active; orders drive it through triggers; histories are written by triggers only.

-- Actor/context helpers: the application sets them per transaction with set_config(name, value, true).
CREATE OR REPLACE FUNCTION app_current_user_id()
RETURNS UUID AS $$
    SELECT NULLIF(current_setting('app.user_id', true), '')::UUID;
$$ LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION app_change_reason()
RETURNS TEXT AS $$
    SELECT NULLIF(current_setting('app.change_reason', true), '');
$$ LANGUAGE sql STABLE;


-- 1. vehicles.status (replaces is_active)
ALTER TABLE vehicles ADD COLUMN status vehicle_lifecycle_status NOT NULL DEFAULT 'in_stock';

ALTER TABLE vehicles DISABLE TRIGGER trg_vehicles_updated_at;
UPDATE vehicles v
SET status = CASE
    WHEN EXISTS (SELECT 1 FROM orders o WHERE o.vehicle_id = v.id AND o.status = 'completed')
        THEN 'sold'::vehicle_lifecycle_status
    WHEN EXISTS (SELECT 1 FROM orders o WHERE o.vehicle_id = v.id AND o.status <> 'cancelled')
        THEN 'reserved'::vehicle_lifecycle_status
    WHEN v.is_active THEN 'in_stock'::vehicle_lifecycle_status
    ELSE 'unavailable'::vehicle_lifecycle_status
END;
ALTER TABLE vehicles ENABLE TRIGGER trg_vehicles_updated_at;

-- Bring the history in line with the status computed above.
INSERT INTO vehicle_status_history(vehicle_id, status, reason)
SELECT v.id, v.status, 'Status synchronized by migration 0003'
FROM vehicles v
WHERE v.status IS DISTINCT FROM (
    SELECT h.status FROM vehicle_status_history h
    WHERE h.vehicle_id = v.id
    ORDER BY h.changed_at DESC, h.id DESC
    LIMIT 1
);

ALTER TABLE vehicles DROP COLUMN is_active;
CREATE INDEX idx_vehicles_status ON vehicles(status);


-- 2. Vehicle guards: 'reserved'/'sold' are managed by orders only; no transfer while an order is active.
-- pg_trigger_depth() = 1 means the statement came from the application, > 1 means from another trigger.
CREATE OR REPLACE FUNCTION guard_vehicle_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF pg_trigger_depth() = 1 THEN
        IF TG_OP = 'INSERT' AND NEW.status IN ('reserved', 'sold') THEN
            RAISE EXCEPTION 'Vehicle status "%" is managed by orders and cannot be set directly', NEW.status;
        END IF;
        IF TG_OP = 'UPDATE' AND NEW.status IS DISTINCT FROM OLD.status
           AND (OLD.status IN ('reserved', 'sold') OR NEW.status IN ('reserved', 'sold')) THEN
            RAISE EXCEPTION 'Vehicle status "%" is managed by orders and cannot be changed directly', NEW.status;
        END IF;
    END IF;
    IF TG_OP = 'UPDATE' AND NEW.dealership_id IS DISTINCT FROM OLD.dealership_id AND EXISTS (
        SELECT 1 FROM orders WHERE vehicle_id = NEW.id AND status NOT IN ('completed', 'cancelled')
    ) THEN
        RAISE EXCEPTION 'Vehicle has an active order and cannot be moved to another dealership';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_vehicles_guard
BEFORE INSERT OR UPDATE ON vehicles
FOR EACH ROW EXECUTE FUNCTION guard_vehicle_changes();

CREATE OR REPLACE FUNCTION record_vehicle_status_history()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' OR NEW.status IS DISTINCT FROM OLD.status THEN
        INSERT INTO vehicle_status_history(vehicle_id, status, reason, changed_by_user_id)
        VALUES (NEW.id, NEW.status, app_change_reason(), app_current_user_id());
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_vehicle_status_history
AFTER INSERT OR UPDATE OF status ON vehicles
FOR EACH ROW EXECUTE FUNCTION record_vehicle_status_history();

-- Price history also needs the initial row on INSERT.
CREATE OR REPLACE FUNCTION record_vehicle_price_history()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' OR NEW.price IS DISTINCT FROM OLD.price THEN
        UPDATE vehicle_price_history SET valid_to = now() WHERE vehicle_id = NEW.id AND valid_to IS NULL;
        INSERT INTO vehicle_price_history(vehicle_id, price, valid_from, changed_by_user_id)
        VALUES (NEW.id, NEW.price, now(), app_current_user_id());
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_vehicle_price_history ON vehicles;
CREATE TRIGGER trg_vehicle_price_history
AFTER INSERT OR UPDATE OF price ON vehicles
FOR EACH ROW EXECUTE FUNCTION record_vehicle_price_history();


-- 3. Orders: one active order per vehicle, immutable parties, valid transitions, vehicle status follows the order.
ALTER TABLE orders DROP CONSTRAINT orders_vehicle_id_key;
CREATE UNIQUE INDEX uq_orders_active_vehicle ON orders(vehicle_id) WHERE status <> 'cancelled';
ALTER TABLE orders ADD CONSTRAINT chk_orders_final_price_positive CHECK (final_price > 0);

CREATE OR REPLACE FUNCTION check_vehicle_availability()
RETURNS TRIGGER AS $$
DECLARE
    v_status vehicle_lifecycle_status;
    v_dealership_id INTEGER;
BEGIN
    SELECT status, dealership_id INTO v_status, v_dealership_id
    FROM vehicles WHERE id = NEW.vehicle_id FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Vehicle not found';
    END IF;
    IF v_status = 'reserved' THEN
        RAISE EXCEPTION 'Vehicle is already reserved in another active order';
    END IF;
    IF v_status <> 'in_stock' THEN
        RAISE EXCEPTION 'Vehicle is not available for purchase';
    END IF;
    IF NEW.dealership_id <> v_dealership_id THEN
        RAISE EXCEPTION 'Order dealership does not match vehicle dealership';
    END IF;
    IF NEW.status <> 'pending_payment' THEN
        RAISE EXCEPTION 'Order must be created in pending_payment status';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_check_vehicle_availability ON orders;
CREATE TRIGGER trg_check_vehicle_availability
BEFORE INSERT ON orders
FOR EACH ROW EXECUTE FUNCTION check_vehicle_availability();

CREATE OR REPLACE FUNCTION guard_order_update()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.customer_id IS DISTINCT FROM OLD.customer_id
       OR NEW.vehicle_id IS DISTINCT FROM OLD.vehicle_id
       OR NEW.dealership_id IS DISTINCT FROM OLD.dealership_id THEN
        RAISE EXCEPTION 'Order customer, vehicle and dealership cannot be changed';
    END IF;
    IF NEW.status IS DISTINCT FROM OLD.status AND NOT is_valid_status_transition(OLD.status, NEW.status) THEN
        RAISE EXCEPTION 'Invalid status transition from % to %', OLD.status, NEW.status;
    END IF;
    IF NEW.final_price IS DISTINCT FROM OLD.final_price THEN
        IF OLD.status <> 'pending_payment' THEN
            RAISE EXCEPTION 'Order price can only be changed while payment is pending';
        END IF;
        IF NEW.final_price < (
            SELECT COALESCE(SUM(amount), 0) FROM order_payments
            WHERE order_id = NEW.id AND status IN ('authorized', 'paid')
        ) THEN
            RAISE EXCEPTION 'Order price cannot be lower than the amount already paid';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_orders_guard
BEFORE UPDATE ON orders
FOR EACH ROW EXECUTE FUNCTION guard_order_update();

CREATE OR REPLACE FUNCTION record_order_status_history()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO order_status_history(order_id, from_status, to_status, changed_by_user_id, comment)
        VALUES (NEW.id, NULL, NEW.status, app_current_user_id(), app_change_reason());
    ELSIF NEW.status IS DISTINCT FROM OLD.status THEN
        INSERT INTO order_status_history(order_id, from_status, to_status, changed_by_user_id, comment)
        VALUES (NEW.id, OLD.status, NEW.status, app_current_user_id(), app_change_reason());
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_order_status_history ON orders;
CREATE TRIGGER trg_order_status_history
AFTER INSERT OR UPDATE OF status ON orders
FOR EACH ROW EXECUTE FUNCTION record_order_status_history();

CREATE OR REPLACE FUNCTION sync_vehicle_status_with_order()
RETURNS TRIGGER AS $$
DECLARE
    v_target vehicle_lifecycle_status;
    v_previous_reason TEXT;
BEGIN
    v_target := CASE NEW.status
        WHEN 'completed' THEN 'sold'
        WHEN 'cancelled' THEN 'in_stock'
        ELSE 'reserved'
    END;
    v_previous_reason := current_setting('app.change_reason', true);
    PERFORM set_config('app.change_reason', format('Order %s: %s', NEW.id, NEW.status), true);
    UPDATE vehicles SET status = v_target WHERE id = NEW.vehicle_id AND status IS DISTINCT FROM v_target;
    PERFORM set_config('app.change_reason', COALESCE(v_previous_reason, ''), true);
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_order_sync_vehicle_status
AFTER INSERT OR UPDATE OF status ON orders
FOR EACH ROW EXECUTE FUNCTION sync_vehicle_status_with_order();

CREATE OR REPLACE FUNCTION guard_order_delete()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status = 'completed' THEN
        RAISE EXCEPTION 'Completed orders cannot be deleted';
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_orders_guard_delete
BEFORE DELETE ON orders
FOR EACH ROW EXECUTE FUNCTION guard_order_delete();

CREATE OR REPLACE FUNCTION release_vehicle_on_order_delete()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE vehicles SET status = 'in_stock' WHERE id = OLD.vehicle_id AND status = 'reserved';
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_order_release_vehicle
AFTER DELETE ON orders
FOR EACH ROW EXECUTE FUNCTION release_vehicle_on_order_delete();

-- Validation and the vehicle side effects now live in the triggers above.
CREATE OR REPLACE PROCEDURE update_order_status(
    p_order_id UUID,
    p_new_status order_status
) AS $$
BEGIN
    UPDATE orders SET status = p_new_status WHERE id = p_order_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Order not found';
    END IF;
END;
$$ LANGUAGE plpgsql;


-- 4. Test drives: only for in-stock vehicles of the right dealership; cancelling is never a "conflict".
CREATE OR REPLACE FUNCTION check_test_drive_conflicts()
RETURNS TRIGGER AS $$
DECLARE
    v_status vehicle_lifecycle_status;
    v_dealership_id INTEGER;
BEGIN
    SELECT status, dealership_id INTO v_status, v_dealership_id FROM vehicles WHERE id = NEW.vehicle_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Vehicle not found';
    END IF;
    IF NEW.dealership_id <> v_dealership_id THEN
        RAISE EXCEPTION 'Test drive dealership does not match vehicle dealership';
    END IF;
    IF TG_OP = 'INSERT' AND v_status <> 'in_stock' THEN
        RAISE EXCEPTION 'Vehicle is not available for test drive';
    END IF;

    IF NEW.status IN ('requested', 'confirmed') AND EXISTS (
        SELECT 1 FROM test_drive_requests
        WHERE vehicle_id = NEW.vehicle_id
          AND status IN ('requested', 'confirmed')
          AND requested_datetime BETWEEN (NEW.requested_datetime - INTERVAL '1 hour')
                                     AND (NEW.requested_datetime + INTERVAL '1 hour')
          AND id != COALESCE(NEW.id, '00000000-0000-0000-0000-000000000000'::UUID)
    ) THEN
        RAISE EXCEPTION 'Test drive conflict: another test drive is scheduled for this vehicle at a similar time';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION record_test_drive_status_history()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO test_drive_status_history(test_drive_request_id, from_status, to_status, changed_by_user_id)
        VALUES (NEW.id, NULL, NEW.status, app_current_user_id());
    ELSIF NEW.status IS DISTINCT FROM OLD.status THEN
        INSERT INTO test_drive_status_history(test_drive_request_id, from_status, to_status, changed_by_user_id)
        VALUES (NEW.id, OLD.status, NEW.status, app_current_user_id());
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_test_drive_status_history ON test_drive_requests;
CREATE TRIGGER trg_test_drive_status_history
AFTER INSERT OR UPDATE OF status ON test_drive_requests
FOR EACH ROW EXECUTE FUNCTION record_test_drive_status_history();

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
    WHERE id = p_vehicle_id AND status = 'in_stock';

    IF v_dealership_id IS NULL THEN
        RAISE EXCEPTION 'Vehicle not found or not available';
    END IF;

    INSERT INTO test_drive_requests
        (customer_id, vehicle_id, dealership_id, requested_datetime)
    VALUES
        (p_customer_id, p_vehicle_id, v_dealership_id, p_requested_datetime);
END;
$$ LANGUAGE plpgsql;


-- 5. Catalog functions: is_active -> status.
DROP FUNCTION get_vehicle_with_details(UUID, VARCHAR);
DROP FUNCTION get_vehicles_filtered(UUID, INTEGER, BOOLEAN, DECIMAL, DECIMAL, VARCHAR, VARCHAR, INTEGER, INTEGER);
DROP FUNCTION count_vehicles_filtered(UUID, INTEGER, BOOLEAN, DECIMAL, DECIMAL);

CREATE FUNCTION get_vehicle_with_details(p_vehicle_id UUID DEFAULT NULL, p_vin VARCHAR DEFAULT NULL)
RETURNS TABLE (
    id UUID,
    model_id UUID,
    dealership_id INTEGER,
    vin VARCHAR,
    production_year INTEGER,
    exterior_color VARCHAR,
    interior_color VARCHAR,
    price DECIMAL,
    status vehicle_lifecycle_status,
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
        v.status,
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

CREATE FUNCTION get_vehicles_filtered(
    p_model_id UUID DEFAULT NULL,
    p_dealership_id INTEGER DEFAULT NULL,
    p_status vehicle_lifecycle_status DEFAULT NULL,
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
    status vehicle_lifecycle_status,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    model_name VARCHAR
) AS $$
DECLARE
    v_order_by TEXT;
BEGIN
    v_order_by := CASE
        WHEN p_sort_by IN ('created_at', 'price', 'production_year') THEN p_sort_by
        ELSE 'created_at'
    END;

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
            v.status,
            v.created_at,
            v.updated_at,
            m.name AS model_name
        FROM vehicles v
        LEFT JOIN models m ON m.id = v.model_id
        WHERE ($1 IS NULL OR v.model_id = $1)
          AND ($2 IS NULL OR v.dealership_id = $2)
          AND ($3 IS NULL OR v.status = $3)
          AND ($4 IS NULL OR v.price >= $4)
          AND ($5 IS NULL OR v.price <= $5)
        ORDER BY v.%s, v.id
        OFFSET $6 LIMIT $7',
        v_order_by
    ) USING p_model_id, p_dealership_id, p_status, p_min_price, p_max_price, p_offset, p_limit;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION count_vehicles_filtered(
    p_model_id UUID DEFAULT NULL,
    p_dealership_id INTEGER DEFAULT NULL,
    p_status vehicle_lifecycle_status DEFAULT NULL,
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
      AND (p_status IS NULL OR v.status = p_status)
      AND (p_min_price IS NULL OR v.price >= p_min_price)
      AND (p_max_price IS NULL OR v.price <= p_max_price);

    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- Same signature and result as before; only vehicles that can be bought are searchable.
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
    WHERE v.status = 'in_stock'
      AND v.price BETWEEN p_min_price AND p_max_price
      AND (p_model_name IS NULL OR m.name ILIKE '%' || p_model_name || '%')
      AND (p_body_type IS NULL OR bt.name = p_body_type)
      AND (p_fuel_type IS NULL OR e.fuel_type = p_fuel_type)
      AND (p_transmission_type IS NULL OR t.type = p_transmission_type)
      AND (p_dealership_id IS NULL OR v.dealership_id = p_dealership_id)
    ORDER BY v.price;
END;
$$ LANGUAGE plpgsql;
