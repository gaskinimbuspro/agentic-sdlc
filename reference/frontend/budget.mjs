import { readdir, readFile } from "node:fs/promises";
import { gzipSync } from "node:zlib";

const assets = await readdir("dist/assets");
const bundleFiles = assets.filter((name) => /\.(js|css)$/.test(name));
if (bundleFiles.length === 0) throw new Error("No built JavaScript or CSS");
const files = await Promise.all(
  bundleFiles.map(
    async (name) => gzipSync(await readFile("dist/assets/" + name)).length,
  ),
);
const bytes = files.reduce((sum, size) => sum + size, 0);
const limit = 120 * 1024;
console.log(
  JSON.stringify({ gzip_bytes: bytes, limit, files: bundleFiles.length }),
);
if (bytes > limit) process.exitCode = 1;
