# Source grounded answer scoring

Each formal judgement is attributed to its executing assistant and uses the frozen question, required facts, answer claims, cited passages and original source location. Configuration labels are hidden in the review material. The method is recorded as `assistant_source_review`.

## Complete correctness

For answerable questions, mark correctness true when all required facts are conveyed accurately, requested edition and applicable conditions are respected, numerical values and units are correct, and additional substantive statements have source support. Meaning-equivalent wording is accepted. A missing required fact, a material unsupported addition or an incorrect edition makes complete correctness false. A partial answer with substantive content is assessed on completeness.

## Citation support

Judge every displayed claim using its entire citation set. Mark support true when that set supports the claim's meaning, numbers, units, conditions and edition. A matching excerpt alone establishes provenance. A claim that changes an obligation, scope or numerical limit receives false. Multiple references supporting one claim receive one judgement. Relevant extra passages may support facts even when they are absent from the benchmark's minimal gold locator.

## Editions and refusals

An answer based on a non-requested edition is a wrong-edition answer when the request specifies one unambiguous edition. This includes unavailable-year requests that produce substantive answers from the available edition. Pure edition lists or a statement explaining missing coverage are assessed as refusal or clarification.

A justified refusal follows the frozen expected action and explains the missing evidence, missing edition or conflicting context without adding unsupported substantive facts. Refusing an answerable question or asking an unnecessary clarification is a false refusal. API failures, invalid JSON, invalid citations and unknown interrupted outcomes receive their corresponding failure status and zero correctness. Their failure is recorded separately from refusal behaviour.

## Failure analysis and consistency

Use the most explanatory primary failure label and preserve a short source-bound reason. Inspect retrieval misses, unsupported claims, edition mistakes, incomplete answers and unnecessary refusals. Identical question, answer, claims and evidence tuples can reuse one judgement with all original slots retained. A changed answer or evidence set requires its own judgement.

Review decisions are retained even where the results fall below the planned targets. The benchmark's limited document coverage, unavailable formal edition pairs and shared assistant author/evaluator remain limitations of the reported observations.
