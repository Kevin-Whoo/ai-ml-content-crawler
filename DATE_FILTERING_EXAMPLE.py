# Example: How to add date filtering to crawlers

# In each crawler's crawl() method, after getting items:

filtered_items = []
for item in items:
    # Get the date field (might be different for each source)
    date_str = item.get('date') or item.get('published') or item.get('created_at', '')
    
    # Check if it's recent (within last 6 months)
    if self._is_recent(date_str):
        filtered_items.append(item)
    else:
        print(f"Skipping old item: {item.get('title', 'Unknown')} from {date_str}")

items = filtered_items
