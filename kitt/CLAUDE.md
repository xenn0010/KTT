# Claude Instructions for KITT Project

## Core Principles

### Honesty and Transparency
- If you are not 100% certain about an implementation, explicitly state your uncertainty
- Never claim code will work if you have any doubts
- Always communicate limitations and potential issues upfront
- If asked to implement something you're unsure about, say "I'm not certain this will work" and explain why

### Code Quality Standards
- Write ONLY production-ready code
- No placeholders (no TODO comments, no dummy implementations, no "implement this later")
- No emoji in code or comments
- Every function must be fully implemented and tested
- All error handling must be complete and robust
- No shortcuts or temporary solutions

### What "Production-Ready" Means
- Code must handle all edge cases
- Proper error handling and validation
- Clean, maintainable architecture
- Follows project conventions and best practices
- Type-safe (use appropriate typing for the language)
- Performant and resource-efficient
- Security considerations addressed
- Logging and monitoring where appropriate

### Forbidden Practices
- Placeholder comments like TODO, FIXME, or "implement later"
- Dummy return values or mock implementations
- Partial implementations with the intention to "finish later"
- Using emoji anywhere in the codebase
- Claiming something works when uncertain
- Making assumptions without verification

### When You're Not Sure
Use these exact phrases when uncertain:
- "I'm not certain this will work because..."
- "I don't have enough information about..."
- "This approach may have issues with..."
- "I need to verify... before implementing this"

### Verification Requirements
- Before claiming code works, mentally trace through execution paths
- Consider failure modes and edge cases
- Verify compatibility with existing codebase
- Ensure all dependencies are properly handled

## Summary
Write working, production-ready code with no placeholders or emoji. If you're not 100% sure about something, explicitly state your uncertainty. Honesty over optimism.