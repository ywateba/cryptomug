# CryptoMug API

This directory contains the core backend API for the CryptoMug application. It is a FastAPI-based service responsible for managing cryptocurrency data providers, tokens, and orchestrating the collection of price data.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)

---

## Overview

The CryptoMug API serves as the central configuration and data-fetching engine. It provides a RESTful interface to:

- Configure and manage data sources (providers).
- Register and manage cryptocurrency tokens.
- Trigger and store time-series price data into a dedicated time-series database.

## Features

- **Provider Management**: Full CRUD (Create, Read, Update, Delete) functionality for data providers.
- **Default Provider**: Ability to designate one provider as the default for data fetching.
- **Token Management**: Full CRUD for cryptocurrency tokens.
- **Token Toggling**: Enable or disable specific tokens for price collection.
- **Price Fetching**: A dedicated endpoint to trigger the collection of prices for all enabled tokens.
- **Containerized**: Fully containerized with Docker and orchestrated with Docker Compose for easy setup and deployment.
- **Structured Logging**: JSON-formatted logs for easy parsing and monitoring.

## Technology Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Databases**:
  - **PostgreSQL**: For storing relational data (Providers, Tokens).
  - **InfluxDB**: For storing time-series price data.
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/)
- **Data Validation**: [Pydantic](https://docs.pydantic.dev/)
- **Containerization**: [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)

---

## Getting Started

The entire application stack (API, PostgreSQL, InfluxDB) is managed by Docker Compose.

### Prerequisites

- Docker
- Docker Compose

### Running the API

1.  **Navigate to the Project Root**: Open a terminal in the root of the `cryptomug` project (the directory containing `docker-compose.yml`).

    ```bash
    cd /path/to/your/cryptomug/
    ```

2.  **Build and Run the Services**: Use Docker Compose to build the API image and start all services in the background.

    ```bash
    docker-compose up --build -d
    ```

3.  **Access the API**: The API will be available at `http://localhost:8000`.

---

## API Endpoints

The API provides interactive documentation (powered by Swagger UI) where you can view and test all available endpoints.

**Interactive Docs URL**: **http://localhost:8000/docs**

The endpoints are organized into the following categories:

- **Providers**: Endpoints for creating, listing, updating, and deleting data providers. Includes functionality for setting a default provider.
- **Tokens**: Endpoints for managing tokens, including enabling/disabling them for price tracking.
- **Prices**: Endpoint to trigger the price fetching and storage process.

---

## Configuration

The API is configured via environment variables, which are set in the `docker-compose.yml` file. Key variables include:

- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_SERVER`, `POSTGRES_DB`: Credentials for the PostgreSQL database.
- `INFLUXDB_URL`: The URL for the InfluxDB instance.
- `INFLUXDB_TOKEN`: The authentication token for InfluxDB.
- `INFLUXDB_ORG`: The organization name in InfluxDB.
- `INFLUXDB_BUCKET`: The bucket where price data is stored.

All configuration is centralized in the `config.py` file.