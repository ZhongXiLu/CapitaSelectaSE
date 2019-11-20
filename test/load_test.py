import aiohttp
import asyncio
import requests
import sys
import time

PROXY_URL = None
ORDERED_TICKETS = 0
TICKETS_TO_ORDER = 0


async def order_ticket(session, user_id, token):
    """Order a ticket and return the total response time"""
    start = time.time()
    async with session.post(f'{PROXY_URL}:30003/orders', json={'user_id': user_id, 'token': token}) as response:
        data = await response.text()
        end = time.time()

        global ORDERED_TICKETS, TICKETS_TO_ORDER, RESPONSE_TIMES
        ORDERED_TICKETS += 1
        print(f"Ordered Tickets: {ORDERED_TICKETS}/{TICKETS_TO_ORDER}", end="\r", flush=True)

        return end - start


async def main():
    # Retrieve all users
    users = []
    response = requests.get(f'{PROXY_URL}:30007/users')
    if response.status_code == 200:
        users = response.json()['data']['users']
    global TICKETS_TO_ORDER
    TICKETS_TO_ORDER = len(users)

    # Order a ticket for each user
    async with aiohttp.ClientSession() as session:
        response_times = await asyncio.gather(*[order_ticket(session, user['id'], user['token']) for user in users])

        print()
        print(f'Average response time:\t{sum(response_times) / float(len(response_times))} sec')
        print(f'Shortest response time:\t{min(response_times)} sec')
        print(f'Longest response time:\t{max(response_times)} sec')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        PROXY_URL = sys.argv[1]
        print(f'PROXY_URL: {PROXY_URL}')
