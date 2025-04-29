import sqlite3
from queue import Queue

# Database path
DB_PATH = 'insurance.db'

class ConnectionPool:
    def __init__(self, max_connections=5):
        self.max_connections = max_connections
        self.pool = Queue(maxsize=max_connections)
        self._initialize_pool()

    def _initialize_pool(self):
        """Create initial connections"""
        for _ in range(self.max_connections):
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            self.pool.put(conn)

    def get_connection(self):
        """Get a connection from the pool"""
        return self.pool.get()

    def return_connection(self, conn):
        """Return a connection to the pool"""
        self.pool.put(conn)

    def close_all(self):
        """Close all connections"""
        while not self.pool.empty():
            conn = self.pool.get()
            conn.close()

# Create a global connection pool
pool = ConnectionPool()