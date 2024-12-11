DROP TABLE IF EXISTS items;
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ebay_item_id TEXT NOT NULL,
    title TEXT NOT NULL,
    price REAL,
    available_quantity = INTEGER NOT NULL,
    sold_quantity = INTEGER NOT NULL,
    alert_price REAL,
    deleted BOOLEAN DEFAULT FALSE
);