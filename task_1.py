import random
import time
from collections import deque
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)


class SlidingWindowRateLimiter:
    """
    A rate limiter that uses the Sliding Window algorithm to control the
    rate of messages sent by users.

    Attributes:
        window_size (int): The size of the time window in seconds.
        max_requests (int): The maximum number of requests allowed
        within the window.
        user_windows (Dict[str, deque]): A dictionary to store the
        message timestamps for each user.
    """

    def __init__(self, window_size: int = 10, max_requests: int = 1):
        """
        Initialize the rate limiter with the given window size and
        maximum requests.

        Args:
            window_size (int): The size of the time window in seconds.
            max_requests (int): The maximum number of requests allowed
            within the window.
        """
        self.window_size = window_size
        self.max_requests = max_requests
        self.user_windows = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        """
        Clean up the window by removing outdated timestamps for the
        given user.

        Args:
            user_id (str): The ID of the user.
            current_time (float): The current time in seconds.
        """
        if user_id in self.user_windows:
            while (
                self.user_windows[user_id]
                and current_time - self.user_windows[user_id][0]
                > self.window_size
            ):
                self.user_windows[user_id].popleft()
            if not self.user_windows[user_id]:
                del self.user_windows[user_id]

    def can_send_message(self, user_id: str) -> bool:
        """
        Check if the user can send a message within the current window.

        Args:
            user_id (str): The ID of the user.

        Returns:
            bool: True if the user can send a message, False otherwise.
        """
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        return len(self.user_windows.get(user_id, [])) < self.max_requests

    def record_message(self, user_id: str) -> bool:
        """
        Record a new message sent by the user.

        Args:
            user_id (str): The ID of the user.

        Returns:
            bool: True if the message was recorded, False if the user is
             rate-limited.
        """
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        if self.can_send_message(user_id):
            if user_id not in self.user_windows:
                self.user_windows[user_id] = deque()
            self.user_windows[user_id].append(current_time)
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        """
        Calculate the time until the user can send the next message.

        Args:
            user_id (str): The ID of the user.

        Returns:
            float: The time in seconds until the next message can be
            sent.
        """
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        if user_id in self.user_windows and self.user_windows[user_id]:
            oldest_message_time = self.user_windows[user_id][0]
            return max(
                0, self.window_size - (current_time - oldest_message_time)
            )
        return 0


# Demonstration of the rate limiter
def test_rate_limiter():
    """
    Test function to demonstrate the functionality of the
    SlidingWindowRateLimiter.
    """
    # Create a rate limiter: window size of 10 seconds, 1 message allowed
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    # Simulate a stream of messages from users (sequential IDs from 1 to 20)
    print(Fore.CYAN + "\n=== Simulating Message Stream ===")
    for message_id in range(1, 11):
        # Simulate different users (IDs from 1 to 5)
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        if result:
            print(Fore.GREEN + f"Message {message_id:2d} | User {user_id} | ✓")
        else:
            print(
                Fore.RED + f"Message {message_id:2d} | "
                f"User {user_id} | × (wait {wait_time:.1f}s)"
            )

        # Small delay between messages for realism
        # Random delay between 0.1 and 1 second
        time.sleep(random.uniform(0.1, 1.0))

    # Wait for the window to clear
    print(Fore.CYAN + "\nWaiting for 4 seconds...")
    time.sleep(4)

    print(Fore.CYAN + "\n=== New Series of Messages After Waiting ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        if result:
            print(Fore.GREEN + f"Message {message_id:2d} | User {user_id} | ✓")
        else:
            print(
                Fore.RED + f"Message {message_id:2d} | "
                f"User {user_id} | × (wait {wait_time:.1f}s)"
            )
        # Random delay between 0.1 and 1 second
        time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    test_rate_limiter()
