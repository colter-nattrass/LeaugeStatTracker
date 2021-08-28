from riotwatcher import LolWatcher, ApiError
import pandas as pd
import pprint
import json
import time

# API Documentation
# RiotWatcher > LoLWatcher: https://riot-watcher.readthedocs.io/en/latest/riotwatcher/LeagueOfLegends/index.html
# Summoner API V4         : https://riot-watcher.readthedocs.io/en/latest/riotwatcher/LeagueOfLegends/SummonerApiV4.html#riotwatcher._apis.league_of_legends.SummonerApiV4
# DataDragon Version      : https://riot-watcher.readthedocs.io/en/latest/riotwatcher/LeagueOfLegends/DataDragonApi.html
# DataDragon Champions    : https://riot-watcher.readthedocs.io/en/latest/riotwatcher/LeagueOfLegends/DataDragonApi.html


# Dependencies to identify me/API key
playerName = 'LuckyFin'
lol_watcher = LolWatcher('RGAPI-f98f6978-3f04-4c42-bb41-8803560f8bae')
my_region = 'na1'  # Define Region
me = lol_watcher.summoner.by_name(my_region, playerName)  # RiotWatcher
my_matches = lol_watcher.match.matchlist_by_account(my_region, me['accountId'])  # Summoner API
latest_version = lol_watcher.data_dragon.versions_for_region(my_region)['n']['champion']  # DataDragon Version
static_champ_list = lol_watcher.data_dragon.champions(latest_version, False, 'en_US')  # DataDragon Champion

# This will make a dictionary of the champions and their number
champ_dict = {}
for key in static_champ_list['data']:
    row = static_champ_list['data'][key]  # store these dictionaries into a variable /  row is a dictionary
    champ_dict[row['key']] = row[
        'id']  # store the dictionary value of 'id', which in this case is each champions name, and store it into the dictionary champ_dict as a string

# Throw Errors
try:
    me = lol_watcher.summoner.by_name(my_region, playerName)
except ApiError as err:
    if err.me.status_code == 429:  # Throw for rate limiting error
        print('We should retry in {} seconds.'.format(err.headers['Retry-After']))
        print('this retry-after is handled by default by the RiotWatcher library')
        print('future requests wait until the retry-after time passes')
    elif err.me.status_code == 404:  # Throw for not finding summoner error
        print('Summoner with that ridiculous name not found.')
    else:
        raise

# Initiate empty series
tableList = []  # Declare a list of dictionaries


# Function to find particpantId and player_index within a match which is typcally participantId -1
# This finds Player in the matches and saves those Id's into a list

def getParticipantId(gameId, match_data):
    for participantId in match['participantIdentities']:
        if playerName in participantId['player']['summonerName']:
            playerId = participantId['participantId']
        else:
            pass
    player_index = playerId - 1
    return player_index


def getChampionName(championId):
    championName = champ_dict[championId]
    return championName


def matchResults(win_bool):
    if win_bool:
        win_loss = 'Win'
    else:
        win_loss = 'Lost'
    return win_loss


def kdaCalc(kills, deaths, assists):
    if deaths == 0:
        kda = (kills + assists) / 1
    else:
        kda = (kills + assists) / deaths
    return round(kda, 1)


# Iterate over my matches and place the gameId's into a list
gameId_list = []
for matches in my_matches['matches']:
    gameId_list.append(matches['gameId'])
gameId_list = gameId_list[:5]

# Iterate through my gameId list and find my match information for each game
for gameId in gameId_list:
    statDict = {}
    # time.sleep(10)
    match = lol_watcher.match.by_id(my_region, gameId)
    player_index = getParticipantId(gameId, match)
    player_stats = match['participants'][player_index]['stats']
    gameDuration = match['gameDuration']
    statDict['Player'] = playerName
    statDict['Champion'] = getChampionName(str(match['participants'][player_index]['championId']))
    statDict['Game Mode'] = match['gameMode']
    statDict['Win/Lost'] = matchResults(player_stats['win'])
    statDict['KDA'] = kdaCalc(player_stats['kills'], player_stats['deaths'], player_stats['assists'])
    statDict['Avg CS/Min'] = round(player_stats['totalMinionsKilled'] / (gameDuration / 60), 1)
    statDict['Vision Score'] = player_stats['visionScore']
    statDict['Wards Placed'] = player_stats['visionWardsBoughtInGame'] + player_stats['sightWardsBoughtInGame']
    statDict['Queue Type'] = match['queueId']
    tableList.append(statDict)

df = pd.DataFrame(tableList)

# df = pd.DataFrame(tableList)

# UP TO HERE WORKS

#
# # Lets try this::
# for gameId in gameId_list:
#     match = lol_watcher.match.by_id(my_region, gameId)
#     # pprint.pp(match['gameId'])
#     for player in match['participantIdentities']:
#         if "LuckyFin" in player['player']['summonerName']:
#             gameDuration = match['gameDuration']
#             gameMode = match['gameMode']
#             queueId = match['queueId']
#
#             # UP TO HERE WORKS
#
#             championId = player['championId']
#
#             statDict['Player'] = 'LuckyFin'
#             statDict['Champion'] = championId
#             statDict['Queue Type'] = queueId
#             statDict['Game Mode'] = gameMode
#             statDict['Win/Lost'] = player['stats']['win']
#             if statDict['Win/Lost'] == True:
#                 statDict['Win/Lost'] = 'Win'
#             else:
#                 statDict['Win/Lost'] = 'Lost'
#             if player['stats']['deaths'] == 0:
#                 statDict['KDA'] = (player['stats']['kills'] + player['stats']['assists']) / 1
#             else:
#                 statDict['KDA'] = (player['stats']['kills'] + player['stats']['assists']) / player['stats']['deaths']
#             statDict['Avg CS/Min'] = (player['stats']['totalMinionsKilled'] / (gameDuration / 60))
#             statDict['Vision Score'] = player['stats']['visionScore']
#             statDict['Wards Placed'] = (
#                     (player['stats']['visionWardsBoughtInGame']) + (player['stats']['sightWardsBoughtInGame']))
#             grid.append(statDict)
#         else:
#             pass
#
# df = pd.DataFrame(grid)
# pprint.pp(df)
#
# # This will make a dictionary of the champions and their number
# champ_dict = {}
# for key in static_champ_list['data']:
#     row = static_champ_list['data'][key]  # store these dictionaries into a variable /  row is a dictionary
#     champ_dict[row['key']] = row[
#         'id']  # store the dictionary value of 'id', which in this case is each champions name, and store it into the dictionary champ_dict as a string
#
# # This will change the champion numbers to actual names in the Dataframe.
# for row in grid:
#     row['Champion'] = champ_dict[str(row['Champion'])]
# df = pd.DataFrame(grid)
#
# # Get the json file from:   https://static.developer.riotgames.com/docs/lol/queues.json
# f = open('/Users/luckyfin/Desktop/queues.json')  # Open on skyes mac
# # f = open('C:/Users/Peterson/Desktop/queues.json')                           # Open on skyes PC
# queueId_dict = {}
# data = json.load(f)
#
# # This converts the queueId to the Queue Description in the json file
# for key in data:
#     for row in grid:
#         if row['Queue Type'] == key['queueId']:
#             row['Queue Type'] = key['description']
#         else:
#             pass
# df = pd.DataFrame(grid)
#
# # Print what we have in our dataframe to see the outcome!
# pprint.pp(df)
#
# # Lastly, pretty print the files and write to an EXCEL sheet
# df.to_csv('/Users/luckyfin/PycharmProjects/LeagueStatTracker.csv')  # FOR MAC
# # df.to_csv('C:/Users/Peterson/Desktop/LeagueStatTracker.csv')                # FOR PC
# f.close()
#
# # OTHER STUFF
#
#
# # We will need this to determine rank and post this in a separate dataframe above my game information
# # This call will return my ranked stats in Flex and Solo queue, total overall games played, and some special ID's
# # my_ranked_stats = lol_watcher.league.by_summoner(my_region, me['id'])
# # print(my_ranked_stats)
#
#
# # seasonId = match_detail0['seasonId']
# # gameType = match_detail0['gameType']
# # I ALSO WANT SEASON NUMBER
# # I ALSO WANT TO CENTER EVERYTHING IN THE DATAFRAME AND IF POSSIBLE ADJUST FONT ON TITLES
# # not a huge deal though because we can create a tool that queries that data and then does these changes within excel sheets
# # We need to round the avg/cs/min to 2 decimal places in the dataframe (or we can do this when we query data in excel sheets
# # find where LP gains are stored
