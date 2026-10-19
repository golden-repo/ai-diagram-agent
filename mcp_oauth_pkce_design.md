# MCP Server via MCP Gateway with OAuth 2.1 + PKCE

I need a sequence diagram showing how to consume an MCP (Model Context Protocol) server through an MCP Gateway using OAuth 2.1 with PKCE flow.

The authentication and request flow includes:
1. Client Application generates a code verifier and code challenge (PKCE)
2. Client initiates OAuth authorization request to Authorization Server with code challenge
3. User authenticates and authorizes the application
4. Authorization Server returns authorization code to Client
5. Client exchanges authorization code + code verifier for access token
6. Authorization Server validates and returns access token
7. Client sends MCP request to MCP Gateway with access token
8. MCP Gateway validates the access token
9. MCP Gateway forwards request to MCP Server
10. MCP Server processes the request and returns response
11. MCP Gateway returns response to Client

Show all participants: Client Application, Authorization Server, MCP Gateway, and MCP Server.
Include PKCE-specific steps (code verifier, code challenge).

Output: Mermaid
GenerateImage: Yes
