import asyncio
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import os

async def main():
    templates = Jinja2Templates(directory="d:/TexBid_motiur/frontend/src/pages")
    
    # Mock data
    class MockRequest(dict):
        def __init__(self):
            super().__init__()
            self.scope = {"type": "http"}

    enriched_bids = [{
        "bid": {"id": "123", "bid_status": "PENDING", "bid_price": 10},
        "rfq": {"id": "rfq123", "buyer_id": "buyer123", "title": None},
        "buyer_name": "Test Buyer"
    }]
    
    try:
        from jinja2 import Template
        template_str = """<button onclick='openChatDrawer("{{ item.rfq.buyer_id }}", {{ item.buyer_name | default("Buyer", true) | tojson }}, "{{ item.rfq.id }}", {{ item.rfq.title | default("RFQ", true) | tojson }})'>Chat</button>"""
        template = Template(template_str)
        res = template.render(item=enriched_bids[0])
        print("Render successful:", res)
    except Exception as e:
        print(f"Jinja render error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
