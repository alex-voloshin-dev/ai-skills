# Prompt Template Foundations

## Delimiter Conventions

Prefer strong delimiters so instructions, data, and examples cannot blur together.

Recommended defaults:

- XML tags for sections and untrusted content
- numbered examples for few-shot blocks
- fenced code blocks for schemas and literal snippets

Avoid:

- mixing delimiter styles without purpose
- putting user data inside instruction blocks
- relying only on markdown headings for isolation

## System Prompt Architecture

Recommended order:

1. identity
2. hard rules
3. reasoning or workflow protocol
4. domain context
5. response format
6. fallback behavior

This keeps non-negotiable rules early and output constraints near the end.

## Few-Shot Formatting

Best practices:

- use a consistent example structure
- include representative, edge, and adversarial examples
- stop at 3-5 examples unless evals justify more

## Chain-of-Thought Formatting

When CoT is necessary:

- separate reasoning from the final answer
- define the reasoning steps explicitly
- avoid exposing free-form reasoning where only the final structured answer is needed

Useful pattern:

```xml
<analysis>...</analysis>
<result>...</result>
```
