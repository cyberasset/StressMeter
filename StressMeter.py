import aiohttp
import asyncio
import time
import nest_asyncio

# Allow nested event loops
nest_asyncio.apply()

async def check_website(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return response.status == 200
    except Exception:
        return False

async def send_request(session, url):
    async with session.get(url) as response:
        return await response.text()

async def run_stress_test(url, requests_per_second):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(requests_per_second):
            tasks.append(send_request(session, url))
        await asyncio.gather(*tasks)

async def main(url):
    # Check if the website is up initially
    if not await check_website(url):
        print(f"The website {url} is down or unreachable. Aborting stress test.")
        return

    print(f"The website {url} is up. Starting stress test...")
    try:
        while True:
            # Check if the website is still up before sending requests
            if not await check_website(url):
                print(f"The website {url} has gone down during the stress test.")
                break
            
            start_time = time.time()
            await run_stress_test(url, 1000)
            elapsed_time = time.time() - start_time
            print(f'Sent 1000 requests in {elapsed_time:.2f} seconds')

            # To ensure we send 1000 requests per second
            await asyncio.sleep(max(0, 1 - elapsed_time))
    except KeyboardInterrupt:
        print("\nStress test stopped by user.")

# Run the main coroutine
if __name__ == "__main__":
    TARGET_URL = input("Enter the website URL to stress test (e.g., http://example.com): ")
    try:
        asyncio.run(main(TARGET_URL))
    except Exception as e:
        print(f"An error occurred: {e}")
