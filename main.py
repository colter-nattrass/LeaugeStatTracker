from riotwatcher import LolWatcher, ApiError
import pandas as pd
import pprint
import json


# Dependencies to identify me/API key
lol_watcher = LolWatcher('RGAPI-93ca0d74-5987-4168-a9db-96bf1bd922e8')                      # RIOT API KEY
my_region = 'na1'                                                                           # Define Region
me = lol_watcher.summoner.by_name(my_region, 'LuckyFin')                                    # Throw error if name is wrong
my_matches = lol_watcher.match.matchlist_by_account(my_region, me['accountId'])             # Limit is 100, can index more
static_champ_list = lol_watcher.data_dragon.champions(game_version, False, 'en_US')         # Latest game version


# Throw Errors
try:
    response = lol_watcher.summoner.by_name(my_region, 'LuckyFin')
except ApiError as err:
    if err.response.status_code == 429:                                                 # Throw for rate limiting error
        print('We should retry in {} seconds.'.format(err.headers['Retry-After']))
        print('this retry-after is handled by default by the RiotWatcher library')
        print('future requests wait until the retry-after time passes')
    elif err.response.status_code == 404:                                               # Throw for not finding summoner error
        print('Summoner with that ridiculous name not found.')
    else:
        raise


# Get match info API's
match0 = my_matches['matches'][0]                                       # Most recent match
match_detail0 = lol_watcher.match.by_id(my_region, match0['gameId'])    # Details of the match
gameDuration = match_detail0['gameDuration']                            # Declare and define the game duration (seconds)
gameMode = match_detail0['gameMode']
queueId = match_detail0['queueId']


# Variables
grid = []                                                               # Declare a list for our dataframe
statDict = {}                                                           # Declare a dictionary of statistics
participantId = ""
summonerName = ""







# CURRENTLY IN PROGRESS
# Find the queue ID and its relevant json code

# Python program to read
# json file
# Opening JSON file
f = open('/Users/luckyfin/Desktop/queues.json')

# returns JSON object as
# a dictionary
data = json.load(f)

# Iterating through the json
# list
for key in data['queueId']:
    print(key)

# Closing file
f.close()










# Find the Summoner name
for identity in match_detail0['participantIdentities']:
    if "LuckyFin" in identity['player']['summonerName']:
        participantId = identity['participantId']
        summonerName = identity['player']['summonerName']
    else:
        pass


# Add the stats of the player to the dataframe
for player in match_detail0['participants']:
    if player['participantId'] == participantId:
        statDict['Player'] = summonerName
        championId = player['championId']
        statDict['Champion'] = championId

        statDict['Game Mode'] = gameMode
        statDict['Win/Lost'] = player['stats']['win']
        if statDict['Win/Lost'] == True:
            statDict['Win/Lost'] = 'Win'
        else:
            statDict['Win/Lost'] = 'Lost'
        statDict['Kills'] = player['stats']['kills']
        statDict['Deaths'] = player['stats']['deaths']
        statDict['Assists'] = player['stats']['assists']
        if statDict['Deaths'] == 0:
            statDict['KDA'] = (player['stats']['kills'] + player['stats']['assists']) / 1
        else:
            statDict['KDA'] = (player['stats']['kills'] + player['stats']['assists']) / player['stats']['deaths']
        statDict['Vision Score'] = player['stats']['visionScore']
        statDict['Total Minions Killed'] = player['stats']['totalMinionsKilled']
        statDict['Avg CS/Min'] = (player['stats']['totalMinionsKilled'] / (gameDuration / 60))
        statDict['Wards Placed'] = player['stats']['wardsPlaced']
        grid.append(statDict)
    else:
        pass
df = pd.DataFrame(grid)


# This will make a dictionary of the champions and their number
champ_dict = {}
for key in static_champ_list['data']:
    row = (static_champ_list['data'][key])
    champ_dict[row['key']] = row['id']
    #print(dict_of_values['id'])                                 # This will print out the Champion names
    #print(dict_of_values['key'])                                # This will print out the champion ID number
    #print(champ_dict[row['key']])                               # This will display the names of the champions
#print(champ_dict)                                               # This will print the dictionary


# This will change the champion numbers to actual names in the Dataframe.
for row in grid:
    row['Champion'] = champ_dict[str(row['Champion'])]


df = pd.DataFrame(grid)
pprint.pp(df)


# Lastly, pretty print the files and write to an EXCEL sheet
df.to_csv('/Users/luckyfin/PycharmProjects/LeagueStatTracker.csv')
#df.to_csv('C:/Users/Desktop/LeagueStatTracker.csv')











            













            # OTHER STUFF




# We will need this to determine rank
# This call will return my ranked stats in Flex and Solo queue, total overall games played, and some special ID's
my_ranked_stats = lol_watcher.league.by_summoner(my_region, me['id'])
# print(my_ranked_stats)





# seasonId = match_detail0['seasonId']

# gameType = match_detail0['gameType']


# I ALSO WANT GAME DURATION, SEASON NUMBER, PLATFORM (NA/EU), GAMEMODE (URF/RANKED SOLO), QUEUEID?

