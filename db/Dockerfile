# Use the official PostgreSQL 13 image as the base
FROM postgres:13

# (Optional) Set environment variables here
# WARNING: Storing credentials in a Dockerfile can be a security risk
# Better practice: pass these via Docker Compose or "docker run -e ..." flags
ENV POSTGRES_USER=phantom_user
ENV POSTGRES_PASSWORD=secret_password
ENV POSTGRES_DB=phantomdb

# Copy your custom initialization SQL script
COPY init.sql /docker-entrypoint-initdb.d/

# The default entrypoint and cmd for postgres:13 are already set,
# so no further commands are strictly necessary.
