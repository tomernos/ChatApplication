/**
 * React Application Entry Point
 * 
 * This file is executed first when the browser loads the app.
 * It "injects" the React App into the HTML div with id="root".
 */

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

// Initialize OpenTelemetry asynchronously after app renders (non-blocking)
// Temporarily disabled to debug frontend loading issue
// TODO: Re-enable once frontend loads properly
/*
setTimeout(() => {
  import('./instrumentation').then(({ initializeOpenTelemetry }) => {
    try {
      initializeOpenTelemetry();
    } catch (error) {
      console.warn('OpenTelemetry initialization skipped:', error.message);
    }
  }).catch((error) => {
    console.warn('OpenTelemetry not available:', error.message);
  });
}, 100);
*/

/**
 * React.StrictMode is a development tool that:
 * - Warns about deprecated features
 * - Checks for potential problems
 * - Only runs in development (not production)
 */
