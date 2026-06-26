// Copies non-TS assets (SVG icons) into the compiled dist tree so that
// n8n can resolve `file:signatrust.svg` references at runtime. tsc never
// touches non-TypeScript files, so this step is mandatory for packages
// that ship icons alongside their TypeScript sources.
const fs = require('fs');
const path = require('path');

const pairs = [
	{ src: 'nodes/Signatrust/signatrust.svg', dst: 'dist/nodes/Signatrust/signatrust.svg' },
	{ src: 'credentials/signatrust.svg',      dst: 'dist/credentials/signatrust.svg' },
];

for (const { src, dst } of pairs) {
	if (!fs.existsSync(src)) {
		console.error(`copy-icons: missing source ${src}`);
		process.exit(1);
	}
	fs.mkdirSync(path.dirname(dst), { recursive: true });
	fs.copyFileSync(src, dst);
	console.log(`copy-icons: ${src} -> ${dst}`);
}
