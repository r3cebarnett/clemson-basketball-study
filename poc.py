import requests
from bs4 import BeautifulSoup
import json
import pprint

BASE_URL    = "https://www.espn.com/mens-college-basketball/team/{schedule,roster}/_/id/{team_id}/season/{year}"
GAME_URL    = "https://www.espn.com/mens-college-basketball/game?gameId=401258866"
PBP_URL     = "https://www.espn.com/mens-college-basketball/playbyplay?gameId=401265031"
SCH_URL     = "https://www.espn.com/mens-college-basketball/team/schedule/_/id/228/season/2020"
RST_URL     = "https://www.espn.com/mens-college-basketball/team/roster/_/id/228/season/2020"
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
    raw_games = soup.find_all('div', attrs={'class': 'flex items-center opponent-logo'})
    schedule = []

    for raw_game in raw_games:
        sections = raw_game.parent.parent.find_all('td', attrs={'class': 'Table__TD'})
        raw_game_span = raw_game.find_all('span')
        opp_team_url = raw_game_span[-1].find('a')['href'].split('/')
        game_a = sections[2].find('a')
        schedule.append({
            'location': 'Home' if raw_game_span[0].get_text() == 'vs' else 'Away',
            'opponent': {
                'name': raw_game_span[-1].get_text().strip(),
                'id': opp_team_url[opp_team_url.index('id') + 1]
            },
            'date': sections[0].get_text(),
            'id': game_a['href'].split('=')[1] if game_a else -1
        })
    
    if VERBOSE:
        pprint.pprint(schedule)

    return schedule

def get_action_from_play(action_text):
    player = None
    action = None
    assist = None

    if 'Official TV Timeout' in action_text:
        action = 'Official TV Timeout'
    elif 'End of 1st half' in action_text:
        action = 'End of 1st half'
    elif 'End of Game' in action_text:
        action = 'End of Game'

    elif 'made Three Point Jumper' in action_text:
        action = 'made Three Point Jumper'
        player = action_text.split(action)[0].strip()
    elif 'missed Three Point Jumper' in action_text:
        action = 'missed Three Point Jumper'
        player = action_text.split(action)[0].strip()
    elif 'made Jumper' in action_text:
        action = 'made Jumper'
        player = action_text.split(action)[0].strip()
    elif 'missed Jumper' in action_text:
        action = 'missed Jumper'
        player = action_text.split(action)[0].strip()
    elif 'made Two Point Tip Shot' in action_text:
        action = 'made Two Point Tip Shot'
        player = action_text.split(action)[0].strip()
    elif 'missed Two Point Tip Shot' in action_text:
        action = 'missed Two Point Tip Shot'
        player = action_text.split(action)[0].strip()
    elif 'made Layup' in action_text:
        action = 'made Layup'
        player = action_text.split(action)[0].strip()
    elif 'missed Layup' in action_text:
        action = 'missed Layup'
        player = action_text.split(action)[0].strip()
    elif 'made Free Throw' in action_text:
        action = 'made Free Throw'
        player = action_text.split(action)[0].strip()
    elif 'missed Free Throw' in action_text:
        action = 'missed Free Throw'
        player = action_text.split(action)[0].strip()
    elif 'made Dunk' in action_text:
        action = 'made Dunk'
        player = action_text.split(action)[0].strip()
    elif 'missed Dunk' in action_text:
        action = 'missed Dunk'
        player = action_text.split(action)[0].strip()
    elif 'Turnover' in action_text:
        action = 'Turnover'
        player = action_text.split(action)[0].strip()
    elif 'Steal' in action_text:
        action = 'Steal'
        player = action_text.split(action)[0].strip()
    elif 'Block' in action_text:
        action = 'Block'
        player = action_text.split(action)[0].strip()
    elif 'Offensive Rebound' in action_text:
        action = 'Offensive Rebound'
        player = action_text.split(action)[0].strip()
    elif 'Defensive Rebound' in action_text:
        action = 'Defensive Rebound'
        player = action_text.split(action)[0].strip()
    elif 'Deadball Team Rebound' in action_text:
        action = 'Deadball Team Rebound'
        player = action_text.split(action)[0].strip()
    elif 'Timeout' in action_text:
        action = 'Timeout'
        player = action_text.split(action)[0].strip()
    elif 'Jump Ball' in action_text:
        action = 'Jump Ball'
        player = action_text.split(action)[-1].strip()
    elif 'Foul on' in action_text:
        action = 'Foul'
        player = action_text.split('Foul on')[-1].strip()
    
    else:
        print(f"{action_text} not handled")
        exit(0)

    if 'Assisted by' in action_text:
        assist = action_text.split('Assisted by')[-1].strip()[:-1]

    return player, action, assist

def get_plays():
    r = requests.get(PBP_URL)
    soup = BeautifulSoup(r.content, 'html5lib')
    raw_halves = soup.find_all('div', attrs={'class': 'accordion-content'})[1:]
    plays = []
    for half_num, raw_half in enumerate(raw_halves):
        raw_plays = raw_half.find('tbody').find_all('tr')
        half_num += 1 # 1-indexing instead of 0-indexing
        for raw_play in raw_plays:
            play = {}
            play_cols = raw_play.find_all('td')
            play['time'] = play_cols[0].get_text()
            play['period'] = half_num
            (player, action, assist) = get_action_from_play(play_cols[2].get_text())
            play['actor'] = player
            play['action'] = action
            play['assist'] = assist

            plays.append(play)
    
    if VERBOSE:
        pprint.pprint(plays)

    return plays

def get_roster():
    r = requests.get(RST_URL)
    soup = BeautifulSoup(r.content, 'html5lib')

    roster = []
    raw_players = soup.find_all('tr', attrs={'class': 'Table__TR Table__TR--lg Table__even'})

    for raw_player in raw_players:
        player_cols = raw_player.find_all('td', attrs={'class':'Table__TD'})
        roster.append({
            'name': player_cols[1].find('a').get_text(),
            'number': player_cols[1].find('span').get_text(),
            'position': player_cols[2].get_text(),
            'height': player_cols[3].get_text(),
            'weight': player_cols[4].get_text(),
            'class': player_cols[5].get_text()
        })

    if VERBOSE:
        pprint.pprint(roster)

    return roster

###         ###
# Main Runner #
###         ###
if __name__ == '__main__':
    # get_teams()
    # get_schedule()
    # get_roster()
    get_plays()