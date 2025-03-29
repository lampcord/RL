import pandas as pd
import numpy as np
import os
from datetime import datetime

trace = True
#trace = False

def get_season_data(year):
    filename = str(year) + ".csv"
    if os.path.exists(filename):
        print(f"Reading {filename}...")
        data = pd.read_csv(filename)
    else:
        url = "https://www.pro-football-reference.com/years/" + str(year) + "/games.htm"
        print(f"Retrieving {url}...")
        data = pd.read_html(url)[0]
        data.to_csv(filename, index=False)
    return data


def create_initial_ratings(data, final_week):
    winners = data["Winner/tie"]

    teams = []
    week0 = []
    for w in winners:
        if w == 'Visitor': continue
        if w == 'Winner/tie': continue
        if w in teams: continue
        if pd.isnull(w): continue
        teams.append(w)
        if w in final_week:
            week0.append(final_week[w])
        else:
            week0.append(100.00)

    teamsdf = pd.DataFrame({'Team':teams})
    teamsdf["Rating_0"] = week0
    
    weeksdf = data['Week']
    weeks = []
    for w in weeksdf:
        if w == 'Week': continue
        if pd.isnull(w): continue
        if w not in weeks:
            weeks.append(w)

    return teamsdf, weeks

def calc_hfa(data):
    total_home_score = 0.0;
    total_vis_score = 0.0;

    count = 0.0
    for index, row in data.iterrows():
        try:
            homepts = int(row['PtsL'])
        except:
            continue

        home = row['Unnamed: 5']
        if home == '@':
            total_home_score += int(row['PtsL'])
            total_vis_score += int(row['PtsW'])
        else:
            total_home_score += int(row['PtsW'])
            total_vis_score += int(row['PtsL'])
        count += 1.0

    #print(f'home {total_home_score} vis {total_vis_score} count {count}')
    hfa = 3.0
    if count > 0.0:
        hfa = (total_home_score - total_vis_score) / count;
    if trace: print(f'Home Field Advantage {hfa}')
    return hfa

def calc_week(data, teamsdf, hfa, lw, w, adj_factor, records):
    #print(teamsdf.columns.values)

    # get oponents for this week
    week = data.loc[data['Week'] == str(w)]
    if week.shape[0] == 0:
        return False

    #print(week)
    lastweek = 'Rating_' + str(lw)
    thisweek = 'Rating_' + str(w)
    result = False
    
    #for index, row in week.iterrows():
    #    try:
    #        homepts = int(row['PtsL'])
    #    except:
    #        return False, lastweek, 0, 0, 0

    # copy previous weeks ratings
    teamsdf[thisweek] = teamsdf[lastweek]

    right = 0
    wrong = 0
    sos = 0
    for index, row in week.iterrows():
        update = True
        winner = row['Winner/tie']
        loser = row['Loser/tie']
        home = row['Unnamed: 5']
        try:
            winpts = int(row['PtsW'])
            lospts = int(row['PtsL'])
        except:
            winpts = 0
            lospts = 0
            update = False

        if home == '@':
            hometeam = loser
            visteam = winner
            homepts = lospts
            vispts = winpts
        else:
            hometeam = winner
            visteam = loser
            homepts = winpts
            vispts = lospts

        homerating = teamsdf.loc[teamsdf['Team'] == hometeam, lastweek].values[0]
        visrating = teamsdf.loc[teamsdf['Team'] == visteam, lastweek].values[0]

        expected = homerating + hfa - visrating
        if expected > 17.0: expected = 17.0
        if expected < -17.0: expected = -17.0


        result = homepts - vispts
        if result > 17.0: result = 17.0
        if result < -17.0: result = -17.0

        hrecord = records.get(hometeam, [0,0,0])
        vrecord = records.get(visteam, [0,0,0])
        if update:
            if result >= 0:
                hrecord[0] = hrecord[0] + 1
                vrecord[1] = vrecord[1] + 1
            else:
                hrecord[1] = hrecord[1] + 1
                vrecord[0] = vrecord[0] + 1
        else:
            if expected >= 0:
                hrecord[0] = hrecord[0] + 1
                vrecord[1] = vrecord[1] + 1
            else:
                hrecord[1] = hrecord[1] + 1
                vrecord[0] = vrecord[0] + 1
        records[hometeam] = hrecord
        records[visteam] = vrecord

        sos += (expected - result) * (expected - result)

        if np.sign(result) == np.sign(expected):
            right += 1
        else:
            wrong += 1
        adjustment = (result - expected) * adj_factor
        newhome = homerating + adjustment
        newvis = visrating - adjustment
        if update:
            teamsdf.loc[teamsdf['Team'] == hometeam, thisweek] = newhome
            teamsdf.loc[teamsdf['Team'] == visteam, thisweek] = newvis
        else:
            print(f'{visteam:25} ({visrating:3}) at {hometeam:25} ({homerating:6})  {expected:6}')
            
        result = True

       


    return result, thisweek, right, wrong, sos, records


def print_ratings(teamsdf, thisweek):
    print('=' * 80)
    print(thisweek)
    print('-' * 80)
    sortedteamsdf = teamsdf.sort_values(by=thisweek, ascending=False)
    rank = 1
    for index, row in sortedteamsdf.iterrows():
        print(f'{rank:2}) {row["Team"]:25} {row[thisweek]}')
        rank += 1
    print('=' * 80)
    print('')


def calc_year(y, adj_factor, final_week = {}):
    data = get_season_data(y)
    hfa = calc_hfa(data)
    teamsdf, weeks = create_initial_ratings(data, final_week)

    lw = '0'
    total_right = 0
    total_wrong = 0
    final_sos = 0
    records = {}
    for w in weeks:
        result, thisweek, right, wrong, sos, records = calc_week(data, teamsdf, hfa, lw, w, adj_factor, records)
        if not result: break
        final_sos += sos
        if trace: print_ratings(teamsdf, thisweek)  
        total_right += right
        total_wrong += wrong
        if trace: print(f'{right}/{right+wrong}')
        if trace: print(f'{total_right}/{total_right + total_wrong}')
        lw = w

        sorted_keys = sorted(records.keys(), key=lambda k: records[k][0], reverse=True)
        for team in sorted_keys:
            print(f'{team:25} {records[team]}')

    final_week = {}
    for index, row in teamsdf.iterrows():
        final_week[row["Team"]] = row[thisweek]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    teamsdf.to_csv(f'ratings_{y}_{timestamp}.txt', index=False)
    return float(total_right) / (total_right + total_wrong), final_week, final_sos
    


def find_lowest_consecutive_sum(float_list):
    if len(float_list) < 2:
        return None  # Not enough elements to form a pair

    lowest_sum = float('inf')  # Start with the highest possible sum
    lowest_pair = (None, None)

    for i in range(len(float_list) - 1):
        current_sum = float_list[i][1] + float_list[i + 1][1]
        if current_sum < lowest_sum:
            lowest_sum = current_sum
            lowest_pair = (float_list[i], float_list[i + 1])

    return lowest_pair, lowest_sum

def solver(minv, maxv, fn, depth = 5, cache = {}):
    distance = maxv - minv
    delta = distance / 4.0
    test = minv
    values = []
    cache_count = 0
    for x in range(5):
        if test in cache:
            result = cache[test]
            cache_count += 1
        else:
            result = fn(test)
            cache[test] = result

        values.append((test,result))
        test += delta

    # print(values)
    lowest_pair, lowest_sum = find_lowest_consecutive_sum(values)
    # print(lowest_pair, cache_count)
    # print(cache)
    depth -= 1
    if depth <= 0:
        return (lowest_pair[0][0] + lowest_pair[1][0]) / 2.0

    return solver(lowest_pair[0][0], lowest_pair[1][0], fn, depth, cache)

def regress_to_mean(final_week, pct):
    for team in final_week.keys():
        current = final_week[team]
        newval = current * (1.0 - pct) + 100.0 * pct
        final_week[team] = newval
    return final_week


adj_factor = 0.130859375
reg_to_mean_pct = 0.34130859375

def f(v):
    result, final_week, sos = calc_year(2022, v)
    final_week = regress_to_mean(final_week, reg_to_mean_pct)
    result, final_week, sos = calc_year(2023, v, final_week)
    print(f'{v:20} {sos}')
    #return 1.0 - result
    return sos

#result = solver(0.0, 0.5, f)
#print(result)

def g(v):
    result, final_week, sos = calc_year(2022, adj_factor)
    final_week = regress_to_mean(final_week, v)
    result, final_week, sos = calc_year(2023, adj_factor, final_week)
    print(f'{v:20} {result}')
    return 1.0 - result

#result = solver(0.0, 0.5, g)
#print(result)

if trace:
    results, final_week, sos = calc_year(2022, adj_factor)
    final_week = regress_to_mean(final_week, reg_to_mean_pct)
    results, final_week, sos = calc_year(2023, adj_factor, final_week)
    final_week = regress_to_mean(final_week, reg_to_mean_pct)
    results, final_week, sos = calc_year(2024, adj_factor, final_week)



