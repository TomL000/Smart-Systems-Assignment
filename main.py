# importing libraries
from presentation import userMenu
import time
from processing import humidityMonitor

# main code sequence
def main():
    userMenu()
    print("Press CTRL+C to pause humidity monitoring and return to menu.")
    # loops humidity monitoring function until user hits CTRL-C to return to menu, where they may quit, adjust or continue.
    while True:
        try:
            humidityMonitor()
            time.sleep(30)
        except KeyboardInterrupt:
            print("\nINTERRUPT\n")
            userMenu()

# executes main code
main()