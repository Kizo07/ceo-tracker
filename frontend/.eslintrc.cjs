module.exports = {
  root: true,
  env: { browser: true, es2021: true, node: true },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
  ],
  ignorePatterns: [
    'dist',
    'node_modules',
    'vite.config.ts',
    'src/types/api.generated.ts',
  ],
  parser: '@typescript-eslint/parser',
  parserOptions: { ecmaVersion: 'latest', sourceType: 'module' },
  plugins: ['react-refresh'],
  rules: {
    // Dev-only Vite HMR hint; noisy for files that co-export constants/hooks.
    'react-refresh/only-export-components': 'off',
    // The codebase uses `any` for untyped API payloads in a few view components;
    // tightened as generated types are adopted (Phase 2, CONTRACT-008).
    '@typescript-eslint/no-explicit-any': 'off',
    '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
  },
};
