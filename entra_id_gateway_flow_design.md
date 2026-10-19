# API Gateway with Entra ID Authentication Flow

I need a sequence diagram showing the authentication and API call flow.

The process steps are:
1. Consumer Application requests an access token from Microsoft Entra ID (Azure AD)
2. Entra ID validates credentials and returns an access token
3. Consumer Application calls the API Gateway with the access token in the Authorization header
4. API Gateway validates the token with Entra ID (JWT validation)
5. If token is valid, Gateway forwards the request to the Backend API
6. Backend API processes the request and returns response to Gateway
7. Gateway returns the response back to Consumer Application
8. If token is invalid, Gateway returns 401 Unauthorized error to Consumer

Show the complete flow with all participants: Consumer Application, Entra ID, API Gateway, and Backend API.

Output: Mermaid
GenerateImage: Yes
