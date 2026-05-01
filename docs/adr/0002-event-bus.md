# ADR 0002 — Event bus

* Status: accepted
* Date: 2026-04-04

## Context

The platform is fundamentally event-driven (block events → features →
anomaly score → signal → order → fill → notification). We considered:

1. Direct service-to-service HTTP calls
2. Redis pub/sub
3. Kafka
4. NATS / JetStream

## Decision

We chose **Kafka**. The arguments:

* Topic-based fan-out is exactly the model we need (`T_PRICES`,
  `T_ANOMALY`, `T_SIGNALS`, …).
* Replayability matters — when we change the anomaly model we want to
  re-process historical events without re-fetching from RPC nodes.
* Strong ecosystem of consumer-group, offset-management, and
  schema-evolution tooling.

## Consequences

* Operational footprint is larger (broker, controller). The Helm
  chart provides an in-cluster Kafka with PVC; production deployments
  may swap to MSK / Confluent Cloud.
* JSON-on-Kafka is sufficient for our scale (low-thousands of events
  per second). We can move to Avro/Protobuf if necessary without
  changing the topology.
* The ML service maintains its own offsets so it can re-run training
  windows. That is the only stateful consumer.
