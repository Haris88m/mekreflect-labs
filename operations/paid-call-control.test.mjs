import test from 'node:test';
import assert from 'node:assert/strict';
import { guardedDraft, limiterDecision } from './paid-call-control.mjs';

for (const [name, request] of [
  ['HTTP failure', () => new Response('', { status: 503 })],
  ['network failure', () => { throw new Error('synthetic failure'); }],
  ['malformed JSON', () => new Response('{')],
  ['null', () => Response.json(null)],
  ['missing decision', () => Response.json({})],
  ['string decision', () => Response.json({ allowed: 'true' })],
  ['number decision', () => Response.json({ allowed: 1 })],
  ['array decision', () => Response.json([{ allowed: true }])],
  ['truthy adapter success flag', () => ({ ok: 'false', json: async () => ({ allowed: true }) })],
]) {
  test(`${name} cannot trigger paid generation`, async () => {
    let calls = 0;
    const outcome = await guardedDraft(request, () => { calls++; return 'draft'; });
    assert.deepEqual(outcome, { status: 503, retryAfter: 60 });
    assert.equal(calls, 0);
  });
}
for (const [retry, expected] of [[22, 22], [1000, 60], [-1, 60], [0, 60], ['9', 60], [1.5, 60], [null, 60]]) {
  test(`denial bounds retry ${String(retry)} without generation`, async () => {
    let calls = 0;
    assert.deepEqual(await guardedDraft(() => Response.json({ allowed: false, retry_after_s: retry }), () => { calls++; }), { status: 429, retryAfter: expected });
    assert.equal(calls, 0);
  });
}
test('positive authorization makes exactly one generation call', async () => {
  let calls = 0;
  assert.deepEqual(await guardedDraft(() => Response.json({ allowed: true }), () => { calls++; return ' Synthetic reply. '; }), { status: 200, draft: 'Synthetic reply.' });
  assert.equal(calls, 1);
});
test('generation errors are not leaked', async () => {
  assert.deepEqual(await guardedDraft(() => Response.json({ allowed: true }), () => { throw new Error('private context'); }), { status: 502 });
});
test('empty generation is not success', async () => {
  assert.deepEqual(await guardedDraft(() => Response.json({ allowed: true }), () => '  '), { status: 502 });
});
test('invalid policy configuration is rejected before a callback', async () => {
  for (const value of [0, -1, 1.5, '60', NaN]) {
    await assert.rejects(limiterDecision(() => { throw new Error('not called'); }, value), TypeError);
  }
});
