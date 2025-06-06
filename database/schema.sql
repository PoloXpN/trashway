CREATE TABLE IF NOT EXISTS bins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bin_id TEXT UNIQUE,
    weight REAL NOT NULL,
    presence INTEGER NOT NULL,
    longitude REAL NOT NULL,
    latitude REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS simulations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    max_trucks INTEGER NOT NULL,
    max_capacity REAL NOT NULL,
    bins_to_collect INTEGER NOT NULL,
    total_distance REAL,
    total_time REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS routes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    simulation_id INTEGER NOT NULL,
    truck_id INTEGER NOT NULL,
    bin_order INTEGER NOT NULL,
    bin_id INTEGER NOT NULL,
    distance_to_next REAL,
    time_to_next REAL,
    FOREIGN KEY (simulation_id) REFERENCES simulations (id),
    FOREIGN KEY (bin_id) REFERENCES bins (id)
);

CREATE TABLE IF NOT EXISTS distances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_bin_id INTEGER NOT NULL,
    to_bin_id INTEGER NOT NULL,
    distance REAL NOT NULL,
    duration REAL NOT NULL,
    FOREIGN KEY (from_bin_id) REFERENCES bins (id),
    FOREIGN KEY (to_bin_id) REFERENCES bins (id),
    UNIQUE(from_bin_id, to_bin_id)
);