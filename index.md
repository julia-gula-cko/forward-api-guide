---
layout: default
title: Forward API - Forward Stored Credentials
---

# Forward Stored Credentials

Use the [Forward API](https://api-reference.checkout.com/#tag/Forward) to enrich a payment request with payment credentials you've stored in the Checkout.com Vault. You can enrich a payment with:

- The billing information stored in a payment instrument or token
- The card details stored in an instrument or token
- The details of a network token

The request is then securely forwarded to your specified third-party API endpoint. For example, you can forward the request to external fraud engines, 3D Secure (3DS) engines, and other payment services providers (PSPs) such as [Stripe](#stripe-forwarding-example) or [Adyen](#adyen-forwarding-example).

> **ℹ️ Info:** To enable forwarding, contact your account manager or [request support](https://dashboard.checkout.com/support/new?topic=case_configuration_change&issue=case_configuration_issue_operational_change_request).

This enables you to:

- Store payment credentials in a single location and use them across multiple PSPs, while remaining PCI compliant.
- Provide additional data to third-party fraud engines.
- Extract stored payment credentials from one client's vault and forward them to another client's vault, if you have a multi-client account structure.
- Provide card-linked offers to an issuer or card network.

> **ℹ️ Important:** You must ensure that the third-party endpoint you forward the request to belongs to a PCI-compliant entity.

---

## Table of Contents

- [Retrieve JSON Web Key](#retrieve-json-web-key)
- [Retrieve the instrument, token, or network token](#retrieve-the-instrument-token-or-network-token)
- [Create a forward request](#create-a-forward-request)
- [Building requests](#building-requests)
- [Secrets in Forward API](#secrets-in-forward-api)
- [Forwarding logic](#forwarding-logic)
- [Stripe forwarding example](#stripe-forwarding-example)
- [Adyen forwarding example](#adyen-forwarding-example)
- [Visa integration example](#visa-integration-example)
- [View forward request outcomes](#view-forward-request-outcomes)

---

## Retrieve JSON Web Key

You need Checkout.com's JSON Web Key (JWK) to encrypt sensitive request headers using JSON Web Encryption (JWE).

In your terminal, run the following command to retrieve our JWK:

```bash
curl --location 'https://forward.checkout.com/.well-known/jwks' \
--header 'Content-Type: application/json'
```

---

## Retrieve the instrument, token, or network token

Before you can create a forward request, retrieve the ID for the source of the stored credentials. This can be one of:

- A payment instrument ID you've created and stored in the Vault, prefixed with `src_`
- A token ID you've generated, prefixed with `tok_`

> **ℹ️ Note:** Tokens expire after 15 minutes. If you want to reuse the credentials in future payments, you can [convert a token into a payment instrument](https://api-reference.checkout.com/#operation/createAnInstrument).

---

## Create a forward request

Call the [Forward an API request](https://api-reference.checkout.com/#operation/forwardRequest) endpoint.

Authenticate the request using one of the following:
- Public key – If using an API key, we recommend encrypting it first.
- An API key
- An access key – If using OAuth 2.0 authentication

> **📝 Note:** Checkout.com does not store the API keys you provide in encrypted headers. We only use the key to process the request in which it's provided.

### Request body parameters

#### For a payment instrument

| Parameter | Description |
|-----------|-------------|
| `source.type` | Set to `id` |
| `source.id` | The payment instrument ID, prefixed with `src_` |
| `destination_request.url` | The third-party endpoint you want to forward the request to |
| `destination_request.method` | The HTTP method you want to use for the request |
| `destination_request.headers.raw` | The raw HTTP headers you want to include in the request |
| `destination_request.body` | The JSON payload formatted according to the key-value pairs expected by the destination PSP |

**Optional parameters:**
- `source.cvv_token` – The token ID for the card verification value (CVV), prefixed with `tok_`
- `source.pin_token` – The token ID for the card's personal identification number (PIN), prefixed with `tok_`

#### For a token

| Parameter | Description |
|-----------|-------------|
| `source.type` | Set to `token` |
| `source.token` | The token ID, prefixed with `tok_` |
| `destination_request.url` | The third-party endpoint you want to forward the request to |
| `destination_request.method` | The HTTP method you want to use for the request |
| `destination_request.headers.raw` | The raw HTTP headers you want to include in the request |
| `destination_request.body` | The JSON payload formatted according to the key-value pairs expected by the destination PSP |

**Optional:** `source.store_for_future_use` – Store the token as a payment instrument.

### Using network tokens

Network tokens enhance transaction security by replacing raw card details. This helps ensure compliance with PCI DSS standards and reduces the risk of fraud.

To process a request which includes network tokens, you must include the forwarding logic that checks they're available and the required fields to forward.

- Set the `network_token.enabled` field to `true`.
- Set the `network_token.request_cryptogram` field to:
  - `true` – For customer-initiated transactions (CITs)
  - `false` – For merchant-initiated transactions (MITs)

If a network token is unavailable, the Forward API falls back to using tokenized card details.

### Placeholder values

You can use the following placeholder values in the `destination_request.body` field. When the request is forwarded to the third-party endpoint, the placeholder values are replaced with the respective payment credentials.

#### Card details placeholders

{% raw %}
| Placeholder | Description |
|-------------|-------------|
| `{{card_cvv}}` | The card verification value (security code) |
| `{{card_expiry_month}}` | The card's expiry month (format: `MM`) |
| `{{card_expiry_year_yy}}` | The card's expiry year (format: `YY`) |
| `{{card_expiry_year_yyyy}}` | The card's expiry year (format: `YYYY`) |
| `{{card_number}}` | The full card number |
| `{{card_pin}}` | The first two digits of the card's PIN |
| `{{cardholder_name}}` | The cardholder's name as shown on the card |
{% endraw %}

#### Billing information placeholders

{% raw %}
| Placeholder | Description |
|-------------|-------------|
| `{{billing_address_city}}` | The city of the billing address |
| `{{billing_address_country}}` | The country of the billing address |
| `{{billing_address_line1}}` | The first line of the billing address |
| `{{billing_address_line2}}` | The second line of the billing address |
| `{{billing_address_state}}` | The state of the billing address |
| `{{billing_address_zip}}` | The ZIP code or post code of the billing address |
{% endraw %}

#### Network token placeholders

{% raw %}
| Placeholder | Description |
|-------------|-------------|
| `{{network_token_number}}` | The network token number from the card scheme |
| `{{network_token_type}}` | The type of network token (`mdes` for Mastercard, `vts` for Visa) |
| `{{network_token_cryptogram}}` | The token authentication verification value (TAVV) |
| `{{network_token_eci}}` | The Electronic Commerce Indicator (ECI) received from the issuer |
| `{{network_token_expiry_year_yy}}` | The network token's expiry year (format: `YY`) |
| `{{network_token_expiry_year_yyyy}}` | The network token's expiry year (format: `YYYY`) |
| `{{network_token_expiry_month}}` | The network token's expiry month (format: `MM`) |
{% endraw %}

> **ℹ️ Note:** If you use the Forward API to perform an authorization with a third party, you must handle any post-transaction actions directly with them (captures, refunds, disputes).

### API endpoints

| Environment | Endpoint |
|-------------|----------|
| **Production** | `POST https://forward.checkout.com/forward` |
| **Sandbox** | `POST https://forward.sandbox.checkout.com/forward` |

### Request example

{% raw %}
```json
{
  "source": {
    "type": "id",
    "id": "src_wmlfc3zyhqzehihu7giusaaawu"
  },
  "reference": "ORD-5023-4E89",
  "processing_channel_id": "pc_azsiyswl7bwe2ynjzujy7lcjca",
  "destination_request": {
    "url": "string",
    "method": "POST",
    "headers": {
      "encrypted": "<JWE encrypted key-value object>",
      "raw": {
        "Idempotency-Key": "xe4fad12367dfgrds",
        "Content-Type": "application/json"
      }
    },
    "body": "{\"amount\": 1000,\"currency\": \"USD\",\"reference\": \"Test\",\"source\": {\"type\": \"card\",\"number\": \"{{card_number}}\",\"expiry_month\": \"{{card_expiry_month}}\",\"expiry_year\": \"{{card_expiry_year_yyyy}}\",\"name\": \"John Smith\"},\"payment_type\": \"Regular\",\"authorization_type\": \"Final\",\"capture\": true,\"processing_channel_id\": \"pc_xxxxxxxxxxx\",\"risk\": {\"enabled\": false},\"merchant_initiated\": true}"
  }
}
```
{% endraw %}

### Response example

```json
{
  "request_id": "fwd_5fa7ee8c-f82d-4440-a6dc-e8c859b03235",
  "destination_response": {
    "status": 201,
    "headers": {
      "Cko-Request-Id": "5fa7ee8c-f82d-4440-a6dc-e8c859b03235",
      "Content-Type": "application/json"
    },
    "body": "{ \"id\": \"pay_mbabizu24mvu3mela5njyhpit4\", \"action_id\": \"act_mbabizu24mvu3mela5njyhpit4\", \"amount\": 6540,\"currency\": \"USD\", \"approved\": true,\"status\": \"Authorized\" }"
  }
}
```

If you receive a `200` response, the request was successfully forwarded to the specified third-party endpoint.

---

## Building requests

You can use variables, query parameters, and JWE encryption to build complex requests for your destination endpoints.

### Variables

Variables allow you to define reusable values that can be referenced throughout your request. They are processed before the request body, headers, and query parameters.

Variables are defined in the `variables` array within your `destination_request`. Each variable has a `name` and a `value`. Once defined, you can reference them anywhere using the syntax {% raw %}`{{ variable_name }}`{% endraw %}.

#### Request example with variables

{% raw %}
```json
{
  "source": {
    "type": "id",
    "id": "src_xxxxxxxxxxxxxxxxxxxxxxxxxx"
  },
  "reference": "your-reference",
  "processing_channel_id": "pc_xxxxxxxxxxxxxxxxxxxxxxxxxx",
  "destination_request": {
    "url": "https://api.example.com/v1/endpoint",
    "method": "POST",
    "headers": {
      "raw": {
        "Content-Type": "application/json",
        "X-Expiry-Date": "{{ formatted_expiry }}"
      }
    },
    "body": "{ \"card\": { \"number\": \"{{ card_number }}\", \"expiry\": \"{{ formatted_expiry }}\", \"cvv\": \"{{ card_cvv }}\" }, \"cardData\": \"{{ card_payload }}\" }",
    "variables": [
      {
        "name": "formatted_expiry",
        "value": "{{ card_expiry_month }}/{{ card_expiry_year_yy }}"
      },
      {
        "name": "card_payload",
        "value": "{\"pan\":\"{{ card_number }}\",\"expiryMonth\":\"{{ card_expiry_month }}\",\"expiryYear\":\"{{ card_expiry_year_yyyy }}\"}"
      }
    ]
  }
}
```
{% endraw %}

### Query parameters

Query parameters allow you to append key-value pairs to your destination URL. They are automatically appended to the URL when the request is sent.

For example, if your destination URL is `https://api.example.com/v1/charges` and you define query parameters, the final URL becomes `https://api.example.com/v1/charges?merchantId=12345&version=2024-01&cardBin=411111`.

#### Request example with query parameters

{% raw %}
```json
{
  "source": {
    "type": "id",
    "id": "src_xxxxxxxxxxxxxxxxxxxxxxxxxx"
  },
  "destination_request": {
    "url": "https://api.example.com/v1/charges",
    "method": "POST",
    "headers": {
      "raw": {
        "Content-Type": "application/json"
      }
    },
    "body": "{ \"amount\": 1000, \"currency\": \"USD\" }",
    "query": [
      { "name": "merchantId", "value": "12345" },
      { "name": "version", "value": "2024-01" },
      { "name": "cardBin", "value": "{{ card_bin }}" }
    ]
  }
}
```
{% endraw %}

### JWE encryption

JWE (JSON Web Encryption) allows you to encrypt sensitive data within your request using a public or symmetric key.

The `jwe_encrypt` function is available within your templates:

{% raw %}
```
{{ jwe_encrypt(data=data_to_encrypt, key=encryption_key, alg='RSA-OAEP', enc='A256GCM', headers=custom_headers) }}
```
{% endraw %}

| Parameter | Description | Example values |
|-----------|-------------|----------------|
| `data` | The data to encrypt | `card_payload` |
| `key` | The encryption key in JWK format | `jwk_key` |
| `alg` | Key encryption algorithm | `RSA-OAEP`, `RSA-OAEP-256`, `A256GCMKW` |
| `enc` | Content encryption algorithm | `A256GCM`, `A128GCM`, `A256CBC-HS512` |
| `headers` | (Optional) Additional JWE headers | `{"kid":"key-id","iat":1234567890}` |

#### Supported algorithms

| Algorithm type | Supported values |
|----------------|------------------|
| Key encryption | `RSA-OAEP`, `RSA-OAEP-256`, `A256GCMKW` |
| Content encryption | `A128GCM`, `A256GCM`, `A128CBC-HS256`, `A256CBC-HS512` |

#### Asymmetric key encryption example

{% raw %}
```json
{
  "destination_request": {
    "body": "{ \"encryptedCard\": \"{{ jwe_encrypt(data=card_data, key=public_key, alg='RSA-OAEP', enc='A256GCM') }}\"}",
    "variables": [
      {
        "name": "card_data",
        "value": "{\"primaryAccountNumber\":\"{{ card_number }}\",\"panExpirationMonth\":\"{{ card_expiry_month }}\",\"panExpirationYear\":\"{{ card_expiry_year_yyyy }}\",\"cvv\":\"{{ card_cvv }}\"}"
      },
      {
        "name": "public_key",
        "value": "{ \"kty\": \"RSA\", \"e\": \"AQAB\", \"use\": \"enc\", \"kid\": \"key-001\", \"alg\": \"RSA-OAEP\", \"n\": \"your-public-key-modulus\" }"
      }
    ]
  }
}
```
{% endraw %}

#### Symmetric key encryption example

For destinations that require symmetric key encryption, use algorithms like `A256GCMKW`. The symmetric key must be provided as a JWK:

```json
{
  "kty": "oct",
  "k": "<base64url-encoded-256-bit-key>"
}
```

> **📝 Note:** Some APIs require the key to be derived as `base64url(sha256(<shared-secret>))`. Check your destination API documentation for the exact key derivation requirements.

---

## Secrets in Forward API

The Forward API allows you to securely store and manage sensitive data such as credentials, API keys, and encryption keys.

### Storing secrets

Store a secret by providing a unique name and the sensitive value.

| Environment | Endpoint |
|-------------|----------|
| **Production** | `POST https://forward.checkout.com/secrets` |
| **Sandbox** | `POST https://forward.sandbox.checkout.com/secrets` |

#### Request example

```json
{
  "name": "my-api-key",
  "value": "sk_live_xxxxxxxxxxxxxxxxxxxxx"
}
```

#### Response example

```json
{
  "id": "sec_xxxxxxxxxxxxxxxxxxxxxxxxxx",
  "name": "my-api-key",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Using secrets in requests

Once a secret is stored, reference it using the {% raw %}`{{ secret_<secret_name> }}`{% endraw %} syntax:

{% raw %}
```json
{
  "destination_request": {
    "headers": {
      "raw": {
        "Authorization": "{{ secret_destination-api-key }}"
      }
    }
  }
}
```
{% endraw %}

---

## Forwarding logic

The fields forwarded to the third-party endpoint depend on the type of request.

### CIT using a network token and cryptogram

If you set `network_token.request_cryptogram` to `true` and the network token and cryptogram are available:

- `network_token_number`
- `network_token_expiry_month`
- `network_token_expiry_year_yyyy` or `network_token_expiry_year_yy`
- `network_token_type`
- `network_token_cryptogram`
- `network_token_eci`

### MIT using a network token

If you set `network_token.request_cryptogram` to `false`:

- `network_token_number`
- `network_token_expiry_month`
- `network_token_expiry_year_yyyy` or `network_token_expiry_year_yy`
- `network_token_type`

### Network token fallback

If a network token or cryptogram is unavailable, the following card detail values are used:

- `card_number`
- `card_expiry_month`
- `card_expiry_year_yyyy` or `card_expiry_year_yy`

---

## Stripe forwarding example

To forward a payment request to Stripe, follow these steps:

### 1. Create a payment method

{% raw %}
```bash
curl --location 'https://forward.sandbox.checkout.com/forward' \
--header 'Content-Type: application/json' \
--header 'Authorization: YOUR_OAUTH_TOKEN' \
--data '{
  "source": {
    "type": "id",
    "id": "src_u422hics5oouvix25ous63grcy"
  },
  "reference": "string",
  "processing_channel_id": "pc_f2vtqcmhgykurkorrnnpz3kneq",
  "destination_request": {
    "url": "https://api.stripe.com/v1/payment_methods",
    "method": "POST",
    "headers": {
      "raw": {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic YOUR_STRIPE_KEY_BASE64",
        "Host": "api.stripe.com"
      }
    },
    "body": "type=card&card[number]={{card_number}}&card[exp_month]={{card_expiry_month}}&card[exp_year]={{card_expiry_year_yyyy}}&card[cvc]=314"
  }
}'
```
{% endraw %}

### 2. Create a payment intent

```bash
curl --location 'https://forward.sandbox.checkout.com/forward' \
--header 'Content-Type: application/json' \
--header 'Authorization: YOUR_OAUTH_TOKEN' \
--data '{
  "destination_request": {
    "url": "https://api.stripe.com/v1/payment_intents",
    "method": "POST",
    "headers": {
      "raw": {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic YOUR_STRIPE_KEY_BASE64"
      }
    },
    "body": "amount=1000&currency=usd&payment_method_types[]=card"
  }
}'
```

### 3. Confirm the payment intent

```bash
curl --location 'https://forward.sandbox.checkout.com/forward' \
--header 'Content-Type: application/json' \
--header 'Authorization: YOUR_OAUTH_TOKEN' \
--data '{
  "destination_request": {
    "url": "https://api.stripe.com/v1/payment_intents/<PAYMENT_INTENT_ID>/confirm",
    "method": "POST",
    "body": "payment_method=<PAYMENT_METHOD_ID>"
  }
}'
```

---

## Adyen forwarding example

To forward a payment request to Adyen:

{% raw %}
```json
{
  "source": {
    "type": "token",
    "token": "tok_zjri4ogrqjuudnhsr7ooq5z6pq"
  },
  "reference": "string",
  "processing_channel_id": "pc_f2vtqcmhgykurkorrnnpz3kneq",
  "destination_request": {
    "url": "https://checkout-test.adyen.com/v71/payments",
    "method": "POST",
    "headers": {
      "raw": {
        "Content-Type": "application/json",
        "X-API-KEY": "<ADYEN API KEY>"
      }
    },
    "body": "{\"amount\":{\"currency\":\"EUR\",\"value\":10},\"paymentMethod\":{\"type\":\"scheme\",\"encryptedCardNumber\":\"test_{{card_number}}\",\"encryptedExpiryMonth\":\"test_{{card_expiry_month}}\",\"encryptedExpiryYear\":\"test_{{card_expiry_year_yyyy}}\",\"encryptedSecurityCode\":\"test_737\"},\"reference\":\"my_reference\",\"merchantAccount\":\"YourMerchantAccount\",\"returnUrl\":\"https://httpstat.us/\"}"
  }
}
```
{% endraw %}

---

## Visa integration example

This example demonstrates how to forward card credentials to Visa's Token Service API for cloud-based provisioning.

### Complete Python implementation

The following Python script shows a complete integration with Visa's API using the Forward API. It demonstrates:

- Building the payment instrument payload with all required card and billing placeholders
- Setting up JWE encryption headers with Visa's requirements
- Using secrets for secure API key and encryption key storage
- Constructing the full Forward API request with query parameters and signature

{% raw %}
```python
import requests
import json
import time

# Define the variables for card data and encryption
forward_api_variables = [
    {
        "name": "payment_instrument",
        "value": json.dumps(
            {
                "accountNumber": "{{card_number}}",
                "cvv2": "{{card_cvv}}",
                "name": "{{cardholder_name}}",
                "expirationDate": {
                    "month": "{{card_expiry_month}}",
                    "year": "{{card_expiry_year_yyyy}}",
                },
                "billingAddress": {
                    "line1": "{{billing_address_line1}}",
                    "line2": "{{billing_address_line2}}",
                    "city": "{{billing_address_city}}",
                    "state": "{{billing_address_state}}",
                    "country": "{{billing_address_country}}",
                    "postalCode": "{{billing_address_zip}}",
                },
            }
        ),
    },
    {
        "name": "jwe_headers",
        "value": json.dumps(
            {
                "kid": "{{ secret.visa_encryption_api_key }}",
                "channelSecurityContext": "SHARED_SECRET",
                "iat": str(int(time.time())),
            }
        ),
    },
    {
        "name": "encryption_key",
        "value": json.dumps(
            {
                "kty": "oct",
                # NOTE: this must be base64(sha256(<encryption-shared-key>))
                # Example: base64.urlsafe_b64encode(hashlib.sha256(b'<key>').digest())
                "k": "{{ secret.visa_encryption_shared_key }}",
            }
        ),
    },
]

# The encrypted payment instrument using JWE
encrypted_payment_instrument = "{{ jwe_encrypt(payment_instrument, key=encryption_key, alg='A256GCMKW', enc='A256GCM', headers=jwe_headers) }}"

# Build the Visa API request body
visa_api_request = {
    "accountType": "CREDIT",
    "panSource": "ON_FILE",
    "locale": "en_US",
    "presentationType": ["CLOUD_HCE"],
    "clientWalletAccountID": "...",
    "encPaymentInstrument": encrypted_payment_instrument,
    "clientAppID": "...",
    "consumerEntryMode": "MANUAL",
    "clientWalletAccountEmailAddress": "user@example.com",
    "clientWalletAccountEmailAddressHash": "...",
    "protectionType": "SOFTWARE",
}

# Build the complete Forward API request
forward_api_request = {
    "source": {"type": "id", "id": "src_snxdnj5ijfmupnuygwz744sbxu"},
    "processing_channel_id": "pc_cvbbk7dyapdeho2qmuzozupapi",
    "destination_request": {
        "url": "https://api.visa.com/vts/provisionedTokens",
        "method": "POST",
        "headers": {
            "raw": {
                "x-request-id": "fa628a57-82ce-4d54-bc2d-1ce93d589519",
            },
        },
        "body": json.dumps(visa_api_request),
        "query": [
            {"name": "relationshipID", "value": "..."},
            {"name": "async", "value": "false"},
            {"name": "apikey", "value": "{{ secret.visa_api_key }}"},
        ],
        "variables": forward_api_variables,
        "signature": {
            "type": "visa",
            "visa_parameters": {"shared_secret": "{{ secret.visa_shared_key }}"},
        },
    },
}

# Send the request to Forward API
response = requests.request(
    method="POST",
    url="https://forward.checkout.com/forward",
    headers={
        "Authorization": "YOUR_CHECKOUT_API_KEY",
        "Content-Type": "application/json",
    },
    json=forward_api_request,
)

# Process the response
forwarded_request = json.loads(response.json()["destination_response"]["body"])["data"]
print(json.dumps(json.loads(forwarded_request), indent=2))
```
{% endraw %}

### Key concepts in this example

| Component | Purpose |
|-----------|---------|
| `payment_instrument` variable | Contains all card and billing placeholders that get replaced with actual values |
| `jwe_headers` variable | Sets up Visa-specific JWE headers including the key ID and timestamp |
| `encryption_key` variable | The symmetric encryption key in JWK format (must be SHA-256 hashed) |
| `jwe_encrypt()` function | Encrypts the payment instrument for secure transmission to Visa |
| `signature.type: "visa"` | Enables Visa-specific request signing |
| {% raw %}`{{ secret.* }}`{% endraw %} placeholders | References securely stored API keys and shared secrets |

### Required secrets

Before running this integration, store these secrets using the Secrets API:

| Secret name | Description |
|-------------|-------------|
| `visa_api_key` | Your Visa API key for authentication |
| `visa_shared_key` | Shared secret for request signing |
| `visa_encryption_api_key` | Key ID for JWE encryption |
| `visa_encryption_shared_key` | Base64-encoded SHA-256 hash of your encryption shared secret |

---

## View forward request outcomes

You can view the outcome of your forward requests in the Dashboard.

1. Sign in to the [Dashboard](https://dashboard.checkout.com).
2. Go to **Vault** > **Credential forwarding**.

On this page you can view:
- The total number of forward requests
- The response rate for your forward requests
- A breakdown of the responses received from the destinations
- A history of all forward requests you've sent

Select a specific forward request to open its details page.

