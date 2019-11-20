import asyncio
import requests
import sys
import time

USER_SERVICE_URL = None
ORDER_SERVICE_URL = None


async def order_ticket(user_id, token):
    """Order a ticket and return the total response time"""
    start = time.time()
    response = requests.post(f'{ORDER_SERVICE_URL}/orders', json={'user_id': user_id, 'token': token})
    end = time.time()
    # print("|", end="")
    return end - start


async def main():
    # Retrieve all users
    users = []
    response = requests.get(f'{USER_SERVICE_URL}/users')
    if response.status_code == 200:
        users = response.json()['data']['users']

    # Order a ticket for each user
    response_times = []
    for user in users:
        response_time = await order_ticket(user['id'], user['token'])
        response_times.append(response_time)

    print()
    print(f'Average response time:\t{sum(response_times) / float(len(response_times))} sec')
    print(f'Shortest response time:\t{min(response_times)} sec')
    print(f'Longest response time:\t{max(response_times)} sec')


if __name__ == '__main__':
    if len(sys.argv) > 2:
        USER_SERVICE_URL = sys.argv[1]
        ORDER_SERVICE_URL = sys.argv[2]
        print(f'USER_SERVICE_URL: {USER_SERVICE_URL}')
        print(f'ORDER_SERVICE_URL: {ORDER_SERVICE_URL}')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(main())
