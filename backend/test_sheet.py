import asyncio
from app.services.sheets import _get_worksheet

def test():
    ws = _get_worksheet()
    all_values = ws.get_all_values()
    print("Total rows returned by get_all_values:", len(all_values))
    if len(all_values) > 1:
        print("Row 2:", all_values[1])
        print("Row 97:", all_values[96] if len(all_values) >= 97 else "N/A")
        print("Row 98:", all_values[97] if len(all_values) >= 98 else "N/A")
        
test()
