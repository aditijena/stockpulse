from db import fetch_inventory

# Test the improved fetch_inventory
inventory_df = fetch_inventory()

print("=" * 100)
print("INVENTORY WITH CALCULATED RISK")
print("=" * 100)
print("\nColumns:", inventory_df.columns.tolist())
print(f"\nTotal Products: {len(inventory_df)}\n")

for _, row in inventory_df.iterrows():
    print(f"Product: {row['Product Name']}")
    print(f"  Category: {row['Category']}")
    print(f"  Stock: {row['Stock Quantity']}")
    print(f"  Days Unsold: {row['Days Unsold']}")
    print(f"  Risk Level: {row['Risk Level']}")
    print(f"  Risk Score: {row['Risk Score (%)']}")
    print()
