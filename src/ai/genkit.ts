import {genkit} from 'genkit';
import {googleAI} from '@genkit-ai/google-genai';

// This is a simplified configuration for demonstration.
// In a real-world scenario, you might have more plugins (e.g., for tracing, evaluation).
export const ai = genkit({
  plugins: [
    googleAI(),
  ],
  logLevel: 'debug',
  enableTracingAndMetrics: true,
});
