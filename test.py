import requests
import json
import time
url = "https://waba-v2.360dialog.io/messages"
payload = json.dumps({
"messaging_product": "whatsapp",
"recipient_type": "individual",
"to": '201002589923',
"type": "text",
"text": {
"body": "مرحبًا من 360Dialog"
}
})
headers = {
'D360-API-KEY': '54tXrXMiHj9KmLdaFElEE2fkAK',
'Content-Type': 'application/json'
}
response = requests.request("POST", url, headers=headers, data=payload)
