# Keeping the creative source intact

## The question

How can I make an approved visual sequence easier to share without losing control of the work that has already been accepted?

For this project, I separated creation from production. The renderer does not decide what the story should be or generate replacement illustrations. Its job starts when the images have been approved. That makes the task inspectable and repeatable.

## My approach

I use AI-assisted development to turn a requirement into a workflow with clear inputs, rules and an output I can inspect. Here the requirement is deliberately narrow. Keep the original artwork, put the pages in order and produce a vertical silent video with restrained motion.

The implementation combines Pillow for image validation and FFmpeg for encoding. It rotates through four pan-and-zoom expressions, applies fades, renders each scene and concatenates the results. The public example supplies geometric shapes so another person can run it without needing my private source material.

## What changed during publication

Reviewing the code exposed two practical problems. Multiple runs could interfere with the same temporary folder, and an existing video could be replaced without a separate decision. The public version gives each run its own workspace and creates the final file exclusively. Numeric configuration now has explicit boundaries. Non-finite duration, odd dimensions and unsupported codecs are rejected early.

The test suite runs an actual encoder and decoder, not only mocked success messages. Failure cleanup is also exercised using an intercepted encoder failure. The result is a reusable production step with known limits, not a claim that I trained a video model or validated a commercial publishing business.

## What this contributes to my research

The principle is the same one I use in operational systems. Give an AI-assisted implementation enough context to do a specific job. Keep the approved source visible. Make transformations explicit. Check the output and the failure path before treating completion as success.

The next useful study would compare different framing policies on a licensed reference set, with human review of lost visual content. That evaluation is a proposal, not a completed result.
