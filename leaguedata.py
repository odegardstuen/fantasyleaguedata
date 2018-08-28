# -*- coding: utf-8 -*-
"""
Created on Mon Aug 20 15:04:23 2018

@author: ANODEG
"""

import requests
import pandas as pd
#from bokeh.io import output_file, show
from bokeh.palettes import brewer
from bokeh.models import ColumnDataSource, TapTool, HoverTool, DataTable, TableColumn, Div
from bokeh.plotting import figure
from bokeh.layouts import layout
from bokeh.models.widgets import TextInput
from bokeh.io import curdoc

# Create Input controls
leagueID = TextInput(title="League ID:")
#pageNo = TextInput(title="League ID:")

leagueID.value = '452368'
#leagueID.value = '570516'
#leagueID.value = '718332'
# Enter league ID


# get current gameweek:
fpl_data = requests.get('https://fantasy.premierleague.com/drf/bootstrap-static').json()
N = len(fpl_data['elements'])

allplayers = {}
allplayers['web_name'] = [None] * N
allplayers['total_points'] = [None] * N
allplayers['team'] = [None] * N
allplayers['now_cost'] = [None] * N
allplayers['element_type'] = [None] * N
allplayers['id'] = [None] * N
allplayers['bonus'] = [None] * N
allplayers['bps'] = [None] * N
allplayers['minutes'] = [None] * N
allplayers['selected_by_percent'] = [None] * N
allplayers['form'] = [None] * N
allplayers['threat'] = [None] * N
allplayers['creativity'] = [None] * N
allplayers['value_form'] = [None] * N
allplayers['value_season'] = [None] * N
allplayers['assists'] = [None] * N
allplayers['goals_scored'] = [None] * N
allplayers['ict_index'] = [None] * N
allplayers['transfers_in'] = [None] * N
allplayers['transfers_in_event'] = [None] * N
allplayers['transfers_out'] = [None] * N
allplayers['transfers_out_event'] = [None] * N
allplayers['event_points'] = [None] * N
allplayers['influence'] = [None] * N

for i in range(N):
    for key in allplayers.keys():
        allplayers[key][i] = fpl_data['elements'][i][key]
        if type(allplayers[key][i]) == str:
            try:
                allplayers[key][i] = float(allplayers[key][i])
            except:
                None

positions = ['GK','DEF','MID','FWD']
allplayers['team_name'] = [None] * N
allplayers['position'] = [None] * N
for i in range(N):
    allplayers['team_name'][i] = fpl_data['teams'][allplayers['team'][i]-1]['name']
    allplayers['position'][i] = positions[allplayers['element_type'][i]-1]

currentGW = fpl_data['current-event']


teams = [None] * 20
teamind = {}
teamstrength = []
for i in range(len(teams)):
    teams[i] = fpl_data['teams'][i]['name']
    teamstrength.append(fpl_data['teams'][i]['strength'])
    teamind[teams[i]] = i
del allplayers['team']

data = pd.DataFrame.from_dict(allplayers)
data['now_cost'] = data['now_cost']/10


# Default source 1 
gameweeks = []
teampos = []
teamcost = []  
teamData = {'Team' : []}
#GWpoints = {'Teams' : []}
for GW in range(currentGW):
    gameweeks.append(str(GW+1))
    instr = str(GW+1)
    teamData[instr] = []
#    GWpoints[instr] = []
#source1 = ColumnDataSource(GWpoints)


# Default source2pool
#teampos = []
#teamcost = []  
#teamData = {'Team' : []}
for position in range(18):
    teampos.append('Pos' + str(position+1))
    teamcost.append('Cost' + str(position+1))
    
    coststr = 'Cost' + str(position+1)
    posstr = 'Pos' + str(position+1)
    namestr = 'Name' + str(position+1)
    
    teamData[coststr] = []
    teamData[posstr] = []
    teamData[namestr] = []
source1 = ColumnDataSource(teamData)

#source2pool = ColumnDataSource(teamData)



# Default source 2
teampos = []
teamcost = []  
teamData = {'Team' : []}
for position in range(18):
    teampos.append('Pos' + str(position+1))
    teamcost.append('Cost' + str(position+1))
    coststr = 'Cost' + str(position+1)
    posstr = 'Pos' + str(position+1)
    teamData[coststr] = []
    teamData[posstr] = []
source2 = ColumnDataSource(teamData)




# Generate colors
Paired = brewer['Paired'][12]
colors = []
while len(gameweeks) != len(colors):
    diff = len(gameweeks)-len(colors)
    if diff>12:
        colors.extend(Paired)
    else:
        colors.extend(Paired[:diff])


colors2 = []
colors2.extend(['#1b9e77'])     # GK
colors2.extend(['#d95f02']*5)   # DEF
colors2.extend(['#7570b3']*5)   # MID
colors2.extend(['#e7298a']*3)   # FWD
colors2.extend(['#d3d3d3']*4)   # Bench
                
                
p1 = figure(y_range=[], plot_height=700,plot_width = 800, toolbar_location=None,tools=[HoverTool(), TapTool()], tooltips='GW $name: @$name')
p1.hbar_stack(gameweeks, y='Team', height=0.9,color=colors, source=source1, legend=["GW %s" % x for x in gameweeks],line_width = 1,line_color = 'black')

p1.y_range.range_padding = 0.1
p1.ygrid.grid_line_color = None
p1.legend.location = "bottom_right"
p1.axis.minor_tick_line_color = None
p1.outline_line_color = None
p1.title.text = 'Points'

p2 = figure(y_range=[], plot_height=700,toolbar_location=None,tools=[HoverTool(), TapTool()], tooltips='@$name{0.0 a}')
p2.hbar_stack(teamcost, y='Team', height=0.9,line_width = 1,line_color = 'black', source=source1, color = colors2)

p2.y_range.range_padding = p1.y_range.range_padding
p2.ygrid.grid_line_color = None
p2.axis.minor_tick_line_color = None
p2.outline_line_color = None
#p2.yaxis.axis_label = p1.yaxis.axis_label 
p2.title.text  = 'Squad cost'


# Table for selected team
tablesource_team = ColumnDataSource(data = dict(position=[], web_name=[], club=[], cost=[]))
tablesource_bench = ColumnDataSource(data = dict(position=[], web_name=[], club=[], cost=[]))

columns = [
        TableColumn(field='position', title='Pos'),
        TableColumn(field='web_name', title='Name'),
        TableColumn(field='club', title='Club'),
        TableColumn(field='cost', title='Cost'),
        ]

teamtable = DataTable(source=tablesource_team, columns=columns, width=350, height=300, name = '', index_position = None)
benchtable = DataTable(source=tablesource_bench, columns=columns, width=350, height=200, name = 'Bench', index_position = None)

teamtableheader = Div(text = "Team")
benchtableheader = Div(text = '<b><font color="#444444"> Bench<b></font>')
#444444
def leagueupdate():

#    reset_output(p)
    
    # Get league participants
    leagueinfo = requests.get('https://fantasy.premierleague.com/drf/leagues-classic-standings/'+ leagueID.value).json()
    memberIDs = []
    for i in range(len(leagueinfo['standings']['results'])):
        memberIDs.append(leagueinfo['standings']['results'][i]['entry'])
    
    
    teamdata = {}
    # Create data for each participant
    for memberID in memberIDs:
        memberhistory = requests.get(r'https://fantasy.premierleague.com/drf/entry/' + str(memberID) + '/history').json()
        memberteam = requests.get(r'https://fantasy.premierleague.com/drf/entry/' + str(memberID) +'/event/' + str(currentGW) + '/picks').json()
        
        teamname = memberhistory['entry']['name']
        teamdata[teamname] = {'GW points': [], 'GW transfercost': [], 'GW net points':[], 'total points':[]}
        
        # member GW history
        for GW in range(len(memberhistory['history'])):
            teamdata[teamname]['GW points'].append(int(memberhistory['history'][GW]['points']))
            teamdata[teamname]['GW transfercost'].append(int(memberhistory['history'][GW]['event_transfers_cost']))
            teamdata[teamname]['GW net points'].append(teamdata[teamname]['GW points'][GW] - teamdata[teamname]['GW transfercost'][GW])
            if GW == 0:
                teamdata[teamname]['total points'].append(teamdata[teamname]['GW net points'][GW])
            else:
                teamdata[teamname]['total points'].append(teamdata[teamname]['GW net points'][GW] + teamdata[teamname]['total points'][GW-1])
        
        # Current team value distribution
        cost_teamsum = [0,0,0,0,0] 
        formation_team = [None] * 15
        positionstr_team = [None] * 15 
        cost_team = [None] * 15
        web_name = [None] * 15
        club_name = [None] * 15 
        for footballer in memberteam['picks']:
            
            position = data[data.id == footballer['element']]['element_type'].iloc[0]
            positionstr = data[data.id == footballer['element']]['position'].iloc[0]
            cost = data[data.id == footballer['element']]['now_cost'].iloc[0]
            name =  data[data.id == footballer['element']]['web_name'].iloc[0]
            club =  data[data.id == footballer['element']]['team_name'].iloc[0]
            
            cost_team[footballer['position']-1] = cost
            web_name[footballer['position']-1] = name
            club_name[footballer['position']-1] = club
            positionstr_team[footballer['position']-1] = positionstr
            
            if footballer['position']<12:
                formation_team[footballer['position']-1] = str(position)
                cost_teamsum[position-1] = cost_teamsum[position-1] + cost
            else:
                formation_team[footballer['position']-1] = '5'
                cost_teamsum[4] = cost_teamsum[4] + cost
        
        teamdata[teamname]['team posstr'] = positionstr_team
        teamdata[teamname]['team webname'] = web_name
        teamdata[teamname]['team clubs'] = club_name    
        teamdata[teamname]['team cost'] = cost_team
        teamdata[teamname]['team cost summed'] = cost_teamsum
        teamdata[teamname]['team formation'] = formation_team
    
    team_names = list(teamdata.keys())
    team_names.reverse()

    # Re-format data to fit Bokeh
    teamDict = {'Team' : team_names}
    # Data for plot 1:
    for gameweek in range(GW+1):
        GWstr = str(gameweek+1)
        teamDict[GWstr] = [None] *len(team_names)
        teamind = 0
        for team in team_names:
            teamDict[GWstr][teamind] = teamdata[team]['GW net points'][gameweek]
            teamind += 1

   
    # Data for table:
    for position in range(15):
       
        posstr = 'TablePos' + str(position+1)
        namestr = 'TableName' + str(position+1)
        clubstr = 'TableClub' +  str(position+1)
        coststr = 'TableCost' + str(position+1)
        
        teamDict[posstr] = [None] *  len(team_names)
        teamDict[namestr] = [None] *  len(team_names)
        teamDict[clubstr] = [None] *  len(team_names)
        teamDict[coststr] = [None] * len(team_names)
        
        teamind = 0
        for teamname in team_names:
            teamDict[posstr][teamind] = teamdata[teamname]['team posstr'][position]
            teamDict[namestr][teamind] = teamdata[teamname]['team webname'][position]
            teamDict[clubstr][teamind] = teamdata[teamname]['team clubs'][position]
            teamDict[coststr][teamind] = teamdata[teamname]['team cost'][position]
            teamind += 1
        
        
    
    poscount = {team:0 for team in team_names}
    for position in range(18):

        coststr = 'Cost' + str(position+1)
        posstr = 'Pos' + str(position+1)
        namestr = 'Name' + str(position+1)
        
        teamDict[coststr] = [0] * len(team_names)
        teamDict[posstr] = ['0'] *  len(team_names)
        teamDict[namestr] = ['0'] *  len(team_names)
        
        teamind = 0
        for teamname in team_names:
            
            currentpos = int(teamdata[teamname]['team formation'][poscount[teamname]])
           
            if position == 0 and currentpos == 1: # Add GK
                teamDict[coststr][teamind] = teamdata[teamname]['team cost'][poscount[teamname]]
                teamDict[posstr][teamind] = str(teamdata[teamname]['team formation'][poscount[teamname]])
                poscount[teamname] += 1
                
            elif position > 0 and position < 6 and currentpos == 2: #Add Def
                teamDict[coststr][teamind] = teamdata[teamname]['team cost'][poscount[teamname]]
                teamDict[posstr][teamind] = str(teamdata[teamname]['team formation'][poscount[teamname]])
                poscount[teamname] += 1
                
            elif position > 5 and position < 11 and currentpos == 3: #Add Mid
                teamDict[coststr][teamind] = teamdata[teamname]['team cost'][poscount[teamname]]
                teamDict[posstr][teamind] = str(teamdata[teamname]['team formation'][poscount[teamname]])
                poscount[teamname] += 1
                
            elif position > 10 and position < 14 and currentpos == 4:  #Add Fwd
                teamDict[coststr][teamind] = teamdata[teamname]['team cost'][poscount[teamname]]
                teamDict[posstr][teamind] = str(teamdata[teamname]['team formation'][poscount[teamname]])
                poscount[teamname] += 1
                
            elif position > 13 and currentpos == 5:               #Add Bench
                teamDict[coststr][teamind] = teamdata[teamname]['team cost'][poscount[teamname]]
                teamDict[posstr][teamind] = str(teamdata[teamname]['team formation'][poscount[teamname]])
                poscount[teamname] += 1
               
            teamind += 1

    p1.y_range.factors = team_names
    p2.y_range.factors = team_names
    source1.data = teamDict
#    source1.data = GWpoints
#    source2pool.data = teamDict

def selectupdate(attrname, old, new):

    if len(source1.selected.indices)>0:
            
        
        # Team
        selectionIndex = source1.selected.indices[0]
        positions = []
        names = []
        clubs = []
        costs = []
        teamtableheader.text = '<b><font color="#444444">'+ source1.data['Team'][selectionIndex] + '<b></font>'
        
        
        for position in range(11):
            posstr = 'TablePos' + str(position+1)
            namestr = 'TableName' + str(position+1)
            clubstr = 'TableClub' +  str(position+1)
            coststr = 'TableCost' + str(position+1)

            positions.append(source1.data[posstr][selectionIndex])
            names.append(source1.data[namestr][selectionIndex])
            clubs.append(source1.data[clubstr][selectionIndex])
            costs.append(source1.data[coststr][selectionIndex])
             
        tablesource_team.data = dict(
                position = positions,
                web_name = names,
                club = clubs,
                cost = costs)
        
        # Bench
        positions = []
        names = []
        clubs = []
        costs = []
       
        for position in range(11,15):
            posstr = 'TablePos' + str(position+1)
            namestr = 'TableName' + str(position+1)
            clubstr = 'TableClub' +  str(position+1)
            coststr = 'TableCost' + str(position+1)

            positions.append(source1.data[posstr][selectionIndex])
            names.append(source1.data[namestr][selectionIndex])
            clubs.append(source1.data[clubstr][selectionIndex])
            costs.append(source1.data[coststr][selectionIndex])
             
        tablesource_bench.data = dict(
                position = positions,
                web_name = names,
                club = clubs,
                cost = costs)
        
        
leagueupdate()  # initial load of the data    
    
#controls = [leagueID]
#for control in controls:
#    control.on_change('value', lambda attr, old, new: leagueupdate())

leagueID.on_change('value', lambda attr, old, new: leagueupdate())

source1.on_change('selected', selectupdate)

sizing_mode = 'fixed'  # 'scale_width' also looks nice with this example

#inputs = widgetbox(*controls, sizing_mode=sizing_mode)

l = layout([
    leagueID,
    [p1,p2,[teamtableheader,teamtable,benchtableheader,benchtable]],
])


curdoc().add_root(l)
curdoc().title = "LeagueData"
    
    
    
    