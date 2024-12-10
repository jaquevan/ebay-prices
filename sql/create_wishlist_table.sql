DROP TABLE IF EXISTS wishlist;
CREATE TABLE wishlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    item_id TEXT NOT NULL,
    title TEXT NOT NULL,
    price REAL,
    alert_price REAL,
    deleted BOOLEAN DEFAULT FALSE
);