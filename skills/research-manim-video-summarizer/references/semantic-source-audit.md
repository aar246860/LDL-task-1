# Semantic Source Audit

The structural storyboard score proves count, order, field, and mapping
contracts. It does not prove that a fluent sentence describes the paper
correctly. Strict completion therefore requires a separate source-passage audit
performed after the storyboard draft and before Manim code generation.

## Review Procedure

1. Assign a named reviewer who did not draft the ledger in the same pass. A
   second local agent or a human coauthor is acceptable; an unchecked self-label
   is not.
2. Reopen the source artifact. The checker accepts UTF-8 text sources and PDFs.
3. Compare every `Bxx` premise with one verbatim source passage that appears
   exactly once and does not overlap any other audited passage.
4. Compare every `Mxx` input-operation-output-validity row with one verbatim
   source passage that appears exactly once and does not overlap any other
   audited passage. Confirm that the row contains one irreducible
   scientific operation, not merely one grammatical clause.
5. Read every scene in full, including step detail, narration, transitions, and
   captions. Record whether it introduces a scientific premise or method
   operation not declared by its owning `Bxx` or `Mxx`.
6. Record any source item that the story should include but does not map. Strict
   approval requires an explicitly empty `unmapped_source_items` list.
7. Compute hashes only after the source and storyboard are final. Any change to
   either artifact invalidates the audit.

## Required JSON

```json
{
  "reviewer": "name or independent-agent identifier",
  "reviewer_role": "independent source auditor",
  "reviewed_at": "2026-07-13T16:00:00+08:00",
  "review_method": "source passage comparison",
  "audit_scope": "all background premises, method operations, and scene scientific claims",
  "decision": "pass",
  "source_artifact_sha256": "64 lowercase hexadecimal characters",
  "storyboard_sha256": "64 lowercase hexadecimal characters",
  "background_items": [
    {
      "id": "B01",
      "source_locator": "exact locator copied from the ledger",
      "source_excerpt": "a distinct passage present in the source artifact",
      "claim_anchor_terms": ["two or more phrases shared by the ledger claim and excerpt"],
      "independent_premise_count": 1,
      "semantic_match": "pass"
    }
  ],
  "method_items": [
    {
      "id": "M01",
      "source_locator": "exact locator copied from the ledger",
      "source_excerpt": "a distinct passage present in the source artifact",
      "claim_anchor_terms": ["two or more phrases shared by the ledger claim and excerpt"],
      "irreducible_operation_count": 1,
      "semantic_match": "pass"
    }
  ],
  "scene_items": [
    {
      "scene": 1,
      "background_premise_count": 1,
      "method_operation_count": 0,
      "undeclared_scientific_content": "none",
      "source_claims_checked": "pass"
    }
  ],
  "unmapped_source_items": []
}
```

Run the structural and semantic gates together:

```bash
uv run scripts/check_storyboard_contract.py storyboard.md --strict \
  --source-artifact paper.pdf \
  --semantic-audit storyboard_semantic_audit.json
```

The checker verifies artifact hashes, exact ledger and scene coverage, locator
agreement, uniquely located non-overlapping excerpts, claim anchor terms shared by
the storyboard claim and source passage, and signed review fields. It cannot infer
whether a passage logically entails a claim. `semantic_match` and
`source_claims_checked` remain accountable reviewer judgments, which is why a
named independent review pass is mandatory.
