from datetime import time

HOUR_OF_DAY_24 = [((time(h ,m).strftime('%I:%M %p')),(time(h ,m).strftime('%I:%M %p'))) for h in range(0,24) for m in(0,30)]
print(HOUR_OF_DAY_24)