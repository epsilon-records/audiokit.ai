# AI Comment Guidelines

## Overview

The `<!--ai-ignore ... ai-ignore-->` comment syntax is used within `<ai_instruction>` blocks to provide human context without affecting AI processing. This document outlines when and how to use these comments effectively.

## When to Use AI Comments

1. **Meta Documentation**
   - Version information
   - Last update timestamps
   - Author information
   - Change history

2. **Context & Rationale**
   - Explaining why a rule exists
   - Providing background information
   - Describing the impact of guidelines

3. **Implementation Notes**
   - How to test AI processing
   - Known limitations or edge cases
   - Integration considerations

4. **Future Plans**
   - Planned updates
   - Deprecated rules
   - Migration notes

## Comment Structure

```
<!--ai-ignore
[Category/Purpose]
- Key point or explanation
- Additional context
- Impact or consequences
Last updated: [Date]
ai-ignore-->
```

## Best Practices

1. **Keep Comments Focused**
   - One topic per comment block
   - Clear and concise explanations
   - Directly related to surrounding content

2. **Update Regularly**
   - Include timestamps
   - Note significant changes
   - Remove outdated information

3. **Provide Context**
   - Explain "why" not just "what"
   - Include examples where helpful
   - Reference related documentation

4. **Avoid Recursion**
   - Don't reference AI processing logic
   - Keep meta-instructions in comments
   - Separate human and AI concerns

## Examples

1. Version Information:
```
<!--ai-ignore
Version: 1.0.0
Last updated: 2024-02-01
Changes: Initial implementation of coding standards
ai-ignore-->
```

2. Rule Context:
```
<!--ai-ignore
This security requirement comes from OWASP Top 10 2024
Critical for maintaining SOC 2 compliance
ai-ignore-->
```

3. Implementation Note:
```
<!--ai-ignore
Note: This section requires specific AI model capabilities
Test with both GPT-4 and Claude for consistent results
ai-ignore-->
```

## Integration with Tools

1. **IDE Support**
   - Configure syntax highlighting
   - Set up folding rules
   - Enable comment searching

2. **Documentation Tools**
   - Include comments in generated docs
   - Maintain comment formatting
   - Support markdown within comments

3. **Version Control**
   - Track comment changes
   - Include in code reviews
   - Maintain comment history

## Maintenance

1. **Regular Review**
   - Validate comment accuracy
   - Update outdated information
   - Remove unnecessary comments

2. **Consistency Checks**
   - Verify comment format
   - Check timestamp accuracy
   - Ensure proper closing tags

3. **Documentation Updates**
   - Sync with related docs
   - Update examples
   - Maintain best practices 