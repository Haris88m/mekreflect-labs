/** Source-derived DOPRI cost admission control. No network adapter is included. */
export async function limiterDecision(requestDecision, windowSeconds = 60) {
  if (!Number.isSafeInteger(windowSeconds) || windowSeconds < 1) {
    throw new TypeError('windowSeconds must be a positive safe integer');
  }
  const unavailable = { allowed: false, retry_after_s: windowSeconds, unavailable: true };
  try {
    const response = await requestDecision();
    if (response?.ok !== true) return unavailable;
    const out = await response.json();
    if (!out || Array.isArray(out) || typeof out.allowed !== 'boolean') return unavailable;
    if (!out.allowed) {
      const retry = out.retry_after_s;
      return {
        allowed: false,
        retry_after_s: typeof retry === 'number' && Number.isSafeInteger(retry) && retry > 0
          ? Math.min(retry, windowSeconds) : windowSeconds,
      };
    }
    return { allowed: true, retry_after_s: 0 };
  } catch {
    return unavailable;
  }
}

/** Admission and execution are deliberately separate observable stages. */
export async function guardedDraft(requestDecision, generateDraft) {
  const decision = await limiterDecision(requestDecision);
  if (decision.unavailable) return { status: 503, retryAfter: decision.retry_after_s };
  if (!decision.allowed) return { status: 429, retryAfter: decision.retry_after_s };
  try {
    const draft = await generateDraft();
    if (typeof draft !== 'string' || !draft.trim()) return { status: 502 };
    return { status: 200, draft: draft.trim() };
  } catch {
    // Never return provider errors, which may contain private inputs or secrets.
    return { status: 502 };
  }
}
