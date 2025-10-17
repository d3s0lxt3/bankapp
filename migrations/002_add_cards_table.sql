CREATE TABLE IF NOT EXISTS cards (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    card_number VARCHAR(16),
    card_type VARCHAR(10),
    balance NUMERIC(12,2) DEFAULT 0
);

