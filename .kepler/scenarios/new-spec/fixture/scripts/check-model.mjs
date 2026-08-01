// The model gate (`npm run lint:model`): validates every data/*.json record
// against src/model.mjs and exits non-zero on any violation.
import { readdirSync, readFileSync } from "node:fs";
import { validateRecord } from "../src/model.mjs";

let failures = 0;
for (const file of readdirSync("data").filter((f) => f.endsWith(".json"))) {
  const record = JSON.parse(readFileSync(`data/${file}`, "utf8"));
  for (const error of validateRecord(record)) {
    console.error(`data/${file}: ${error}`);
    failures += 1;
  }
}
if (failures) {
  console.error(`${failures} violation(s).`);
  process.exit(1);
}
console.log("model gate: all records valid.");
