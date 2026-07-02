// The one shape every stored record must satisfy. Both walls import this —
// scripts/check-model.mjs (the gate) and tests/model.test.mjs — so a SPEC's
// Minimal Shape is copied from here, never imagined.
export const REQUIRED_FIELDS = ["id", "name", "status"];
export const STATUS_VALUES = ["draft", "active", "retired"];

export function validateRecord(record) {
  const errors = [];
  for (const field of REQUIRED_FIELDS) {
    if (!(field in record)) errors.push(`missing required field '${field}'`);
  }
  if ("status" in record && !STATUS_VALUES.includes(record.status)) {
    errors.push(`status '${record.status}' not one of ${STATUS_VALUES.join(" | ")}`);
  }
  if ("id" in record && !/^[a-z0-9-]+$/.test(record.id)) {
    errors.push(`id '${record.id}' must be kebab-case`);
  }
  return errors;
}
