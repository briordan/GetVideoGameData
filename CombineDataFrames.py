import numpy as np
import pandas as pd
import requests
import json
import time

# combine the csv files for ps4, switch, and xboxone
# I ran this after running queries for each platform
def test_run():
    ps4 = pd.read_csv('ps4.csv')
    XBoxOne = pd.read_csv('xboxone.csv')
    Switch = pd.read_csv('switch.csv')

    Games = pd.concat([ps4, XBoxOne, Switch], axis=0, ignore_index=True, sort=False)
    Games.to_csv('games.csv', index=False)


if __name__ == "__main__":
    test_run()