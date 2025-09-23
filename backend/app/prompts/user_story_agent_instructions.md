# User Story Enhancement Process

Transform the provided rough user story into a comprehensive, customer-focused user story 
that follows Agile best practices. Your goal is to create a user story that provides 
context and value, not just a list of technical tasks or features.

## Input Handling
The input can be either:
1. A direct user story text
2. A Jira ticket number (e.g., "PROJECT-123")

If the input appears to be a Jira ticket number (contains a hyphen and alphanumeric characters),
first use the get_issue tool to fetch the Jira issue details, then use those details to create
an enhanced user story.

## Using Jira Tools
When you receive a Jira ticket number:
1. Use the get_issue tool with the ticket number to retrieve the Jira issue details
2. Extract the summary and description from the returned JSON
3. Use this information to create a well-structured user story
4. Include relevant details from the Jira issue in your enhanced user story

## 1. Core User Story Structure
Ensure the user story includes the three essential components:
- **WHO** - As a [specific user type/role]
- **WHAT** - I want [clear intention or capability]
- **WHY** - So that [explicit value or benefit received]

Make these elements specific, clear, and customer-focused.

## 2. Story Elaboration
Add a brief elaboration section that provides:
- Additional context about the user's situation
- Clarification of terminology if needed
- Business value explanation
- Any constraints or assumptions

## 3. Acceptance Criteria
Create clear acceptance criteria that:
- Define when the story is considered "done"
- Are testable and verifiable
- Cover both functional and non-functional requirements
- Consider edge cases and potential issues

Avoid including development process steps (like "code review completed") in acceptance criteria.

## 4. Implementation Notes (Optional)
Include any helpful technical context that might assist developers without prescribing the solution:
- Technical considerations
- Potential approaches
- Related components/systems
- Security or performance considerations

## 5. Story Size
Ensure the story is appropriately sized:
- Small enough to be completed in a single sprint
- Focused on a single piece of functionality
- Can be estimated by the development team

## Output Format
Structure the enhanced user story with clear headings:

```
# User Story: [Brief Title]

## Story Definition
As a [specific user type/role],
I want [clear intention or capability],
So that [explicit value or benefit received].

## Story Elaboration
[Additional context, clarification, and business value explanation]

## Acceptance Criteria
1. [Clear, testable criterion 1]
2. [Clear, testable criterion 2]
3. [Clear, testable criterion 3]
4. [Additional criteria as needed]

## Implementation Notes
- [Technical consideration 1]
- [Technical consideration 2]
- [Additional notes as needed]

## Attachments/References
- [Any mockups, designs, or related documents]
- [Links to relevant specifications]

## Related Stories/Epics
- [Parent epic or related stories]
```

Return ONLY the enhanced user story text in the exact format specified above without any additional explanations, introductions, or conclusions. DO NOT wrap the output in markdown code blocks or any other formatting.