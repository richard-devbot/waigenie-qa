Analyze the provided input, which is a set of detailed manual test cases.
Each manual test case represents a specific scenario or example of how the
system should behave based on the original user story and its acceptance criteria.

Your task is to convert these manual test cases into comprehensive and
well-structured Gherkin scenarios and scenario outlines within a single
Feature file.

**Best Practices for Gherkin Generation:**

1.  **Feature Description:** Start the output with a clear and concise `Feature:` description that summarizes the overall functionality being tested. This should align with the user story's main goal.
2.  **Scenario vs. Scenario Outline:**
    *   Use a `Scenario:` for individual test cases that cover a unique flow or specific set of inputs/outcomes.
    *   Use a `Scenario Outline:` when multiple manual test cases cover the *same* workflow or steps but with *different test data* (inputs and potentially expected simple outcomes). Extract the varying data into an `Examples:` table below the Scenario Outline and use placeholders (< >) in the steps. This promotes the DRY (Don't Repeat Yourself) principle.
3.  **Descriptive Titles:** Use clear, concise, and action-oriented titles for both `Scenario` and `Scenario Outline`, derived from the manual test case titles or descriptions. The title should quickly convey the purpose of the scenario.
4.  **Tags:** Apply relevant and meaningful `@tags` above each Scenario or Scenario Outline (e.g., `@smoke`, `@regression`, `@login`, `@negative`, `@boundary`). Consider tags based on the test case type, priority, or related feature area to aid in test execution filtering and reporting.
5.  **Structured Steps (Given/When/Then/And/But):**
    *   `Given`: Describe the initial context or preconditions required to perform the test. **The first Given step MUST ALWAYS specify the entry point URL** using the format: "Given I am on "[full URL]"" (e.g., "Given I am on "https://www.example.com""). Additional Given steps can include other preconditions (e.g., "Given the user is logged in", "Given the product is out of stock").
    *   `When`: Describe the specific action or event that triggers the behavior being tested (e.g., "When the user adds the item to the cart", "When invalid credentials are provided"). There should ideally be only one main `When` per scenario.
    *   `Then`: Describe the expected outcome or result after the action is performed. This verifies the behavior (e.g., "Then the item should appear in the cart", "Then an error message should be displayed"). This should directly map to the Expected Result in the manual test case.
    *   `And` / `But`: Use these to extend a previous Given, When, or Then step. `And` is typically for additive conditions or actions, while `But` can be used for negative conditions (though `And not` is often clearer). Limit the number of `And` steps to maintain readability.
6.  **Level of Abstraction (What, Not How):** Write Gherkin steps at a high level, focusing on the *intent* and *behavior* (what the system does or what the user achieves) rather than the technical implementation details (how it's done, e.g., "click button X", "fill field Y"). Abstract away UI interactions where possible, but ensure steps are specific enough for automation tools to identify elements reliably.
7.  **Automation-Friendly Language:** Use consistent terminology that translates well to automation:
    *   "user enters [value] in the [field name] field" (clear element identification)
    *   "user clicks the [button name] button" (specific action and target)
    *   "system displays [expected text/message]" (clear verification points)
    *   "user navigates to [page/section]" (clear navigation steps)
    *   **IMPORTANT:** Always include a specific entry point URL in the first Given step of each scenario using the format: "Given I am on "[full URL]"" (e.g., "Given I am on "https://www.example.com"")
8.  **Element Identification Hints:** When referring to UI elements, use names or descriptions that help automation tools locate them (e.g., "login button", "username field", "error message", "dashboard page").
9.  **Clarity and Readability:** Use plain, unambiguous language that is easy for both technical and non-technical team members to understand. Avoid technical jargon. Maintain consistent phrasing. Use empty lines to separate scenarios for better readability.
10. **Background:** If multiple scenarios within the feature file share the same initial preconditions, consider using a `Background:` section at the top of the feature file. This reduces repetition but ensure it doesn't make scenarios harder to understand.
11. **Traceability (Optional but Recommended):** If the manual test cases reference user story or requirement IDs (e.g., Jira IDs), you can include these as tags or comments (using `#`) near the Feature or Scenario title for traceability.

Convert each relevant manual test case into one or more Gherkin scenarios/scenario outlines based on the above principles. Ensure the generated Gherkin accurately reflects the preconditions, steps, and expected results described in the manual test cases, while elevating the level of abstraction.

**IMPORTANT:** Your final output MUST be ONLY the JSON array of Gherkin scenarios without any markdown formatting, code blocks, or additional text. Do not include any other text, explanations, or tool calls before or after the JSON array.