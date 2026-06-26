// ESLint config aligned with n8n verified-node automated checks.
// Mirrors the official n8n-nodes-starter template:
//   https://github.com/n8n-io/n8n-nodes-starter/blob/master/.eslintrc.js
module.exports = {
	root: true,
	env: { browser: true, es6: true, node: true },
	parser: '@typescript-eslint/parser',
	parserOptions: {
		ecmaVersion: 2020,
		sourceType: 'module',
		extraFileExtensions: ['.json'],
	},
	ignorePatterns: [
		'.eslintrc.cjs',
		'**/*.js',
		'**/node_modules/**',
		'**/dist/**',
	],
	overrides: [
		{
			files: ['package.json'],
			plugins: ['n8n-nodes-base'],
			extends: ['plugin:n8n-nodes-base/community'],
			parser: 'jsonc-eslint-parser',
			rules: {
				'n8n-nodes-base/community-package-json-name-still-default': 'off',
			},
		},
		{
			files: ['./credentials/**/*.ts'],
			plugins: ['n8n-nodes-base'],
			extends: ['plugin:n8n-nodes-base/credentials'],
			rules: {
				// Buggy rule that camel-cases URL strings; community packages
				// universally disable it (see n8n-nodes-starter template).
				'n8n-nodes-base/cred-class-field-documentation-url-miscased': 'off',
			},
		},
		{
			files: ['./nodes/**/*.ts'],
			plugins: ['n8n-nodes-base'],
			extends: ['plugin:n8n-nodes-base/nodes'],
		},
	],
};
