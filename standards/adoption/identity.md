# OIDC and session adoption

Extends [SEC02 and SEC06](../operations/security.md) and the backend server authorization rules. Select the identity provider, exact HTTPS issuer and callback, application/API audiences, access-token format, client type and credential owner. Record tenant claim mapping, account lifecycle, TTLs, clock tolerance, rotation overlap, outage behavior and logout or revocation guarantee. Test against a distinct test application registration before promoting the configuration.

Use authorization code flow with PKCE and exact registered callbacks for interactive login. Associate state, nonce, issuer and return target with the initiating browser session. Protect the code exchange and refresh credentials on the server for the recommended same-origin backend-for-frontend binding. Use secure, HttpOnly cookies with deliberately selected SameSite and scope attributes. Use origin validation and CSRF protection for cookie-authenticated writes. Clear private UI and server state across logout or changes of identity or tenant.

For an API accepting JWT access tokens, pin issuer, audience, token purpose, permitted signature algorithms and trusted keys. Reject wrong, unknown or expired credentials at the boundary. Use the configured issuer's key source and bounded key refresh rather than following attacker-supplied key URLs. For opaque access tokens use the approved introspection path and bounded caching. Use OIDC ID tokens to establish login and apply the API's separate access-token policy. Map roles and tenant membership from verified authority and enforce access for each resource on the server.

| Case | Action and required evidence |
| --- | --- |
| ID01 | Complete login, cookie/session checks and logout on the approved issuer and application registration. Record callback and observed session lifecycle. |
| ID02 | Reject a mismatched callback, wrong state/nonce, invalid proof key and replayed authorization code. Demonstrate no session creation. |
| ID03 | Deny expired/wrong-issuer/wrong-audience credentials and an ID token presented to the API. Include disallowed algorithm, malformed token and wrong purpose for JWTs, or inactive/untrusted introspection for opaque tokens. |
| ID04 | Exercise role denial and cross-tenant access with direct API read/write attempts. Verify that no forbidden data is exposed or changed. |
| ID05 | Rotate keys or credentials and exercise provider/key service loss. Record bounded verification and recovery and the effective revocation window. |
| ID06 | Exercise cross-origin state change, session expiry, logout and tenant switch. Verify cache/credential cleanup and sanitized logs. |

Primary sources for protocol behavior and threat guidance. [IETF OAuth Security BCP](https://www.rfc-editor.org/rfc/rfc9700.html) · [IETF JWT BCP](https://www.rfc-editor.org/rfc/rfc8725.html) · [OpenID Connect Core, errata set 2](https://openid.net/specs/openid-connect-core-1_0-errata2.html)
