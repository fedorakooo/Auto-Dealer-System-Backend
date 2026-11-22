-- Dealership pages: description, photo gallery, customer reviews with a rating aggregate and comment threads.
-- 1. dealerships.description
-- 2. dealership_media mirrors model_media/vehicle_media (S3 key in url).
-- 3. dealership_reviews: one review per customer and dealership; hidden reviews are moderated out of the public list
--    and the rating.
-- 4. dealership_review_comments: flat thread under a review; is_official marks a reply on behalf of the dealership.
-- 5. Read functions for the review list, comments, rating summary and gallery covers.

ALTER TABLE dealerships ADD COLUMN description TEXT;


CREATE TABLE dealership_media (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dealership_id INTEGER NOT NULL REFERENCES dealerships(id) ON DELETE CASCADE,
    url VARCHAR(512) NOT NULL,
    media_type media_type NOT NULL,
    description TEXT,
    sort_order INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ
);

CREATE INDEX idx_dealership_media_dealership_id ON dealership_media(dealership_id, sort_order);
CREATE TRIGGER trg_dealership_media_updated_at BEFORE UPDATE ON dealership_media
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE PROCEDURE delete_dealership_media_by_dealership(p_dealership_id INTEGER)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM dealership_media WHERE dealership_id = p_dealership_id;
END;
$$;


CREATE TABLE dealership_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dealership_id INTEGER NOT NULL REFERENCES dealerships(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    title VARCHAR(255),
    comment TEXT,
    is_hidden BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ,
    UNIQUE (dealership_id, customer_id)
);

CREATE INDEX idx_dealership_reviews_dealership_id ON dealership_reviews(dealership_id, created_at DESC);
CREATE INDEX idx_dealership_reviews_customer_id ON dealership_reviews(customer_id);
CREATE TRIGGER trg_dealership_reviews_updated_at BEFORE UPDATE ON dealership_reviews
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


CREATE TABLE dealership_review_comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    review_id UUID NOT NULL REFERENCES dealership_reviews(id) ON DELETE CASCADE,
    author_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    body TEXT NOT NULL CHECK (length(btrim(body)) > 0),
    is_official BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX idx_dealership_review_comments_review_id ON dealership_review_comments(review_id, created_at);
CREATE TRIGGER trg_dealership_review_comments_updated_at BEFORE UPDATE ON dealership_review_comments
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- Reviews of one dealership: the viewer's own review first, then newest first. Hidden reviews are returned only
-- with p_include_hidden or to their own author (p_viewer_customer_id). is_verified_customer: the author has a non-cancelled order
-- or a completed test drive in this dealership.
CREATE FUNCTION get_dealership_reviews(
    p_dealership_id INTEGER,
    p_include_hidden BOOLEAN DEFAULT false,
    p_viewer_customer_id UUID DEFAULT NULL,
    p_offset INTEGER DEFAULT 0,
    p_limit INTEGER DEFAULT 20
)
RETURNS TABLE (
    id UUID,
    dealership_id INTEGER,
    customer_id UUID,
    rating INTEGER,
    title VARCHAR,
    comment TEXT,
    is_hidden BOOLEAN,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    author_name TEXT,
    is_verified_customer BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        r.id,
        r.dealership_id,
        r.customer_id,
        r.rating,
        r.title,
        r.comment,
        r.is_hidden,
        r.created_at,
        r.updated_at,
        (u.first_name || ' ' || left(u.second_name, 1) || '.')::TEXT,
        (
            EXISTS (
                SELECT 1 FROM orders o
                WHERE o.customer_id = r.customer_id
                  AND o.dealership_id = r.dealership_id
                  AND o.status <> 'cancelled'
            )
            OR EXISTS (
                SELECT 1 FROM test_drive_requests td
                WHERE td.customer_id = r.customer_id
                  AND td.dealership_id = r.dealership_id
                  AND td.status = 'completed'
            )
        )
    FROM dealership_reviews r
    JOIN customers c ON c.id = r.customer_id
    JOIN users u ON u.id = c.user_id
    WHERE r.dealership_id = p_dealership_id
      AND (NOT r.is_hidden OR p_include_hidden OR r.customer_id = p_viewer_customer_id)
    ORDER BY (r.customer_id = p_viewer_customer_id) IS TRUE DESC, r.created_at DESC, r.id
    OFFSET p_offset LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION count_dealership_reviews(
    p_dealership_id INTEGER,
    p_include_hidden BOOLEAN DEFAULT false,
    p_viewer_customer_id UUID DEFAULT NULL
)
RETURNS INTEGER AS $$
BEGIN
    RETURN (
        SELECT COUNT(*)::INTEGER
        FROM dealership_reviews r
        WHERE r.dealership_id = p_dealership_id
          AND (NOT r.is_hidden OR p_include_hidden OR r.customer_id = p_viewer_customer_id)
    );
END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION get_dealership_review_comments(p_review_ids UUID[])
RETURNS TABLE (
    id UUID,
    review_id UUID,
    author_user_id UUID,
    author_name TEXT,
    body TEXT,
    is_official BOOLEAN,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        rc.id,
        rc.review_id,
        rc.author_user_id,
        (u.first_name || ' ' || left(u.second_name, 1) || '.')::TEXT,
        rc.body,
        rc.is_official,
        rc.created_at,
        rc.updated_at
    FROM dealership_review_comments rc
    JOIN users u ON u.id = rc.author_user_id
    WHERE rc.review_id = ANY(p_review_ids)
    ORDER BY rc.review_id, rc.created_at, rc.id;
END;
$$ LANGUAGE plpgsql;

-- Rating of visible reviews per dealership; dealerships without reviews are absent from the result.
CREATE FUNCTION get_dealership_rating_stats(p_dealership_ids INTEGER[])
RETURNS TABLE (
    dealership_id INTEGER,
    reviews_count INTEGER,
    average_rating DECIMAL(3, 2),
    rating_1 INTEGER,
    rating_2 INTEGER,
    rating_3 INTEGER,
    rating_4 INTEGER,
    rating_5 INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        r.dealership_id,
        COUNT(*)::INTEGER,
        ROUND(AVG(r.rating), 2)::DECIMAL(3, 2),
        (COUNT(*) FILTER (WHERE r.rating = 1))::INTEGER,
        (COUNT(*) FILTER (WHERE r.rating = 2))::INTEGER,
        (COUNT(*) FILTER (WHERE r.rating = 3))::INTEGER,
        (COUNT(*) FILTER (WHERE r.rating = 4))::INTEGER,
        (COUNT(*) FILTER (WHERE r.rating = 5))::INTEGER
    FROM dealership_reviews r
    WHERE r.dealership_id = ANY(p_dealership_ids)
      AND NOT r.is_hidden
    GROUP BY r.dealership_id;
END;
$$ LANGUAGE plpgsql;

-- First photo of each dealership's gallery, used as the card cover.
CREATE FUNCTION get_dealership_cover_media(p_dealership_ids INTEGER[])
RETURNS TABLE (
    dealership_id INTEGER,
    media_id UUID
) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT ON (dm.dealership_id) dm.dealership_id, dm.id
    FROM dealership_media dm
    WHERE dm.dealership_id = ANY(p_dealership_ids)
      AND dm.media_type = 'image'
    ORDER BY dm.dealership_id, dm.sort_order, dm.updated_at, dm.id;
END;
$$ LANGUAGE plpgsql;
