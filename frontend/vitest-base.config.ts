import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    reporters: ['default'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/**',
        'dist/**',
        'src/environments/**',
        '**/*.routes.ts',
        '**/*.model.ts',
        '**/*.dto.ts',
        '**/*.d.ts',
      ],
    },
  },
});
