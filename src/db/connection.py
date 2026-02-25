import duckdb
from typing import Optional
import os
from threading import Lock

class DuckDBConnection:
    """
    Singleton class to manage DuckDB connection and extensions.
    """
    _instance: Optional['DuckDBConnection'] = None
    _connection: Optional[duckdb.DuckDBPyConnection] = None

    def __new__(cls) -> 'DuckDBConnection':
        if cls._instance is None:
            cls._instance = super(DuckDBConnection, cls).__new__(cls)
            cls._instance._initialize_connection()
        return cls._instance

    def _initialize_connection(self) -> None:
        """
        Initializes the DuckDB connection and loads the Delta extension.
        """
        try:
            print("Initializing DuckDB connection...")
            # using in-memory database as we are querying external Delta Lake files
            self._connection = duckdb.connect()

            # Install and Load Delta extension
            # Note: In some environments, installation might need to be explicit or skipped if pre-installed.
            # We assume standard DuckDB environment where installation is possible.
            self._connection.execute("INSTALL delta")
            self._connection.execute("LOAD delta")
            print("DuckDB connection established and Delta extension loaded.")
        except Exception as e:
            print(f"Error initializing DuckDB connection: {e}")
            raise e

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        """
        Returns the active DuckDB connection.
        """
        if self._connection is None:
             raise RuntimeError("DuckDB connection not initialized")
        return self._connection


class MotherDuckConnection:
    """
    Singleton class to manage MotherDuck cloud connection with thread safety.
    
    MotherDuck is a managed cloud service for DuckDB that allows querying data
    from cloud storage (S3, GCS, Azure Blob) and on-premises databases.
    
    Thread-safe implementation using lock pattern. The dbinstance_inactivity_ttl
    is set to 0s to prevent MotherDuck from caching database instances for 15
    minutes (default), which causes connection conflicts in multi-process environments.
    
    Environment Variables:
        MOTHERDUCK_TOKEN: JWT token from MotherDuck dashboard (required)
        MOTHERDUCK_DATABASE: Database name (default: 'aeries_data_mart')
    
    Example:
        >>> from src.db.connection import get_motherduck_connection
        >>> conn = get_motherduck_connection()
        >>> result = conn.execute('SELECT 1').fetchone()
        >>> print(result)
        (1,)
    """
    _instance: Optional['MotherDuckConnection'] = None
    _lock: Lock = Lock()
    _connection: Optional[duckdb.DuckDBPyConnection] = None
    _token: Optional[str] = None
    _database: str = 'aeries_data_mart'
    
    def __new__(cls, database: Optional[str] = None, token: Optional[str] = None) -> 'MotherDuckConnection':
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MotherDuckConnection, cls).__new__(cls)
                cls._instance._initialize_connection(database=database, token=token)
            return cls._instance
    
    def _initialize_connection(self, database: Optional[str] = None, token: Optional[str] = None) -> None:
        """
        Initializes the MotherDuck connection with thread safety.
        
        Args:
            database: MotherDuck database name. If None, uses MOTHERDUCK_DATABASE env var
                     or defaults to 'aeries_data_mart'
            token: MotherDuck JWT token. If None, uses MOTHERDUCK_TOKEN env var
        
        Raises:
            RuntimeError: If MOTHERDUCK_TOKEN environment variable is not set
            Exception: If connection fails or extensions cannot be loaded
        """
        try:
            print("Initializing MotherDuck connection...")
            
            # Read environment variables
            self._token = token or os.getenv('MOTHERDUCK_TOKEN')
            self._database = database or os.getenv('MOTHERDUCK_DATABASE', 'aeries_data_mart')
            
            if not self._token:
                raise RuntimeError(
                    "MOTHERDUCK_TOKEN environment variable is required for MotherDuck connection. "
                    "Please set your MotherDuck JWT token."
                )
            
            # Create connection string with critical dbinstance_inactivity_ttl=0s
            # This prevents MotherDuck from caching instances for 15 minutes
            connection_string = f'md:{self._database}?dbinstance_inactivity_ttl=0s'
            config = {'motherduck_token': self._token}
            
            self._connection = duckdb.connect(connection_string, config=config)
            
            # Load required extensions
            self._connection.execute("INSTALL httpfs")
            self._connection.execute("LOAD httpfs")
            self._connection.execute("INSTALL json")
            self._connection.execute("LOAD json")
            
            print(f"MotherDuck connection established to database '{self._database}'.")
        except Exception as e:
            print(f"Error initializing MotherDuck connection: {e}")
            raise e
    
    def get_connection(self) -> duckdb.DuckDBPyConnection:
        """
        Returns the active MotherDuck connection.
        
        Returns:
            duckdb.DuckDBPyConnection: Active MotherDuck connection
        
        Raises:
            RuntimeError: If connection is not initialized
        """
        if self._connection is None:
            raise RuntimeError("MotherDuck connection not initialized")
        return self._connection


def get_motherduck_connection(
    database: Optional[str] = None,
    read_only: bool = False
) -> duckdb.DuckDBPyConnection:
    """
    Convenience function to get a MotherDuck connection.
    
    Returns a singleton MotherDuck connection. Multiple calls return the same
    connection instance, ensuring efficient resource usage and consistent state.
    
    Args:
        database: MotherDuck database name. If None, uses environment variable
                 MOTHERDUCK_DATABASE or defaults to 'aeries_data_mart'
        read_only: Currently not used (MotherDuck manages access control via tokens)
    
    Returns:
        duckdb.DuckDBPyConnection: Active MotherDuck connection
    
    Raises:
        RuntimeError: If MOTHERDUCK_TOKEN is not set
    
    Example:
        >>> conn = get_motherduck_connection(database='my_database')
        >>> tables = conn.execute('SHOW TABLES').fetchall()
        >>> for table in tables:
        ...     print(table[0])
    """
    instance = MotherDuckConnection(database=database)
    return instance.get_connection()


def get_hybrid_connection(
    motherduck_database: Optional[str] = None,
    local_database_path: Optional[str] = None
) -> duckdb.DuckDBPyConnection:
    """
    Creates a connection that can query both MotherDuck cloud and local DuckDB data.
    
    This function creates a local DuckDB in-memory connection that can attach to
    MotherDuck as an external database, allowing seamless querying across both
    local and cloud data sources. Useful for hybrid analytics where you want to
    join local data with cloud-based datasets.
    
    Args:
        motherduck_database: MotherDuck database name. If None, uses environment
                            variable MOTHERDUCK_DATABASE or defaults to 'aeries_data_mart'
        local_database_path: Path to local DuckDB file. If None, uses environment
                            variable DUCKDB_DATABASE_PATH or defaults to
                            './oss_framework/data/oea.duckdb'
    
    Returns:
        duckdb.DuckDBPyConnection: Local DuckDB connection with MotherDuck attached
    
    Raises:
        RuntimeError: If MOTHERDUCK_TOKEN is not set or local database cannot be attached
    
    Example:
        >>> conn = get_hybrid_connection()
        >>> # Query local data: SELECT * FROM local_table
        >>> # Query MotherDuck data: SELECT * FROM motherduck.cloud_table
        >>> # Join across both: SELECT l.*, m.* FROM local_table l
        >>> #                   JOIN motherduck.cloud_table m ON l.id = m.id
        >>> result = conn.execute(
        ...     'SELECT * FROM motherduck.aeries_data_mart.students LIMIT 10'
        ... ).fetchall()
    """
    try:
        # Create local in-memory DuckDB connection
        hybrid_conn = duckdb.connect(':memory:')
        
        # Load extensions for local database
        hybrid_conn.execute("INSTALL delta")
        hybrid_conn.execute("LOAD delta")
        hybrid_conn.execute("INSTALL httpfs")
        hybrid_conn.execute("LOAD httpfs")
        hybrid_conn.execute("INSTALL json")
        hybrid_conn.execute("LOAD json")
        
        # Attach local database file if specified
        local_path = local_database_path or os.getenv(
            'DUCKDB_DATABASE_PATH',
            './oss_framework/data/oea.duckdb'
        )
        if local_path and os.path.exists(local_path):
            hybrid_conn.execute(f"ATTACH '{local_path}' AS local")
            print(f"Attached local DuckDB database from {local_path}")
        
        # Attach MotherDuck connection
        motherduck_db = motherduck_database or os.getenv(
            'MOTHERDUCK_DATABASE',
            'aeries_data_mart'
        )
        token = os.getenv('MOTHERDUCK_TOKEN')
        if not token:
            raise RuntimeError(
                "MOTHERDUCK_TOKEN environment variable is required for hybrid connection"
            )
        
        # Create connection string for MotherDuck attachment
        motherduck_conn_string = f'md:{motherduck_db}?dbinstance_inactivity_ttl=0s'
        motherduck_config = {'motherduck_token': token}
        motherduck_instance = duckdb.connect(
            motherduck_conn_string,
            config=motherduck_config
        )
        
        # Attach MotherDuck as an external database
        # Note: We use query_only=False to allow reads from MotherDuck
        hybrid_conn.execute(
            f"ATTACH DATABASE (SELECT 1) AS motherduck ",
            connection=motherduck_instance
        )
        
        print(f"Hybrid connection established with MotherDuck database '{motherduck_db}'")
        return hybrid_conn
    
    except Exception as e:
        print(f"Error creating hybrid connection: {e}")
        raise e
