Generate comprehensive, production-ready test automation code based on:
1. Gherkin scenarios (Given/When/Then steps)
2. Enhanced element tracking data with comprehensive selector information
3. Framework-specific requirements and best practices

## Input Data Analysis
You will receive rich element tracking data including:
- **Element Library**: Comprehensive element details with attributes, position, accessibility info
- **Action Sequence**: Step-by-step interactions with timestamps and metadata
- **Framework Exports**: Pre-optimized selectors for specific automation frameworks
- **Selector Priorities**: data-testid > ID > name > aria-label > CSS classes > XPath

## Code Generation Standards

### 1. Selector Strategy (Priority Order)
- **Highest Priority**: data-testid, data-cy attributes (automation-friendly)
- **High Priority**: ID attributes (unique and stable)
- **Medium Priority**: name attributes (good for forms)
- **Lower Priority**: aria-label, role (accessibility-based)
- **Fallback**: CSS classes, XPath (use sparingly and make robust)

### 2. Framework-Specific Requirements

**Selenium (Python/Java):**
- Use WebDriverWait with expected_conditions
- Implement Page Object Model pattern
- Add proper exception handling
- Use By.CSS_SELECTOR for data-testid: `[data-testid='element-id']`

**Playwright (Python/JavaScript):**
- Use modern async/await patterns
- Leverage built-in auto-wait functionality
- Use data-testid selectors: `data-testid=element-id`
- Implement proper page object structure

**Cypress (JavaScript):**
- Use data-cy attributes: `[data-cy='element-id']`
- Implement proper command chaining
- Add custom commands for reusability
- Use cy.intercept() for API testing when applicable

**Robot Framework:**
- Create reusable keywords
- Use SeleniumLibrary with proper locator strategies
- Implement data-driven testing with variables

### 3. Code Structure Requirements
- **Imports**: Include all necessary dependencies
- **Setup/Teardown**: Proper test lifecycle management
- **Page Objects**: Separate element definitions from test logic
- **Helper Methods**: Reusable functions for common operations
- **Error Handling**: Try-catch blocks with meaningful error messages
- **Comments**: Clear documentation for complex logic
- **Constants**: URLs, timeouts, and configuration values

### 4. Production Ready Features
- **Robust Waits**: Explicit waits for element visibility/clickability
- **Error Recovery**: Graceful handling of common failures
- **Logging**: Appropriate logging for debugging
- **Configuration**: Parameterized for different environments
- **Assertions**: Clear, descriptive assertions with meaningful messages

### 5. Element Interaction Patterns
When using the provided element tracking data:
- Extract selectors from `element_library` and `framework_exports`
- Use `action_sequence` to understand the interaction flow
- Prioritize stable selectors over position-based ones
- Implement retries for flaky elements
- Add validation for element state before interaction

## Expected Output Format
Generate a complete, executable test file with:
1. All necessary imports and dependencies
2. Proper test class/function structure
3. Page object definitions (when applicable)
4. Step implementations matching Gherkin scenarios
5. Helper methods and utilities
6. Configuration and constants

**IMPORTANT GUIDELINES:**
- Prioritize maintainability over brevity
- Use meaningful variable and method names
- Include error messages that help with debugging
- Make the code self-documenting with clear structure
- Follow language/framework conventions and best practices
- Ensure code is ready to run without additional modifications