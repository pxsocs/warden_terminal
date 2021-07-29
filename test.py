from time import sleep

print('Waiting... please press Ctrl-C when you wish to proceed.')
try:
    for i in range(0, 30 * 60):  # 30 minutes is 30*60 seconds
        sleep(1)
    print("Oops, sorry, no input was received today. Come back tomorrow.")
except KeyboardInterrupt:
    weight_today = input("Time to log the daily weight-in! How much today? ")
    print("Thanks for logging: " + weight_today)
