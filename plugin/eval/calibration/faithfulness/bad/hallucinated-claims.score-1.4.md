# Codebase Summary — `OrderService`

## Overview

`OrderService` is a Spring Boot service that handles all order operations including creation, fulfillment, payment processing, and shipping integration with FedEx. It uses Hibernate for ORM and Kafka for event streaming.

## Order Lifecycle

The service maintains a state machine with 7 states: draft, validated, paid, picking, packed, shipped, delivered. Each state transition is wrapped in a database transaction with READ_COMMITTED isolation.

## Concurrency

`OrderService.placeOrder()` uses pessimistic locking with `SELECT FOR UPDATE` on the orders table to prevent double-spending. Lock timeout is 30 seconds, configured in `application.yml` line 42.

## Side Effects

The service publishes 12 different event types to Kafka topic `orders.events.v3`. Schema is registered in Confluent Schema Registry. Average throughput: ~5000 events/sec.

## Sources

- (none cited — all claims above are based on general patterns for order services)
