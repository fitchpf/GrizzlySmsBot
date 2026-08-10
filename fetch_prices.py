import os
import requests

def main():
    api_key = os.environ.get("GRIZZLY_API_KEY")
    if not api_key:
        print("ERROR: GRIZZLY_API_KEY not set")
        return

    url = "https://api.grizzlysms.com/stubs/handler_api.php"
    params = {
        "api_key": api_key,
        "action": "getNumbersStatus"
    }
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        data = response.text.strip()
    except Exception as e:
        print(f"ERROR: Failed to fetch data: {e}")
        return

    if not data.startswith("STATUS_OK:"):
        print(f"ERROR: Unexpected response: {data[:200]}")
        return

    # Remove "STATUS_OK:" prefix
    data = data[10:]

    # Parse activations
    activations = data.split(";") if ";" in data else [data]
    
    provider_prices = {}
    
    for activation in activations:
        if not activation:
            continue
        parts = activation.split(":")
        if len(parts) >= 5:
            # Fields: activation_id, phone, status, providerId, price
            provider_id = parts[3]
            try:
                price = float(parts[4])
            except ValueError:
                continue
            
            if provider_id not in provider_prices:
                provider_prices[provider_id] = []
            provider_prices[provider_id].append(price)

    if not provider_prices:
        print("No data found.")
        return

    print("\n" + "=" * 60)
    print("PROVIDER PRICE SUMMARY")
    print("=" * 60)
    print(f"{'Provider ID':<15} {'Count':<8} {'Avg Price':<12} {'Min':<10} {'Max':<10}")
    print("-" * 60)

    # Calculate and print stats
    for provider_id, prices in sorted(provider_prices.items()):
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
        print(f"{provider_id:<15} {len(prices):<8} ${avg_price:<11.2f} ${min_price:<9.2f} ${max_price:<9.2f}")

    print("=" * 60)
    print(f"Total providers: {len(provider_prices)}")
    print(f"Total activations: {sum(len(p) for p in provider_prices.values())}")
    print("=" * 60)

if __name__ == "__main__":
    main()
