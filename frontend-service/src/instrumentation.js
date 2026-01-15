/**
 * OpenTelemetry Instrumentation for React Frontend
 * 
 * Initializes OpenTelemetry SDK for browser-based tracing.
 * Sends traces to OTEL Collector via HTTP endpoint.
 * 
 * Pattern: Follows backend instrumentation pattern (app/__init__.py)
 */

import { WebTracerProvider } from '@opentelemetry/sdk-trace-web';
import { Resource } from '@opentelemetry/resources';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { BatchSpanProcessor } from '@opentelemetry/sdk-trace-base';
import { FetchInstrumentation } from '@opentelemetry/instrumentation-fetch';
import { XMLHttpRequestInstrumentation } from '@opentelemetry/instrumentation-xml-http-request';
import { registerInstrumentations } from '@opentelemetry/instrumentation';
import { trace } from '@opentelemetry/api';

let tracer = null;

/**
 * Initialize OpenTelemetry for distributed tracing
 */
export function initializeOpenTelemetry() {
  try {
    // Get configuration from environment variables
    const otelEndpoint = process.env.REACT_APP_OTEL_EXPORTER_OTLP_ENDPOINT ||
      'http://otel-collector-opentelemetry-collector.monitoring.svc.cluster.local:4318';
    
    const serviceName = process.env.REACT_APP_OTEL_SERVICE_NAME || 'chatapp-frontend';
    const serviceNamespace = process.env.REACT_APP_OTEL_SERVICE_NAMESPACE || 'chatapp-dev';

    // Create resource with service information
    const resource = Resource.default().merge(
      new Resource({
        'service.name': serviceName,
        'service.namespace': serviceNamespace,
        'service.version': '1.0.0',
      })
    );

    // Configure OTLP exporter (HTTP endpoint for browser)
    const traceExporter = new OTLPTraceExporter({
      url: `${otelEndpoint}/v1/traces`,
      headers: {},
    });

    // Initialize Web Tracer Provider
    const provider = new WebTracerProvider({
      resource,
    });

    // Add span processor
    provider.addSpanProcessor(new BatchSpanProcessor(traceExporter));

    // Register the provider
    provider.register();

    // Register instrumentations
    registerInstrumentations({
      instrumentations: [
        // Auto-instrument fetch API
        new FetchInstrumentation({
          propagateTraceHeaderCorsUrls: [
            /http:\/\/.*/, // Allow all HTTP URLs (adjust for production)
          ],
        }),
        // Auto-instrument XMLHttpRequest (for axios)
        new XMLHttpRequestInstrumentation({
          propagateTraceHeaderCorsUrls: [
            /http:\/\/.*/, // Allow all HTTP URLs (adjust for production)
          ],
        }),
      ],
    });

    // Get tracer for manual spans
    tracer = trace.getTracer(serviceName);

    console.log(`✅ OpenTelemetry initialized: ${serviceName} -> ${otelEndpoint}`);
    console.log(`   Service namespace: ${serviceNamespace}`);

    return tracer;
  } catch (error) {
    console.warn(`⚠️  Failed to initialize OpenTelemetry: ${error.message}. Tracing disabled.`);
    console.warn(`   Error details:`, error);
    return null;
  }
}

/**
 * Get the tracer instance for manual spans
 * @returns {Tracer|null} Tracer instance or null if not initialized
 */
export function getTracer() {
  return tracer;
}

/**
 * Create a span for manual instrumentation
 * @param {string} name - Span name
 * @param {Object} attributes - Span attributes
 * @param {Function} fn - Function to execute within span
 * @returns {Promise} Result of the function
 */
export async function withSpan(name, attributes = {}, fn) {
  if (!tracer) {
    return fn();
  }

  const span = tracer.startSpan(name, {
    attributes,
  });

  try {
    const result = await fn(span);
    span.setStatus({ code: 1 }); // OK
    return result;
  } catch (error) {
    span.setStatus({ code: 2, message: error.message }); // ERROR
    span.recordException(error);
    throw error;
  } finally {
    span.end();
  }
}

