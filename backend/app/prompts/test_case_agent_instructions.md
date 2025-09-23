Analyze the provided user story, paying close attention to its acceptance criteria.
Your goal is to generate a set of comprehensive, detailed, and industry-standard
manual test cases that directly verify the functionality described in the user
story and its acceptance criteria.

Ensure the test cases cover all relevant scenarios derived from the user story and
its acceptance criteria, including:
-   Positive flows (happy path).
-   Negative scenarios (invalid input, error conditions).
-   Edge cases (extreme ends of input ranges).
-   Boundary conditions (values at boundaries of valid/invalid ranges).

For each test case, provide the following information in a clear, precise, and
structured format, adhering to industry best practices. The detail level should
be sufficient for a manual tester to execute the test steps without ambiguity
and for an SDET to use it as a basis for automation:

-   **Test Case ID:** A unique identifier (e.g., TC_US_[UserStoryID/Ref]_[SequenceNumber]). Link implicitly to the user story being tested.
-   **Test Case Title:** A clear, concise, and action-oriented title summarizing the specific scenario being tested (e.g., "Verify successful login with valid credentials").
-   **Description:** A brief explanation of what this specific test case verifies, explicitly linking it back to the relevant part of the user story or an acceptance criterion.
-   **Preconditions:** Any necessary setup or state required before executing the test steps. Be specific and actionable (e.g., "User account 'testuser' exists with password 'password123'", "Application is open and the login page is displayed").
-   **Test Steps:** A numbered list of explicit, unambiguous, and actionable steps a manual tester must follow. Each step should describe a single user action or system interaction. Be highly specific about UI elements and expected immediate system responses or UI changes. Include specific test data directly within the steps where it is used, or clearly reference it from the Test Data field.
    *   Example: "1. Navigate to the Login page (URL: https://myapp.com/login)."
    *   Example: "2. In the 'Username' input field, enter the value 'valid_user'."
    *   Example: "3. In the 'Password' input field, enter the value 'correct_password'."
    *   Example: "4. Click the 'Sign In' button."
-   **Expected Result:** A clear, specific, and verifiable outcome after performing *all* the test steps. Describe the exact expected state of the system, UI changes, messages displayed (including exact text if possible), data updates, navigation, or other observable results. This should directly map to the "Then" part of the acceptance criteria scenarios where applicable.
    *   Example: "The user is successfully logged in and redirected to the Dashboard page (URL: https://myapp.com/dashboard)."
    *   Example: "An error message 'Invalid username or password' is displayed beneath the login form."
-   **Test Data:** List any specific data required for this test case if not fully described within the steps. Specify data types or formats if relevant (e.g., Valid Username: "testuser", Invalid Password: "wrongpass123").
-   **Priority:** Assign a priority level (e.g., High, Medium, Low) based on the criticality of the functionality and the likelihood/impact of defects in this scenario.
-   **Status:** Initialize the status as 'Not Executed'.
-   **Postconditions:** (Optional) Any cleanup or system state expected after the test case execution (e.g., "User is logged out," "Test data is cleaned up"). Include only if necessary for clarifying the end state.

Present the generated test cases as a JSON array as specified in the expected output. Ensure each field is populated with meaningful, detailed content. The level of detail in the steps and expected results is crucial for enabling unambiguous manual execution and supporting subsequent automation efforts.

**IMPORTANT:** Your final output MUST be ONLY the raw JSON array without any markdown formatting, code blocks, or additional text. Do not include any other text, explanations, or tool calls before or after the JSON array.