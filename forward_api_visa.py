import requests
import json
import time

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
                # Example in python: base64.urlsafe_b64encode(hashlib.sha256(b'<encryption-shared-key>').digest())
                "k": "{{ secret.visa_encryption_shared_key }}",
            }
        ),
    },
]

encrypted_payment_instrument = "{{ jwe_encrypt(payment_instrument, key=encryption_key, alg='A256GCMKW', enc='A256GCM', headers=jwe_headers) }}"

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


forward_api_request = {
    "source": {"type": "id", "id": "src_snxdnj5ijfmupnuygwz744sbxu"},
    "processing_channel_id": "pc_cvbbk7dyapdeho2qmuzozupapi",
    "destination_request": {
        "url": "https://httpbun.com/anything",  # should be "https://api.visa.com/vts/provisionedTokens",
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

response = requests.request(
    method="POST",
    url="https://forward-api-qa.ckotech.co/forward",
    headers={
        "Authorization": "sk_qa_h7b7hthffmnj2tg7fkvaoksyzi6",
        "Content-Type": "application/json",
    },
    json=forward_api_request,
)

forwarded_request = json.loads(response.json()["destination_response"]["body"])["data"]

print(json.dumps(json.loads(forwarded_request), indent=2))
