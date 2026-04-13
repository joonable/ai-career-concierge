import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";

const appRoot = process.cwd();
const envFiles = [
  ".env.development.local",
  ".env.local",
  ".env.development",
  ".env",
].map((name) => path.join(appRoot, name));

const loadedEnv = {};
for (const envPath of envFiles) {
  if (!existsSync(envPath)) {
    continue;
  }

  const lines = readFileSync(envPath, "utf-8").split(/\r?\n/);
  for (const line of lines) {
    if (!line || line.trim().startsWith("#")) {
      continue;
    }

    const separatorIndex = line.indexOf("=");
    if (separatorIndex < 0) {
      continue;
    }

    const key = line.slice(0, separatorIndex).trim();
    const rawValue = line.slice(separatorIndex + 1).trim();
    if (!key || process.env[key] !== undefined || loadedEnv[key] !== undefined) {
      continue;
    }

    loadedEnv[key] = rawValue;
  }
}

const port = process.env.PORT ?? loadedEnv.PORT ?? "3000";
const nextBinary = path.join(appRoot, "node_modules", ".bin", "next");
const child = spawn(nextBinary, ["dev", "--port", port], {
  stdio: "inherit",
  env: {
    ...process.env,
    ...loadedEnv,
    PORT: port,
  },
});

child.on("exit", (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
    return;
  }

  process.exit(code ?? 0);
});
