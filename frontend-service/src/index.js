/**
 * React Application Entry Point
 * 
 * This file is executed first when the browser loads the app.
 * It "injects" the React App into the HTML div with id="root".
 */

// Initialize OpenTelemetry BEFORE React (for tracing)
import { initializeOpenTelemetry } from './instrumentation';
initializeOpenTelemetry();

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// Get the root HTML element
const root = ReactDOM.createRoot(document.getElementById('root'));

// Render the App component into the root element
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

/**
 * React.StrictMode is a development tool that:
 * - Warns about deprecated features
 * - Checks for potential problems
 * - Only runs in development (not production)
 */
