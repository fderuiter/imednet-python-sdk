# Authentication

Authenticate your account using one of the methods outlined below. The response returns a session ID that you can use in subsequent API calls. Session IDs time out after a period of inactivity, which varies by Vault. Learn more about session duration and management.

After acquiring a Vault Session ID, include it on every subsequent API call inside the Authorization HTTP request header.

## Basic Authorization

| Name | Description |
| ---- | ----------- |
| Authorization | {sessionId} |

Alternatively, you can use Salesforce™ or OAuth2/OIDC Delegated Requests.

Vault API also accepts Vault Session IDs as Bearer tokens. Include Bearer keyword to send Vault Session IDs with as bearer tokens:

## Bearer Token Authorization

| Name | Description |
| ---- | ----------- |
| Authorization | Bearer {sessionId} |

## User Name and Password

### Request

```bash
curl -X POST https://myvault.veevavault.com/api/v24.3/auth \
-H "Content-Type: application/x-www-form-urlencoded" \
-H "Accept: application/json" \
-d "username={username}&password={password}"
```

### Response

```json
{
  "responseStatus": "SUCCESS",
  "sessionId": "3B3C45FD240E26F0C3DB4F82BBB0C15C7EFE4B29EF9916AF41AF7E44B170BAA01F232B462BE5C2BE2ACB82F6704FDA216EBDD69996EB23A6050723D1EFE6FA2B",
  "userId": 12021,
  "vaultIds": [
    {
      "id": 1776,
      "name": "PromoMats",
      "url": "https://promomats-veevapharm.veevavault.com/api"
    },
    {
      "id": 1777,
      "name": "eTMF",
      "url": "https://etmf-veevapharm.veevavault.com/api"
    },
    {
      "id": 1779,
      "name": "QualityDocs",
      "url": "https://qualitydocs-veevapharm.veevavault.com/api"
    }
  ],
  "vaultId": 1776
}
```

Authenticate your account using your Vault user name and password to obtain a Vault Session ID.

If the specified user cannot successfully authenticate to the given vaultDNS, the subdomain is considered invalid and this request instead generates a session for the user’s most relevant available Vault. A DNS is considered invalid for the given user if the user cannot access any Vaults in that subdomain, for example, if the user does not exist in that DNS or if all Vaults in that DNS are inactive. For this reason, it is best practice to inspect the response, compare the desired Vault ID with the list of returned Vault IDs, and confirm the DNS matches the expected login.

Vault limits the number of Authentication API calls based on the user name and the domain name used in the API call. To determine the Vault Authentication API burst limit for your Vault or the length of delay for a throttled response, check the response headers or the API Usage Logs.

**Endpoint:** `POST https://{vaultDNS}/api/{version}/auth`

### Headers

| Name | Description |
| ---- | ----------- |
| Content-Type | multipart/form-data or application/x-www-form-urlencoded |
| Accept | application/json (default) or application/xml |

### URI Path Parameters

| Name | Description |
| ---- | ----------- |
| vaultDNS | The DNS of the Vault for which you want to generate a session. If the requesting user cannot successfully authenticate to this vaultDNS, this request generates a session for the user’s most relevant available Vault. |
| version | The Vault API version. Your authentication version does not need to match the version in subsequent calls. For example, you can authenticate with v17.3 and run your integrations with v20.1. |

### Body Parameters

| Name | Description |
| ---- | ----------- |
| username | required: Your Vault user name assigned by your administrator. |
| password | required: Your Vault password associated with your assigned Vault user name. |
| vaultDNS | optional: The DNS of the Vault for which you want to generate a session. If specified, this optional vaultDNS body parameter overrides the value in the URI vaultDNS. If the requesting user cannot successfully authenticate to this vaultDNS, this request generates a session for the user’s most relevant available Vault. If this vaultDNS body parameter is omitted, this request instead generates a session for the domain specified in the URI vaultDNS. |

### Response Details

On SUCCESS, this request returns a valid sessionId for any Vault DNS where the user has access.

The Vault DNS for the returned session is calculated in the following order:

1. Generates a session for the DNS in the optional vaultDNS body parameter
2. If this vaultDNS is invalid, generates a session for the user’s most relevant available Vault:
   - Generates a session for the Vault where the user last logged in
   - If the user has never logged in, or if the last logged-in Vault is inactive, generates a session for the oldest active Vault where that user is a member
   - If the user is not a member of any active Vaults, the user cannot authenticate and the API returns FAILURE
3. If the optional vaultDNS body parameter is omitted, generates a session for the DNS specified in the vaultDNS URI parameter
4. If this vaultDNS is invalid, generates a session for the user’s most relevant available Vault:
   - Generates a session for the Vault where the user last logged in
   - If the user has never logged in, or if the last logged-in Vault is inactive, generates a session for the oldest active Vault where that user is a member
   - If the user is not a member of any active Vaults, the user cannot authenticate and the API returns FAILURE

An invalid DNS is any DNS which the specified user cannot access, for example, if the DNS does not exist, if the user does not exist in that DNS, or if all Vaults in that DNS are inactive.

It is best practice to inspect the response, compare the desired Vault ID with the list of returned vaultIds, and confirm the DNS matches the expected login.

This API only returns FAILURE if it is unable to return a valid sessionId for any Vault the user can access.

## Session Keep Alive

### Request - Session Keep Alive

```bash
curl -X GET -H "Authorization: {SESSION_ID}" \
https://myvault.veevavault.com/api/v24.3/keep-alive
```

### Response - Session Keep Alive

```json
{
   "responseStatus": "SUCCESS"
}
```

Given an active sessionId, keep the session active by refreshing the session duration.

A Vault session is considered active as long as some activity (either through the UI or API) happens within the maximum inactive session duration. This maximum inactive session duration varies by Vault and is configured by your Vault Admin. The maximum active session duration is 48 hours, which is not configurable. Learn more about best practices for session management.

**Endpoint:** `POST /api/{version}/keep-alive`

### Headers - Session Keep Alive

| Name | Description |
| ---- | ----------- |
| Accept | application/json (default) or application/xml |
| Authorization | The Vault sessionId to keep active. |

## End Session

### Request - End Session

```bash
curl -X DELETE -H "Authorization: {SESSION_ID}" \
https://myvault.veevavault.com/api/v24.3/session
```

### Response - End Session

```json
{
"responseStatus": "SUCCESS"
}
```

Given an active sessionId, inactivate an API session. If a user has multiple active sessions, inactivating one session does not inactivate all sessions for that user. Each session has its own unique sessionId.

**Endpoint:** `DELETE /api/{version}/session`

### Headers - End Session

| Name | Description |
| ---- | ----------- |
| Accept | application/json (default) or application/xml |
| Authorization | The Vault sessionId to end. |
