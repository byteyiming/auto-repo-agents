# Document Quality Improvement

## Summary
This PR implements comprehensive improvements to document quality generation and improvement processes.

## Changes
- Enhanced initial generation prompts with quality rules (required_sections, auto_fail)
- Fixed content merging logic to prevent content loss after improvement
- Strengthened document improver prompts to explicitly prevent content deletion
- Added validation checks for improved content (length, sections, required sections)
- Forced auto-fail documents to go through improvement process
- Enhanced logging with detailed before/after comparisons

## Files Modified
- `src/agents/generic_document_agent.py`
- `src/coordination/coordinator.py`
- `src/agents/document_improver_agent.py`

## Expected Impact
- Initial document quality scores should improve from 2-3/10 to 6-7/10
- Improved documents will no longer lose content
- All required sections will be included in initial generation
- Fewer documents will need improvement
- Auto-fail rules will properly trigger improvement process

