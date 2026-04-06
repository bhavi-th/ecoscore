import json

# Load the two JSON files
with open("score.json") as f:
    main_product = json.load(f)

with open("alternatives.json") as f:
    alternatives = json.load(f)["alternatives"]

# Combine main product with alternatives
all_products = [main_product] + alternatives

# Sort by score descending, then carbon ascending
best_product = sorted(all_products, key=lambda x: (-x["score"], x["carbon"]))[0]

print("Best Product:")
print(json.dumps(best_product, indent=2))
