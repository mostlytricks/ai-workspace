import test from "node:test";
import assert from "node:assert/strict";
import { validateRecord } from "../src/model.mjs";

test("model-required-fields", () => {
  assert.deepEqual(validateRecord({ id: "a-1", name: "A", status: "draft" }), []);
  assert.ok(validateRecord({ name: "A" }).length >= 2);
});

test("model-status-vocabulary", () => {
  assert.equal(validateRecord({ id: "a-1", name: "A", status: "bogus" }).length, 1);
});
