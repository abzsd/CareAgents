# GCP Cloud SQL PostgreSQL Setup Guide

This guide explains how to connect your CareAgents backend to Google Cloud Platform (GCP) Cloud SQL PostgreSQL.

## Prerequisites

- GCP Cloud SQL PostgreSQL instance created
- Database and user credentials
- Network access configured

## Connection Methods

### Method 1: Cloud SQL Proxy (Recommended)

The Cloud SQL Proxy provides secure access to your Cloud SQL instances without needing to whitelist IP addresses or configure SSL.

#### Step 1: Install Cloud SQL Proxy

```bash
# Download Cloud SQL Proxy
# macOS
curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.0/cloud-sql-proxy.darwin.amd64
chmod +x cloud-sql-proxy

# Linux
curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.0/cloud-sql-proxy.linux.amd64
chmod +x cloud-sql-proxy

# Move to PATH
sudo mv cloud-sql-proxy /usr/local/bin/
```

#### Step 2: Get Your Instance Connection Name

In GCP Console:
1. Go to Cloud SQL Instances
2. Click your instance
3. Copy the "Instance connection name" (format: `project:region:instance-name`)

#### Step 3: Start Cloud SQL Proxy

```bash
# Start proxy in the background
cloud-sql-proxy <INSTANCE_CONNECTION_NAME> --port 5432 &

# Example:
# cloud-sql-proxy my-project:us-central1:my-postgres-instance --port 5432 &
```

#### Step 4: Update Your .env File

```env
# Cloud SQL via Proxy
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=healthcare_db
DB_USER=postgres
DB_PASSWORD=your_password
# No SSL needed with proxy
DB_SSL=
```

### Method 2: Public IP with SSL

If you prefer direct connection via public IP:

#### Step 1: Enable Public IP

In GCP Console:
1. Go to your Cloud SQL instance
2. Navigate to "Connections"
3. Enable "Public IP"

#### Step 2: Add Authorized Networks

1. In "Connections" tab, go to "Authorized networks"
2. Add your IP address or network range
3. Click "Save"

#### Step 3: Get Public IP Address

Copy the public IP address from the instance overview page.

#### Step 4: Update Your .env File

```env
# Cloud SQL via Public IP with SSL
DB_HOST=<your-instance-public-ip>
DB_PORT=5432
DB_NAME=healthcare_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_SSL=require
```

### Method 3: Private IP (VPC)

If your application runs in the same VPC or you have VPN configured:

#### Step 1: Get Private IP

In GCP Console, get the private IP address of your instance.

#### Step 2: Update Your .env File

```env
# Cloud SQL via Private IP
DB_HOST=<your-instance-private-ip>
DB_PORT=5432
DB_NAME=healthcare_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_SSL=require
```

## SSL Configuration Options

The `DB_SSL` variable supports these values:

- **Empty or not set**: No SSL encryption
- **`require`**: SSL required but doesn't verify server certificate (good for Cloud SQL with proxy or trusted networks)
- **`verify-ca`**: Verify server certificate against CA
- **`verify-full`**: Full certificate verification including hostname

## Troubleshooting

### Connection Timeout

If you're experiencing connection timeouts:

1. Check firewall rules in GCP
2. Verify authorized networks include your IP
3. Increase timeout values in .env:

```env
DB_TIMEOUT=120
DB_COMMAND_TIMEOUT=120
```

### SSL/TLS Errors

If you see SSL-related errors:

```bash
# Try without SSL first (only for testing)
DB_SSL=

# Then try with SSL
DB_SSL=require
```

### Authentication Failed

1. Verify credentials in GCP Console
2. Check that the user has proper permissions
3. Ensure the database name is correct

### Cloud SQL Proxy Not Working

```bash
# Check if proxy is running
ps aux | grep cloud-sql-proxy

# Check proxy logs
cloud-sql-proxy <INSTANCE_CONNECTION_NAME> --port 5432

# Authenticate with gcloud
gcloud auth application-default login
```

### Network Connection Issues

1. Check if instance is running in GCP Console
2. Verify your IP is in authorized networks
3. Check VPC firewall rules if using private IP
4. Ensure Cloud SQL API is enabled in your GCP project

## Testing Connection

Test your connection with psql:

```bash
# Via Cloud SQL Proxy
psql -h 127.0.0.1 -p 5432 -U postgres -d healthcare_db

# Via Public/Private IP
psql -h <instance-ip> -p 5432 -U postgres -d healthcare_db
```

## Environment Variables Reference

```env
# Database Connection
DB_HOST=<host>                    # IP address or localhost
DB_PORT=5432                      # Port (default: 5432)
DB_NAME=healthcare_db             # Database name
DB_USER=postgres                  # Database user
DB_PASSWORD=<password>            # User password

# SSL Configuration
DB_SSL=require                    # SSL mode (require, verify-ca, verify-full, or empty)

# Connection Pool Settings
DB_POOL_MIN_SIZE=10              # Minimum pool size
DB_POOL_MAX_SIZE=20              # Maximum pool size

# Timeout Settings
DB_TIMEOUT=60                     # Connection timeout in seconds
DB_COMMAND_TIMEOUT=60            # Command timeout in seconds
```

## Best Practices

1. **Use Cloud SQL Proxy in production** - Most secure and doesn't require IP whitelisting
2. **Enable SSL** - Always use SSL for public IP connections
3. **Use strong passwords** - Generate secure passwords for database users
4. **Limit authorized networks** - Only whitelist necessary IP ranges
5. **Use IAM authentication** - Consider using Cloud SQL IAM authentication for better security
6. **Monitor connections** - Set up monitoring for connection pool metrics
7. **Use secrets management** - Store credentials in GCP Secret Manager instead of .env files

## Additional Resources

- [Cloud SQL Proxy Documentation](https://cloud.google.com/sql/docs/postgres/sql-proxy)
- [Cloud SQL Security Best Practices](https://cloud.google.com/sql/docs/postgres/security)
- [Connection Options](https://cloud.google.com/sql/docs/postgres/connect-overview)
