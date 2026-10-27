import { defineConfig, globalIgnores } from 'eslint/config';
import nextVitals from 'eslint-config-next/core-web-vitals';
import nextTs from 'eslint-config-next/typescript';

export default defineConfig([
  ...nextVitals,
  ...nextTs,
  globalIgnores(['.next/**', 'out/**', 'node_modules/**', 'next-env.d.ts']),
  {
    rules: {
      // New React Compiler-era rule; existing data-fetching effects trip it.
      // Reported as a warning until those effects are refactored.
      'react-hooks/set-state-in-effect': 'warn',
    },
  },
]);
