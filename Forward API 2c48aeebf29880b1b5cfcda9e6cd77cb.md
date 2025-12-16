# Forward API

# Using Variables in Forward API Requests

Variables allow you to define reusable values that can be referenced throughout your request. They are processed before the request body, headers, and query parameters, making them ideal for building complex data structures or combining multiple values.

## How to Use Variables

Variables are defined in the `variables` array within your `destination_request`. Each variable has a `name` and a `value`. Once defined, you can reference them anywhere in your request using the syntax:

```
{{ variable_name }}

```

## Key Features

- **Reusability**: Define a value once and use it multiple times throughout your request
- **Composition**: Combine multiple card data fields or other values into a single variable
- **Order of Processing**: Variables are processed first, so they can be used in the body, headers, and query parameters

## Example Request

```bash
curl --location --request POST '<https://forward.sandbox.checkout.com/forward>' \\
--header 'Authorization: Bearer <YOUR_ACCESS_TOKEN>' \\
--header 'Content-Type: application/json' \\
--data '{
    "source": {
        "type": "id",
        "id": "src_xxxxxxxxxxxxxxxxxxxxxxxxxx"
    },
    "reference": "your-reference",
    "processing_channel_id": "pc_xxxxxxxxxxxxxxxxxxxxxxxxxx",
    "destination_request": {
        "url": "<https://api.example.com/v1/endpoint>",
        "method": "POST",
        "headers": {
            "raw": {
                "Content-Type": "application/json",
                "X-Expiry-Date": "{{ formatted_expiry }}"
            }
        },
        "body": "{ \\"card\\": { \\"number\\": \\"{{ card_number }}\\", \\"expiry\\": \\"{{ formatted_expiry }}\\", \\"cvv\\": \\"{{ card_cvv }}\\" }, \\"cardData\\": \\"{{ card_payload }}\\" }",
        "variables": [
            {
                "name": "formatted_expiry",
                "value": "{{ card_expiry_month }}/{{ card_expiry_year_yy }}"
            },
            {
                "name": "card_payload",
                "value": "{\\"pan\\":\\"{{ card_number }}\\",\\"expiryMonth\\":\\"{{ card_expiry_month }}\\",\\"expiryYear\\":\\"{{ card_expiry_year_yyyy }}\\"}"
            }
        ]
    }
}'

```

## Available Card Data Fields

You can use these built-in fields when defining variables:

| Field | Description | Example |
| --- | --- | --- |
| `{{ card_number }}` | Full card number | `4111111111111111` |
| `{{ card_expiry_month }}` | Expiry month | 8 |
| `{{ card_expiry_month_mm }}` | 2-digit expiry month | 08 |
| `{{ card_expiry_year_yy }}` | 2-digit expiry year | `25` |
| `{{ card_expiry_year_yyyy }}` | 4-digit expiry year | `2025` |
| `{{ card_cvv }}` | Card CVV | `123` |
| `{{ cardholder_name }}` | Cardholder name | `John Doe` |

---

# Using Query Parameters in Forward API Requests

Query parameters allow you to append key-value pairs to your destination URL. They are automatically appended to the URL when the request is sent to the destination.

## How to Use Query Parameters

Query parameters are defined in the `query` array within your `destination_request`. Each parameter has a `name` and a `value`. You can use static values or template expressions to inject dynamic values.

For example, if your destination URL is:

```
<https://api.example.com/v1/charges>

```

And you define query parameters, the final URL becomes:

```
<https://api.example.com/v1/charges?merchantId=12345&version=2024-01&cardBin=411111>

```

## Key Features

- **Dynamic Values**: Query parameter values support template expressions
- **Variable Support**: You can reference variables defined in the `variables` array
- **Automatic URL Encoding**: Values are properly encoded when appended to the URL

## Example Request

```bash
curl --location --request POST '<https://forward.sandbox.checkout.com/forward>' \\
--header 'Authorization: Bearer <YOUR_ACCESS_TOKEN>' \\
--header 'Content-Type: application/json' \\
--data '{
    "source": {
        "type": "id",
        "id": "src_xxxxxxxxxxxxxxxxxxxxxxxxxx"
    },
    "reference": "your-reference",
    "processing_channel_id": "pc_xxxxxxxxxxxxxxxxxxxxxxxxxx",
    "destination_request": {
        "url": "<https://api.example.com/v1/charges>",
        "method": "POST",
        "headers": {
            "raw": {
                "Content-Type": "application/json"
            }
        },
        "body": "{ \\"amount\\": 1000, \\"currency\\": \\"USD\\" }",
        "variables": [
            {
                "name": "card_bin",
                "value": "{{ card_number }}"
            }
        ],
        "query": [
            {
                "name": "merchantId",
                "value": "12345"
            },
            {
                "name": "version",
                "value": "2024-01"
            },
            {
                "name": "cardBin",
                "value": "{{ card_bin }}"
            },
            {
                "name": "expiryYear",
                "value": "{{ card_expiry_year_yyyy }}"
            }
        ]
    }
}'

```

---

# Using JWE Encryption in Forward API Requests

JWE (JSON Web Encryption) allows you to encrypt sensitive data within your request using a public key.

## How to Use JWE Encryption

The `jwe_encrypt` function is available within your templates. It takes 4 required parameters and 1 optional parameter:

```
{{ jwe_encrypt(data=data_to_encrypt, key=encryption_key, alg='RSA-OAEP', enc='A256GCM', headers=custom_headers) }}

```

| Parameter | Description | Example Values |
| --- | --- | --- |
| `data` | The data to encrypt (typically a variable containing card data) | `card_payload` |
| `key` | The encryption key in JWK format (RSA public key or symmetric key) | `jwk_key` |
| `alg` | Key encryption algorithm | `RSA-OAEP`, `RSA-OAEP-256`, `A256GCMKW` |
| `enc` | Content encryption algorithm | `A256GCM`, `A128GCM`, `A256CBC-HS512` |
| `headers` | (Optional) Additional JWE headers as JSON | `{"kid":"key-id","iat":1234567890}` |

## Supported Algorithms

| Algorithm Type | Supported Values |
| --- | --- |
| **Key Encryption** | `RSA-OAEP`, `RSA-OAEP-256`, `A256GCMKW` |
| **Content Encryption** | `A128GCM`, `A256GCM`, `A128CBC-HS256`, `A256CBC-HS512` |

## Examples

### Using Asymmetric Key Encryption

For RSA-based encryption, provide the public key in JWK format:

```bash
curl --location --request POST '<https://forward.sandbox.checkout.com/forward>' \\
--header 'Authorization: Bearer <YOUR_ACCESS_TOKEN>' \\
--header 'Content-Type: application/json' \\
--data '{
    "source": {
        "type": "id",
        "id": "src_xxxxxxxxxxxxxxxxxxxxxxxxxx"
    },
    "reference": "your-reference",
    "processing_channel_id": "pc_xxxxxxxxxxxxxxxxxxxxxxxxxx",
    "destination_request": {
        "url": "<https://api.example.com/v1/endpoint>",
        "method": "POST",
        "headers": {
            "raw": {
                "Content-Type": "application/json"
            }
        },
        "body": "{ \\"encryptedCard\\": \\"{{ jwe_encrypt(data=card_data, key=public_key, alg='\\''RSA-OAEP'\\'', enc='\\''A256GCM'\\'') }}\\"}",
        "variables": [
            {
                "name": "card_data",
                "value": "{\\"primaryAccountNumber\\":\\"{{ card_number }}\\",\\"panExpirationMonth\\":\\"{{ card_expiry_month }}\\",\\"panExpirationYear\\":\\"{{ card_expiry_year_yyyy }}\\",\\"cvv\\":\\"{{ card_cvv }}\\"}"
            },
            {
                "name": "public_key",
                "value": "{ \\"kty\\": \\"RSA\\", \\"e\\": \\"AQAB\\", \\"use\\": \\"enc\\", \\"kid\\": \\"key-001\\", \\"alg\\": \\"RSA-OAEP\\", \\"n\\": \\"your-public-key-modulus\\" }"
            }
        ]
    }
}'

```

### Using Symmetric Key Encryption

For destinations that require symmetric key encryption, use algorithms like `A256GCMKW`. This requires a 256-bit (32 bytes) symmetric key encoded in base64url format.

The symmetric key must be provided as a JWK with the `k` parameter containing the base64url-encoded key:

```json
{
    "kty": "oct",
    "k": "<base64url-encoded-256-bit-key>"
}
```

> **Note**: Some APIs require the key to be derived as `base64url(sha256(<shared-secret>))`. Check your destination API documentation for the exact key derivation requirements.

```bash
curl --location --request POST '<https://forward.sandbox.checkout.com/forward>' \\
--header 'Authorization: Bearer <YOUR_ACCESS_TOKEN>' \\
--header 'Content-Type: application/json' \\
--data '{
    "source": {
        "type": "id",
        "id": "src_xxxxxxxxxxxxxxxxxxxxxxxxxx"
    },
    "reference": "your-reference",
    "processing_channel_id": "pc_xxxxxxxxxxxxxxxxxxxxxxxxxx",
    "destination_request": {
        "url": "<https://api.example.com/v1/tokenize>",
        "method": "POST",
        "headers": {
            "raw": {
                "Content-Type": "application/json"
            }
        },
        "body": "{ \\"encryptedPayload\\": \\"{{ jwe_encrypt(data=payment_data, key=symmetric_key, alg='\\''A256GCMKW'\\'', enc='\\''A256GCM'\\'', headers=jwe_headers) }}\\"}",
        "variables": [
            {
                "name": "payment_data",
                "value": "{\\"accountNumber\\":\\"{{ card_number }}\\",\\"expirationMonth\\":\\"{{ card_expiry_month }}\\",\\"expirationYear\\":\\"{{ card_expiry_year_yyyy }}\\"}"
            },
            {
                "name": "symmetric_key",
                "value": "{ \\"kty\\": \\"oct\\", \\"k\\": \\"<your-base64url-encoded-256-bit-key>\\" }"
            },
            {
                "name": "jwe_headers",
                "value": "{ \\"kid\\": \\"your-key-id\\", \\"iat\\": 1234567890 }"
            }
        ]
    }
}'

```

## How It Works

1. **Define the data to encrypt**: Create a variable (`card_data`) containing the JSON payload with card details
2. **Define the encryption key**: Create a variable (`public_key` or `symmetric_key`) with the JWK key provided by the destination
3. **Call the function**: Use `jwe_encrypt(data=card_data, key=public_key, alg='RSA-OAEP', enc='A256GCM')` in your body template
4. **Result**: The function returns the encrypted JWE token string that replaces the placeholder

---

# Storing and Using Secrets

The Forward API provides endpoints for securely storing and managing sensitive data. This allows you to store credentials, API keys, encryption keys, and other sensitive values that can be referenced in your Forward API requests without exposing them in the request payload.

## Storing Secrets

Store a secret by providing a unique name and the sensitive value.

```bash
curl --location --request POST 'https://forward.sandbox.checkout.com/secrets' \
--header 'Authorization: Bearer <YOUR_ACCESS_TOKEN>' \
--header 'Content-Type: application/json' \
--data '{
    "name": "my-api-key",
    "value": "sk_live_xxxxxxxxxxxxxxxxxxxxx"
}'

```

**Response:**

```json
{
    "id": "sec_xxxxxxxxxxxxxxxxxxxxxxxxxx",
    "name": "my-api-key",
    "created_at": "2024-01-15T10:30:00Z"
}
```

---

## Using Secrets in Forward API Requests

Once a secret is stored, you can reference it in your Forward API requests using the `{{ secret_<secret_name> }}` syntax. The secret value will be securely injected at runtime.

### Example: Using a Stored API Key in Headers

```bash
curl --location --request POST 'https://forward.sandbox.checkout.com/forward' \
--header 'Authorization: Bearer <YOUR_ACCESS_TOKEN>' \
--header 'Content-Type: application/json' \
--data '{
    "source": {
        "type": "id",
        "id": "src_xxxxxxxxxxxxxxxxxxxxxxxxxx"
    },
    "reference": "your-reference",
    "processing_channel_id": "pc_xxxxxxxxxxxxxxxxxxxxxxxxxx",
    "destination_request": {
        "url": "https://api.example.com/v1/charges",
        "method": "POST",
        "headers": {
            "raw": {
                "Content-Type": "application/json",
                "Authorization": "{{ secret_destination-api-key }}"
            }
        },
        "body": "{ \"amount\": 1000, \"currency\": \"USD\", \"card\": { \"number\": \"{{ card_number }}\", \"expiry_month\": \"{{ card_expiry_month }}\", \"expiry_year\": \"{{ card_expiry_year_yyyy }}\", \"cvv\": \"{{ card_cvv }}\" } }"
    }
}'

```

### Example: Using a Stored Encryption Key with JWE

You can reference secrets within variables to use them with functions like `jwe_encrypt`:

```bash
curl --location --request POST 'https://forward.sandbox.checkout.com/forward' \
--header 'Authorization: Bearer <YOUR_ACCESS_TOKEN>' \
--header 'Content-Type: application/json' \
--data '{
    "source": {
        "type": "id",
        "id": "src_xxxxxxxxxxxxxxxxxxxxxxxxxx"
    },
    "reference": "your-reference",
    "processing_channel_id": "pc_xxxxxxxxxxxxxxxxxxxxxxxxxx",
    "destination_request": {
        "url": "https://api.example.com/v1/tokenize",
        "method": "POST",
        "headers": {
            "raw": {
                "Content-Type": "application/json"
            }
        },
        "body": "{ \"encryptedCard\": \"{{ jwe_encrypt(data=card_data, key=encryption_key, alg='\''RSA-OAEP'\'', enc='\''A256GCM'\'') }}\"}",
        "variables": [
            {
                "name": "card_data",
                "value": "{\"primaryAccountNumber\":\"{{ card_number }}\",\"panExpirationMonth\":\"{{ card_expiry_month }}\",\"panExpirationYear\":\"{{ card_expiry_year_yyyy }}\"}"
            },
            {
                "name": "encryption_key",
                "value": "{{ secret_partner-public-key }}"
            }
        ]
    }
}'

```

## Secret Reference Syntax

| Syntax | Description | Example |
| --- | --- | --- |
| `{{ secret_<name> }}` | References a stored secret by its name | `{{ secret_my-api-key }}` |
