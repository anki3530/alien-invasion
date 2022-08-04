import json

filename = 'highscore.json'
try:
    with open(filename) as f:
        highscore = json.load(f)

except FileNotFoundError:
    highscore = 0
    with open(filename, 'w') as f:
        json.dump(highscore, f)


