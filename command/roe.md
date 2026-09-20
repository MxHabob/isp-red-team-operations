# Rules of Engagement

## Purpose
Define the boundaries for `RT-YNET-001`.

## Required before execution
- Written authorization exists.
- Scope identifiers are populated.
- Test accounts are confirmed.
- Emergency contact is documented.
- Stop conditions are agreed.
- Evidence classification is defined.

## Stop conditions
Immediately stop the current test if:
- an out-of-scope destination is reached;
- customer/third-party data appears;
- service degradation is observed;
- unexpected production impact occurs;
- the test identity behaves unexpectedly;
- authorization becomes uncertain.

## Evidence
Preserve raw evidence externally and store only metadata/hashes in Git.

## Operator rule
Do not improvise scope expansion during execution. Create a new approved test/change instead.
