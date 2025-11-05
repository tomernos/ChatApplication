#!/bin/sh
# wait-for-services.sh
# Waits for Redis and RabbitMQ to be fully ready before starting the backend

echo "Waiting for services to be ready..."

# Wait for Redis
until nc -z cache 6379; do
  echo "Redis is unavailable - sleeping"
  sleep 2
done
echo "✓ Redis is ready!"

# Wait for RabbitMQ (management port indicates full readiness)
until nc -z message-queue 15672; do
  echo "RabbitMQ is unavailable - sleeping"
  sleep 2
done
echo "✓ RabbitMQ is ready!"

# Extra grace period for RabbitMQ to fully initialize
echo "Giving services extra 5 seconds to stabilize..."
sleep 5

echo "✓ All services ready! Starting backend..."
exec "$@"
