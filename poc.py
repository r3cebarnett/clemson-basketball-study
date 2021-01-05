import requests
from bs4 import BeautifulSoup
import json
import pprint

BASE_URL    = "https://www.espn.com/mens-college-basketball/team/{schedule,roster}/_/id/{team_id}/season/{year}"
GAME_URL    = "https://www.espn.com/mens-college-basketball/game?gameId=401258866"
PBP_URL     = "https://www.espn.com/mens-college-basketball/playbyplay?gameId=401265031"
SCH_URL     = "https://www.espn.com/mens-college-basketball/team/schedule/_/id/228/season/2021"
RST_URL     = "https://www.espn.com/mens-college-basketball/team/roster/_/id/228/season/2021"
TEAMS_URL   = "https://www.espn.com/mens-college-basketball/teams"

VERBOSE = True

def get_teams():
    r = requests.get(TEAMS_URL)
    soup = BeautifulSoup(r.content, 'html5lib')
    table = soup.findAll('div', attrs={'class': 'mt7'})
    all_teams_by_conference = {}
    
    for conference in table:
        name = conference.find('div', attrs={'class': 'headline headline pb4 n8 fw-heavy clr-gray-01'})
        name = name.get_text()
        all_teams_by_conference[name] = []

        teams = conference.findAll('div', attrs={'class': 'pl3'})
        for team in teams:
            team_a = team.find('a')
            team_url_split = team_a['href'].split('/')
            team_dict = {
                'name': team_a.get_text(),
                'id': team_url_split[team_url_split.index('id') + 1]
            }

            all_teams_by_conference[name].append(team_dict)

    if VERBOSE:
        pprint.pprint(all_teams_by_conference)
    
    return all_teams_by_conference

def get_schedule():
    r = requests.get(SCH_URL)
    soup = BeautifulSoup(r.content, 'html5lib')
    print('To be determined')

###         ###
# Main Runner #
###         ###
if __name__ == '__main__':
    #get_teams()