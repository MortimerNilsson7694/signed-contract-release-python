import json

from src.sign_service import ContractRequest, InfraiPdfClient, release_contract


request = ContractRequest(
    contract_id="demo-contract",
    parties=("Acme Tools", "Example Developer"),
    body_markdown="Access is granted for the listed developer tools.",
)
result = release_contract(request, InfraiPdfClient())
print(json.dumps({"contract_id": result.contract_id, "event": result.event, "pdf": result.pdf}, indent=2))
