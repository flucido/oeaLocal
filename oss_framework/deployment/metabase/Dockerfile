# Debian-based Metabase with DuckDB driver
# Based on: https://github.com/motherduckdb/metabase_duckdb_driver/blob/main/Dockerfile

FROM eclipse-temurin:21-jre-jammy

# Build arguments for versions
ARG METABASE_VERSION=v0.58.7
ARG METABASE_DUCKDB_DRIVER_VERSION=1.4.3.1

ENV MB_PLUGINS_DIR=/home/metabase/plugins/

# Create metabase user and group
RUN groupadd -r metabase && useradd -r -g metabase metabase

# Install curl and CA certificates
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create directories
RUN mkdir -p /home/metabase/plugins /home/metabase/data && \
    chown -R metabase:metabase /home/metabase

WORKDIR /home/metabase

# Download Metabase JAR
RUN curl -L -o /home/metabase/metabase.jar \
    https://downloads.metabase.com/${METABASE_VERSION}/metabase.jar && \
    chown metabase:metabase /home/metabase/metabase.jar && \
    chmod 755 /home/metabase/metabase.jar

# Download DuckDB driver
RUN curl -L -o /home/metabase/plugins/duckdb.metabase-driver.jar \
    https://github.com/motherduckdb/metabase_duckdb_driver/releases/download/${METABASE_DUCKDB_DRIVER_VERSION}/duckdb.metabase-driver.jar && \
    chown metabase:metabase /home/metabase/plugins/duckdb.metabase-driver.jar && \
    chmod 755 /home/metabase/plugins/duckdb.metabase-driver.jar

EXPOSE 3000

USER metabase

CMD ["java", "-jar", "/home/metabase/metabase.jar"]
