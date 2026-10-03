import httpx

try:
    r = httpx.get("https://wyiknkmoskkpbwjvtiyp.supabase.co", timeout=10)
    print("Success:", r.status_code)
except Exception as e:
    print(type(e).__name__)
    print(e)