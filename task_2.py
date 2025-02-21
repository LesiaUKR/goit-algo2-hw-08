import time
import random
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)


class ThrottlingRateLimiter:
    """
    A rate limiter that uses the Throttling algorithm to control the rate
    of messages sent by users.

    Attributes:
        min_interval (float): The minimum interval (in seconds) required
        between consecutive messages.
        last_message_times (dict[str, float]): A dictionary to store the
        last message timestamp for each user.
    """

    def __init__(self, min_interval: float = 10.0):
        """
        Initialize the rate limiter with the given minimum interval.

        Args:
            min_interval (float): The minimum interval (in seconds)
            required between consecutive messages.
        """
        self.min_interval = min_interval
        self.last_message_times = {}

    def can_send_message(self, user_id: str) -> bool:
        """
        Check if the user can send a message based on the last message
        timestamp.

        Args:
            user_id (str): The ID of the user.

        Returns:
            bool: True if the user can send a message, False otherwise.
        """
        current_time = time.time()
        last_time = self.last_message_times.get(user_id, 0)
        return current_time - last_time >= self.min_interval

    def record_message(self, user_id: str) -> bool:
        """
        Record a new message sent by the user and update the last
        message timestamp.

        Args:
            user_id (str): The ID of the user.

        Returns:
            bool: True if the message was recorded, False if the user
            is rate-limited.
        """
        if self.can_send_message(user_id):
            self.last_message_times[user_id] = time.time()
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        """
        Calculate the time until the user can send the next message.

        Args:
            user_id (str): The ID of the user.

        Returns:
            float: The time in seconds until the next message can be sent.
        """
        current_time = time.time()
        last_time = self.last_message_times.get(user_id, 0)
        return max(0, self.min_interval - (current_time - last_time))


def test_throttling_limiter():
    """
    Test function to demonstrate the functionality of the ThrottlingRateLimiter.
    """
    # Create a rate limiter with a minimum interval of 10 seconds
    limiter = ThrottlingRateLimiter(min_interval=10.0)

    # Simulate a stream of messages from users (sequential IDs from 1 to 20)
    print(Fore.CYAN + "\n=== Simulating Message Stream (Throttling) ===")
    for message_id in range(1, 11):
        # Simulate different users (IDs from 1 to 5)
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        if result:
            print(Fore.GREEN + f"Message {message_id:2d} | User {user_id} | ✓")
        else:
            print(
                Fore.RED
                + f"Message {message_id:2d} | "
                  f"User {user_id} | × (wait {wait_time:.1f}s)"
            )

        # Random delay between messages for realism
        time.sleep(random.uniform(0.1, 1.0))

    # Wait for the minimum interval to pass
    print(Fore.CYAN + "\nWaiting for 10 seconds...")
    time.sleep(10)

    # Simulate a new series of messages after waiting
    print(Fore.CYAN + "\n=== New Series of Messages After Waiting ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        if result:
            print(Fore.GREEN + f"Message {message_id:2d} |"
                               f" User {user_id} | ✓")
        else:
            print(
                Fore.RED
                + f"Message {message_id:2d} | "
                  f"User {user_id} | × (wait {wait_time:.1f}s)"
            )
        time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    test_throttling_limiter()
