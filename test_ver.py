# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 21:00:08 2024

@author: bac0n
"""
#library imports
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
#1. Treat like an expected value problem
#2. Calculate using 10 years of RE 24


#data imports for estimating value
#the following information is derived based on league performance from 2015-2024
batting_splits_real = pd.read_csv("irl_splits_2015-2024.csv")
batter_splits_real = pd.read_csv("2015-2024_individuals.csv")
batting_splits_real_by_type = pd.read_csv("irl_splits_2015-2024_by_hit_type.csv")
game_state_probabilities = pd.read_csv("game_state_probabilities.csv")
#drop columns that can interfere later
columns_to_drop = ["I","tOPS+","sOPS+","Rk"]
columns_to_drop_by_type = ["I","tOPS+","sOPS+","GS","Rk"]
for column in columns_to_drop:
    batting_splits_real.drop(column, axis=1, inplace=True)
for column in columns_to_drop_by_type:
    batting_splits_real_by_type.drop(column, axis=1, inplace=True)

class batting_model():
    def __init__(self,model_type="large",type_splits="Yes",player_name="NO_NAME"):
        self.player_name = player_name
        self.model_type = model_type
        self.type_splits = type_splits
        self.real_averages = {}
        self.derived_averages = {}
        self.outcome_by_type = {}
        if (type_splits == "Yes"):
            self.real_averages_by_type = {}
            self.derived_averages_by_type = {}
       
        
    def setup(self):
        #first val is wanted stat, second is what it's rounded to. should be 3 for % stats, 0 for counting stats
        wanted_averages = [["BA",3], ["OBP",3], ["AB",0], ["PA",0], ["BB",0], ["HBP",0], ["SF",0], ["SH",0], ["H",0], ["2B",0] , ["3B",0], ["HR",0], ["SO",0], ["GDP",0], ["ROE",0]]
        wanted_averages_by_type = [["AB",0], ["PA",0], ["SF",0], ["SH",0], ["H",0], ["2B",0] , ["3B",0], ["HR",0], ["GDP",0], ["ROE",0], ["Out",0]]
        wanted_averages_derived = [["BB%", 3], ["HBP%",3], ["SH%",3], ["SF%",3], ["H%",3], ["2B%",3], ["3B%",3], ["HR%",3], ["SO%",3], ["GDP%",3], ["ROE%",3]]
        wanted_averages_derived_by_type = [["SH%",3], ["SF%",3], ["H%",3], ["2B%",3], ["3B%",3], ["HR%",3], ["GDP%",3], ["ROE%",3], ["Out%",3]]
        #real is given, derived is sorta given but not really

        #derivation of averages non-exclusive
        for stat in range(len(wanted_averages)):
            self.real_averages[wanted_averages[stat][0]] = round(sum(batting_splits_real[wanted_averages[stat][0]])/len(batting_splits_real[wanted_averages[stat][0]]),wanted_averages[stat][1])
        for stat in range(len(wanted_averages_derived)):
            self.derived_averages[wanted_averages_derived[stat][0]] = self.real_averages[wanted_averages_derived[stat][0][0:len(wanted_averages_derived[stat][0]) - 1]]/(self.real_averages["PA"])

        #type splits are the different type of splits
        type_split = ["Bunts","Fly Balls","Ground Balls","Line Drives"]
        #derivation of averages type-exclusive
        columns = batting_splits_real_by_type.columns.values.tolist()
        for contact_type in type_split:
            self.real_averages_by_type[contact_type] = {}
            self.derived_averages_by_type[contact_type] = {}
            for column in range(len(columns)):
                self.real_averages_by_type[contact_type][columns[column]] = 0
        
        for contact_type in type_split:
            for i in range(len(batting_splits_real_by_type)):
                for z in range(len(columns)):
                    stat = batting_splits_real_by_type.loc[i][z]
                    if (stat == "Bunts" or stat == "Fly Balls" or stat == "Ground Balls" or stat == "Line Drives"):
                        pass
                    elif (stat):
                        if batting_splits_real_by_type.loc[i][0] == contact_type:
                            self.real_averages_by_type[contact_type][columns[z]] = self.real_averages_by_type[contact_type][columns[z]] + stat
                    
        for contact_type in type_split:
            for avg in wanted_averages_by_type:
                self.real_averages_by_type[contact_type][avg[0]] = round(self.real_averages_by_type[contact_type][avg[0]]/len(batting_splits_real),avg[1])

        for contact_type in type_split:
            for avg in wanted_averages_derived_by_type:
                if self.real_averages_by_type[contact_type][avg[0][0:len(avg[0]) - 1]] != 0:
                    if avg[0] == "Out%":
                        self.derived_averages_by_type[contact_type][avg[0]] = (self.real_averages_by_type[contact_type][avg[0][0:len(avg[0]) - 1]]-self.real_averages_by_type[contact_type]["GDP"])/(self.real_averages_by_type[contact_type]["PA"])
                    else:
                        
                        self.derived_averages_by_type[contact_type][avg[0]] = self.real_averages_by_type[contact_type][avg[0][0:len(avg[0]) - 1]]/(self.real_averages_by_type[contact_type]["PA"])
            
        #derivation of type specificity/type outs
        out_by_type = {}
        #bunts are double counted if included here
        #GDP would cause issues with total calculation if not subtracted (doublecounted outs)
        for contact_type in type_split:
            if (contact_type == "Bunts"):
                pass
            elif (contact_type == "Ground Balls"):
                out_by_type[contact_type] = (self.real_averages_by_type[contact_type]["Out"]-self.real_averages_by_type[contact_type]["GDP"])/self.real_averages["PA"]
            else:
                out_by_type[contact_type] = self.real_averages_by_type[contact_type]["Out"]/self.real_averages["PA"]
        
        #calculation of outcome by type
        outcome_types = ["BB%","HBP%","SO%","Ground Balls", "Fly Balls", "Line Drives","Bunts"]
        for outcome in outcome_types:
            if (outcome == "Ground Balls") or (outcome == "Fly Balls") or (outcome == "Line Drives") or (outcome == "Bunts"):
                self.outcome_by_type[outcome] = self.real_averages_by_type[outcome]["PA"]/self.real_averages["PA"]
            else:
                self.outcome_by_type[outcome] = self.derived_averages[outcome]
    
    def at_bat(self,outcome_table="GENERIC",type_tables="GENERIC"):
        if outcome_table == "GENERIC":
            random_gen = random.random()
            if random_gen < self.outcome_by_type["BB%"]:
                return "BB"
            elif random_gen < (self.outcome_by_type["BB%"] + self.outcome_by_type["HBP%"]):
                return "HBP"
            elif random_gen < (self.outcome_by_type["BB%"] + self.outcome_by_type["HBP%"] + self.outcome_by_type["SO%"]):
                return "SO"
            elif random_gen < (self.outcome_by_type["BB%"] + self.outcome_by_type["HBP%"] + self.outcome_by_type["SO%"] + self.outcome_by_type["Ground Balls"]):
                type_random = random.random()
                if type_random < self.derived_averages_by_type["Ground Balls"]["ROE%"]:
                    return "ROE"
                elif type_random < (self.derived_averages_by_type["Ground Balls"]["ROE%"]+self.derived_averages_by_type["Ground Balls"]["3B%"]):
                    return "3B"
                elif type_random < (self.derived_averages_by_type["Ground Balls"]["ROE%"]+self.derived_averages_by_type["Ground Balls"]["3B%"]+self.derived_averages_by_type["Ground Balls"]["2B%"]):
                    return "2B"
                elif type_random < (self.derived_averages_by_type["Ground Balls"]["ROE%"]+self.derived_averages_by_type["Ground Balls"]["H%"]):
                    return "1B"
                elif type_random < (self.derived_averages_by_type["Ground Balls"]["ROE%"]+self.derived_averages_by_type["Ground Balls"]["H%"] + self.derived_averages_by_type["Ground Balls"]["GDP%"]):
                    return "GDP"
                else:
                    return "GO"
            elif random_gen < (self.outcome_by_type["BB%"] + self.outcome_by_type["HBP%"] + self.outcome_by_type["SO%"] + self.outcome_by_type["Ground Balls"] + self.outcome_by_type["Fly Balls"]):
                type_random = random.random()
                if type_random < self.derived_averages_by_type["Fly Balls"]["ROE%"]:
                    return "ROE"
                elif type_random < (self.derived_averages_by_type["Fly Balls"]["ROE%"]+self.derived_averages_by_type["Fly Balls"]["HR%"]):
                    return "HR"
                elif type_random < (self.derived_averages_by_type["Fly Balls"]["ROE%"]+self.derived_averages_by_type["Fly Balls"]["HR%"] + self.derived_averages_by_type["Fly Balls"]["3B%"]):
                    return "3B"
                elif type_random < (self.derived_averages_by_type["Fly Balls"]["ROE%"]+self.derived_averages_by_type["Fly Balls"]["HR%"]+self.derived_averages_by_type["Fly Balls"]["3B%"]+self.derived_averages_by_type["Fly Balls"]["2B%"]):
                    return "2B"
                elif type_random < (self.derived_averages_by_type["Fly Balls"]["ROE%"]+self.derived_averages_by_type["Fly Balls"]["H%"]):
                    return "1B"
                elif type_random < (self.derived_averages_by_type["Fly Balls"]["ROE%"]+self.derived_averages_by_type["Fly Balls"]["H%"] + self.derived_averages_by_type["Fly Balls"]["SF%"]):
                    return "SF"
                else:
                    return "FO"
            elif random_gen < (self.outcome_by_type["BB%"] + self.outcome_by_type["HBP%"] + self.outcome_by_type["SO%"] + self.outcome_by_type["Ground Balls"] + self.outcome_by_type["Fly Balls"] + self.outcome_by_type["Line Drives"]):
                type_random = random.random()
                if type_random < self.derived_averages_by_type["Line Drives"]["ROE%"]:
                    return "ROE"
                elif type_random < (self.derived_averages_by_type["Line Drives"]["ROE%"]+self.derived_averages_by_type["Line Drives"]["HR%"]):
                    return "HR"
                elif type_random < (self.derived_averages_by_type["Line Drives"]["ROE%"]+self.derived_averages_by_type["Line Drives"]["HR%"] + self.derived_averages_by_type["Line Drives"]["3B%"]):
                    return "3B"
                elif type_random < (self.derived_averages_by_type["Line Drives"]["ROE%"]+self.derived_averages_by_type["Line Drives"]["HR%"]+self.derived_averages_by_type["Line Drives"]["3B%"]+self.derived_averages_by_type["Line Drives"]["2B%"]):
                    return "2B"
                elif type_random < (self.derived_averages_by_type["Line Drives"]["ROE%"]+self.derived_averages_by_type["Line Drives"]["H%"]):
                    return "1B"
                elif type_random < (self.derived_averages_by_type["Line Drives"]["ROE%"]+self.derived_averages_by_type["Line Drives"]["H%"] + self.derived_averages_by_type["Line Drives"]["SF%"]):
                    return "SF"
                else:
                    return "LO"
            else:
                type_random = random.random()
                if type_random < self.derived_averages_by_type["Bunts"]["ROE%"]:
                    return "ROE"
                elif type_random < (self.derived_averages_by_type["Bunts"]["ROE%"]+self.derived_averages_by_type["Bunts"]["2B%"]):
                    return "2B"
                elif type_random < (self.derived_averages_by_type["Bunts"]["ROE%"]+self.derived_averages_by_type["Bunts"]["H%"]):
                    return "1B"
                elif type_random < (self.derived_averages_by_type["Bunts"]["ROE%"]+self.derived_averages_by_type["Bunts"]["H%"] + self.derived_averages_by_type["Bunts"]["GDP%"]):
                    return "GDP"
                elif type_random < (self.derived_averages_by_type["Bunts"]["ROE%"]+self.derived_averages_by_type["Bunts"]["H%"] + self.derived_averages_by_type["Bunts"]["GDP%"] + self.derived_averages_by_type["Bunts"]["SH%"]):
                    return "SH"
                else:
                    return "BO"
    def full_season_batting_stats(self,outcome_table="GENERIC",type_tables="GENERIC",Plate_Appearances=600):
        season_stats = {"BA":0,"SLG":0,"OBP":0,"OPS":0,"PA":Plate_Appearances,"AB":0,"BB":0,"HBP":0,"SO":0,"H":0,"1B":0,"2B":0,"3B":0,"HR":0,"ROE":0,"GDP":0,"SF":0,"SH":0,"BO":0,"GO":0,"LO":0,"FO":0}
        for PA in range(Plate_Appearances):
            result = self.at_bat(outcome_table="GENERIC",type_tables="GENERIC")
            if (result == "HR") or (result == "3B") or (result == "2B") or (result == "1B"):
                season_stats[result] = season_stats[result] + 1
                season_stats["H"] = season_stats["H"] + 1
            else:
                season_stats[result] = season_stats[result] + 1
        season_stats["AB"] = season_stats["PA"] - season_stats["BB"] - season_stats["HBP"] - season_stats["SH"] - season_stats["SF"]
        season_stats["BA"] = round(season_stats["H"]/season_stats["AB"],3)
        season_stats["SLG"] = round((season_stats["HR"]*4 + season_stats["3B"]*3 + season_stats["2B"]*2 + season_stats["1B"])/season_stats["AB"],3)
        season_stats["OBP"] = round((season_stats["H"]+season_stats["BB"]+season_stats["HBP"])/season_stats["PA"],3)
        season_stats["OPS"] = round(season_stats["OBP"] + season_stats["SLG"],3)
        return season_stats 
    #1 = base loaded
    #2 = base empty
    def from_position(self,first,second,third,starting_outs,starting_outcome):
        bases = [first,second,third]
        at_bat = starting_outcome
        outs = starting_outs
        runs_scored = 0
        while(True):
            if at_bat == "BB" or at_bat == "HBP" or at_bat == "ROE":
                if bases[0] != 1:
                    bases[0] = 1
                elif bases == [1,1,1]:
                    runs_scored = runs_scored + 1
                elif bases[0] == bases[1] == 1:
                    bases[2] = 1
                elif bases[0] == bases[2] == 1:
                    bases[1] = 1
            elif at_bat == "FO" or at_bat == "GO" or at_bat == "SO" or at_bat == "BO":
                outs = outs + 1
            elif at_bat == "GDP":
                if (bases[0]+bases[1]+bases[2]) == 0:
                    outs = outs + 1
                elif(bases == [1,1,1]) and outs == 0:
                    luck = random.random()
                    if luck > 0.5:
                        bases = [1,0,0]
                        runs_scored = runs_scored + 1
                    else:
                        bases = [1,1,0]
                elif((bases == [1,1,0]) or (bases == [0,1,1]) or (bases == [1,0,1]) and (outs == 0)):    
                    luck = random.random()
                    if luck > 0.5:
                        bases == [1,0,0]
                    else:
                        bases == [0,1,0]
                else:
                    bases = [0,0,0]
                outs = outs + 2
            elif at_bat == "HR":
                for i in range(3):
                    if bases[i] == 1:
                        runs_scored= runs_scored + 1
                        bases[i] = 0
                runs_scored= runs_scored + 1
            elif at_bat == "3B":
                for i in range(3):
                    if bases[i] == 1:
                        runs_scored= runs_scored + 1
                        bases[i] = 0
                bases[2] = 1
            elif at_bat == "2B":
                luck = random.random()
                if bases[2] == 1:
                    runs_scored= runs_scored + 1
                    bases[2] = 0
                if bases[1] == 1:
                    runs_scored= runs_scored + 1
                    bases[1] = 0
                if bases[0] == 1:
                    if luck>0.65:
                        runs_scored= runs_scored + 1
                        bases[0] = 0
                    else:
                        bases[0] = 0
                        bases[2] = 1
                bases[1] = 1
            elif at_bat == "1B":
                luck = random.random()
                if bases[2] == 1:
                    runs_scored= runs_scored + 1
                    bases[2] = 0
                if bases[1] == 1:
                    if luck > 0.85:
                        runs_scored= runs_scored + 1
                        bases[1] = 0
                    else:
                        bases[2] = 1
                        bases[1] = 0
                if bases[0] == 1:
                    if luck > 0.99:
                        runs_scored= runs_scored + 1
                        bases[0] = 0
                    else:
                        bases[1] = 1
                bases[0] = 1
            elif (at_bat == "SF") or (at_bat == "SH"):
                if (outs < 2) and (bases[2] == 1):
                    runs_scored = runs_scored + 1
                    bases[2] = 0
                    outs = outs + 1
                else:
                    outs = outs + 1
            
            if outs >= 3:
                return runs_scored
            at_bat = self.at_bat()

#function for estimating the run value of different types of hit
def hit_run_vals(sim_model):
    matrix_1b = []
    matrix_2b = []
    matrix_3b = []
    matrix_hr = []
    for first in range(2):
        for second in range(2):
            for third in range(2):
                for out in range(3):
                    model_test_results = pd.DataFrame()
                    for sim in range(10000):
                        x = {"1B":sim_model.from_position(first,second,third,out,"1B"),"2B":sim_model.from_position(first,second,third,out,"2B"),"3B":sim_model.from_position(first,second,third,out,"3B"),"HR":sim_model.from_position(first,second,third,out,"HR")}
                        model_test_results[sim] = x
                    model_test_results = model_test_results.transpose()
                    single_distribution = model_test_results["1B"]
                    double_distribution = model_test_results["2B"]
                    triple_distribution = model_test_results["3B"]
                    homer_distribution = model_test_results["HR"]
                    plt.hist(single_distribution,bins=12,color="blue",edgecolor="black",alpha=0.5,label="1B Distribution")
                    plt.hist(double_distribution,bins=12,color="skyblue",edgecolor="black",alpha=0.5,label="2B Distribution")
                    plt.hist(triple_distribution,bins=12,color="green",edgecolor="black",alpha=0.5,label="3B Distribution")
                    plt.hist(homer_distribution,bins=12,color="red",edgecolor="black",alpha=0.5,label="HR Distribution")
                    plt.xlabel("Runs Scored")
                    plt.ylabel("Samples")
                    plt.title(f"{out} out(s), {first} on first, {second} on second, {third} on third")
                    plt.legend(loc='upper right')
                    plt.show()
                    print(f"{sum((single_distribution)/10000)} runs per single with {out} out(s), {first} on first, {second} on second, {third} on third")
                    print(f"{sum((double_distribution)/10000)} runs per double with {out} out(s), {first} on first, {second} on second, {third} on third")
                    print(f"{sum((triple_distribution)/10000)} runs per single with {out} out(s), {first} on first, {second} on second, {third} on third")
                    print(f"{sum((homer_distribution)/10000)} runs per home run with {out} out(s), {first} on first, {second} on second, {third} on third")
                    matrix_1b.append([f"{sum((single_distribution)/10000)}",[first,second,third,out]])
                    matrix_2b.append([f"{sum((double_distribution)/10000)}",[first,second,third,out]])
                    matrix_3b.append([f"{sum((triple_distribution)/10000)}",[first,second,third,out]])
                    matrix_hr.append([f"{sum((homer_distribution)/10000)}",[first,second,third,out]])
    out = [matrix_1b,matrix_2b,matrix_3b,matrix_hr]
    tot_1b = 0
    tot_2b = 0
    tot_3b = 0
    tot_hr = 0
    #normalization data taken from williams paper
    for val in range(len(out[0])):
        tot_1b = tot_1b + float(out[0][val][0])
    for val in range(len(out[1])):
        tot_2b = tot_2b + float(out[1][val][0])
    for val in range(len(out[2])):
        tot_3b = tot_2b + float(out[2][val][0])
    for val in range(len(out[1])):
        tot_hr = tot_hr + float(out[3][val][0])

    print(f"A single is worth {tot_1b/tot_hr} of a home run")
    print(f"A double is worth {tot_2b/tot_hr} of a home run")
    print(f"A triple is worth {tot_3b/tot_hr} of a home run")
    return [tot_1b/tot_hr,tot_2b/tot_hr,tot_3b/tot_hr]

#function for generating theoretical outcomes of a given season using a "probability table" (batting stats)
def full_season_isolated(sim_model,number_of_seasons=10000):
    model_test_results = pd.DataFrame()
    for sim in range(10000):
        model_test_results[sim] = sim_model.full_season_batting_stats()
    model_test_results = model_test_results.transpose()
    ba_distribution = model_test_results["OPS"]
    plt.hist(ba_distribution,bins=30,color="skyblue",edgecolor="black")
    plt.xlabel("OPS")
    plt.ylabel("Number of Batters")
    plt.title("Distribution of OPS for League Average Hitter")
    plt.show()
    real_distribution = batter_splits_real["OPS"]
    plt.hist(real_distribution,bins=30,color="skyblue",edgecolor="black")
    plt.xlabel("OPS")
    plt.ylabel("Number of Batters")
    plt.title("Distribution of OPS for Real Batters")
    plt.show()
    return model_test_results

#function for generating theoretical outcomes of a given season given a full lineup (batting stats)
def full_season_full_team_batting(lineup,number_of_seasons=10000):
    every_season_stats = {}
    for i in range(number_of_seasons): 
        full_team_stats = {}
        for z in range(9):
            full_team_stats[lineup[z].player_name] = {"BA":0,"SLG":0,"OBP":0,"OPS":0,"PA":0,"AB":0,"BB":0,"HBP":0,"SO":0,"H":0,"1B":0,"2B":0,"3B":0,"HR":0,"R":0,"RBI":0,"ROE":0,"GDP":0,"SF":0,"SH":0,"BO":0,"GO":0,"LO":0,"FO":0}
        for x in range(162):
            full_team_stats = full_team_game(lineup,full_team_stats)
        for q in range(9):
            full_team_stats[lineup[q].player_name]["BA"] = round(full_team_stats[lineup[q].player_name]["H"]/full_team_stats[lineup[q].player_name]["AB"],3)
            full_team_stats[lineup[q].player_name]["SLG"] = round((full_team_stats[lineup[q].player_name]["HR"]*4 + full_team_stats[lineup[q].player_name]["3B"]*3 + full_team_stats[lineup[q].player_name]["2B"]*2 + full_team_stats[lineup[q].player_name]["1B"])/full_team_stats[lineup[q].player_name]["AB"],3)
            full_team_stats[lineup[q].player_name]["OBP"] = round((full_team_stats[lineup[q].player_name]["H"]+full_team_stats[lineup[q].player_name]["BB"]+full_team_stats[lineup[q].player_name]["HBP"])/full_team_stats[lineup[q].player_name]["PA"],3)
            full_team_stats[lineup[q].player_name]["OPS"] = round(full_team_stats[lineup[q].player_name]["OBP"] + full_team_stats[lineup[q].player_name]["SLG"],3)
        every_season_stats[i] = full_team_stats
        print(i)
    return every_season_stats
                
#generates result of full game offensive production independent of winner/loser and defense
def full_team_game(lineup,full_team_stats):
    next_batter = 0
    for i in range(9):
        inning_results = full_team_inning(next_batter,lineup)
        for player in full_team_stats:
            for stat in full_team_stats[player]:
                full_team_stats[player][stat] = full_team_stats[player][stat] + inning_results[0][player][stat]
        next_batter = inning_results[1]
    return full_team_stats
            
#odds of scoring from a given base taken from williams paper
def full_team_inning(starting_batter,starting_lineup,splits_by_type="Yes"):
    bases = [0,0,0]
    current_batter = starting_batter
    #turnover the batting order if necessary
    if current_batter > 8:
        current_batter = 0
    at_bat = starting_lineup[current_batter].at_bat()
    outs = 0
    inning_stats = {}
    for player in starting_lineup:
        inning_stats[player.player_name] =  {"BA":0,"SLG":0,"OBP":0,"OPS":0,"PA":0,"AB":0,"BB":0,"HBP":0,"SO":0,"H":0,"1B":0,"2B":0,"3B":0,"HR":0,"R":0,"RBI":0,"ROE":0,"GDP":0,"SF":0,"SH":0,"BO":0,"GO":0,"LO":0,"FO":0}
    runs_scored = 0
    while(splits_by_type == "Yes"):
        if at_bat == "BB" or at_bat == "HBP" or at_bat == "ROE":
            if bases[0] == 0:
                bases[0] = starting_lineup[current_batter].player_name
            elif (bases[0] != 0) and (bases[1] != 0) and (bases[2] != 0):
                for player in range(len(starting_lineup)):
                    if starting_lineup[player].player_name == bases[2]:
                        inning_stats[starting_lineup[player].player_name]["R"] = inning_stats[starting_lineup[player].player_name]["R"] + 1
                bases[2] = bases[1]
                bases[1] = bases[0]
                bases[0] = starting_lineup[current_batter].player_name
                inning_stats[starting_lineup[current_batter].player_name]["RBI"] = inning_stats[starting_lineup[current_batter].player_name]["RBI"] + 1
            elif (bases[0] != 0) and (bases[1] != 0):
                 bases[2] = bases[1]
                 bases[1] = bases[0]
                 bases[0] = starting_lineup[current_batter].player_name
            elif (bases[0] != 0) and (bases[2] != 0):
                 bases[1] = bases[0]
                 bases[0] = starting_lineup[current_batter].player_name
        elif at_bat == "FO" or at_bat == "GO" or at_bat == "SO" or at_bat == "BO":
            outs = outs + 1
        elif at_bat == "GDP":
            if (bases[0] == 0) and (bases[1] == 0) and (bases[2] == 0):
                outs = outs + 1
                at_bat = "GO"
            elif((bases[0] != 0) and (bases[1] != 0) and (bases[2] != 0)) and outs == 0:
                luck = random.random()
                if luck > 0.75:
                    for player in range(len(starting_lineup)):
                        if starting_lineup[player].player_name == bases[2]:
                            inning_stats[starting_lineup[player].player_name]["R"] = inning_stats[starting_lineup[player].player_name]["R"] + 1
                    inning_stats[starting_lineup[current_batter].player_name]["RBI"] = inning_stats[starting_lineup[current_batter].player_name]["RBI"] + 1
                    bases[2] = bases[1]
                    bases[1] = 0
                    bases[0] = 0
                else:
                    bases[2] = bases[1]
                    bases[1] = bases[0]
                    bases[0] = 0
            elif(((bases[0] == 0) and (bases[1] != 0) and (bases[2] != 0)) or ((bases[0] != 0) and (bases[1] == 0) and (bases[2] != 0)) or ((bases[0] != 0) and (bases[1] != 0) and (bases[2] == 0)) and (outs == 0)):    
                luck = random.random()
                if luck > 0.75:
                    if bases[2] == 0:
                        bases[2] = bases[1]
                    bases[1] = 0
                    bases[0] = 0
                else:
                    if bases[1] == 0:
                        bases[1] = bases[0]
                    bases[2] = 0
                    bases[0] = 0
            else:
                 bases = [0,0,0]
                 outs = outs + 2
        elif at_bat == "HR":
            inning_stats[starting_lineup[current_batter].player_name]["H"] = inning_stats[starting_lineup[current_batter].player_name]["H"] + 1
            for i in range(3):
                if bases[i] != 0:
                    for player in range(len(starting_lineup)):
                        if starting_lineup[player].player_name == bases[i]:
                            inning_stats[starting_lineup[player].player_name]["R"] = inning_stats[starting_lineup[player].player_name]["R"] + 1
                    inning_stats[starting_lineup[current_batter].player_name]["RBI"] = inning_stats[starting_lineup[current_batter].player_name]["RBI"] + 1
                    bases[i] = 0
        elif at_bat == "3B":
            inning_stats[starting_lineup[current_batter].player_name]["H"] = inning_stats[starting_lineup[current_batter].player_name]["H"] + 1
            for i in range(3):
                if bases[i] != 0:
                    for player in range(len(starting_lineup)):
                        if starting_lineup[player].player_name == bases[i]:
                            inning_stats[starting_lineup[player].player_name]["R"] = inning_stats[starting_lineup[player].player_name]["R"] + 1
                    inning_stats[starting_lineup[current_batter].player_name]["RBI"] = inning_stats[starting_lineup[current_batter].player_name]["RBI"] + 1
                    bases[i] = 0
            bases[2] = starting_lineup[current_batter].player_name
        elif at_bat == "2B":
            inning_stats[starting_lineup[current_batter].player_name]["H"] = inning_stats[starting_lineup[current_batter].player_name]["H"] + 1
            luck = random.random()
            if bases[2] != 0:
                for player in range(len(starting_lineup)):
                    if starting_lineup[player].player_name == bases[2]:
                        inning_stats[starting_lineup[player].player_name]["R"] = inning_stats[starting_lineup[player].player_name]["R"] + 1
                inning_stats[starting_lineup[current_batter].player_name]["RBI"] = inning_stats[starting_lineup[current_batter].player_name]["RBI"] + 1
                bases[2] = 0
            if bases[1] != 0:
                for player in range(len(starting_lineup)):
                    if starting_lineup[player].player_name == bases[1]:
                        inning_stats[starting_lineup[player].player_name]["R"] = inning_stats[starting_lineup[player].player_name]["R"] + 1
                inning_stats[starting_lineup[current_batter].player_name]["RBI"] = inning_stats[starting_lineup[current_batter].player_name]["RBI"] + 1
                bases[1] = 0
            if bases[0] != 0:
                if luck>0.25:
                    for player in range(len(starting_lineup)):
                        if starting_lineup[player].player_name == bases[0]:
                            inning_stats[starting_lineup[player].player_name]["R"] = inning_stats[starting_lineup[player].player_name]["R"] + 1
                    inning_stats[starting_lineup[current_batter].player_name]["RBI"] = inning_stats[starting_lineup[current_batter].player_name]["RBI"] + 1
                    bases[0] = 0
                else:
                    bases[2] = bases[0]
                    bases[0] = 0
            bases[1] = starting_lineup[current_batter].player_name
        elif at_bat == "1B":
            inning_stats[starting_lineup[current_batter].player_name]["H"] = inning_stats[starting_lineup[current_batter].player_name]["H"] + 1
            luck = random.random()
            if bases[2] == 1:
                for player in range(len(starting_lineup)):
                    if starting_lineup[player].player_name == bases[2]:
                        inning_stats[starting_lineup[player].player_name]["R"] = inning_stats[starting_lineup[player].player_name]["R"] + 1
                inning_stats[starting_lineup[current_batter].player_name]["RBI"] = inning_stats[starting_lineup[current_batter].player_name]["RBI"] + 1
                bases[2] = 0
            if bases[1] == 1:
                if luck > 0.6:
                    for player in range(len(starting_lineup)):
                        if starting_lineup[player].player_name == bases[1]:
                            inning_stats[starting_lineup[player].player_name]["R"] = inning_stats[starting_lineup[player].player_name]["R"] + 1
                    inning_stats[starting_lineup[current_batter].player_name]["RBI"] = inning_stats[starting_lineup[current_batter].player_name]["RBI"] + 1
                    bases[1] = 0
                else:
                    bases[2] = bases[1]
                    bases[1] = 0
            if bases[0] == 1:
                if luck > 0.99:
                    for player in range(len(starting_lineup)):
                        if starting_lineup[player].player_name == bases[0]:
                            inning_stats[starting_lineup[player].player_name]["R"] = inning_stats[starting_lineup[player].player_name]["R"] + 1
                    inning_stats[starting_lineup[current_batter].player_name]["RBI"] = inning_stats[starting_lineup[current_batter].player_name]["RBI"] + 1
                    bases[0] = 0
                else:
                    bases[1] = bases[0]
            bases[0] = starting_lineup[current_batter].player_name
        elif (at_bat == "SF") or (at_bat == "SH"):
            if (outs < 2) and (bases[2] != 0):
                for player in range(len(starting_lineup)):
                    if starting_lineup[player].player_name == bases[2]:
                        inning_stats[starting_lineup[player].player_name]["R"] = inning_stats[starting_lineup[player].player_name]["R"] + 1
                inning_stats[starting_lineup[current_batter].player_name]["RBI"] = inning_stats[starting_lineup[current_batter].player_name]["RBI"] + 1
                bases[2] = 0
                outs = outs + 1
            else:
                outs = outs + 1
                if at_bat == "SF":
                    at_bat = "FO"
                else:
                    at_bat = "BO"
        #log the result of the at_bat
        inning_stats[starting_lineup[current_batter].player_name][at_bat] = inning_stats[starting_lineup[current_batter].player_name][at_bat] + 1
        inning_stats[starting_lineup[current_batter].player_name]["PA"] = inning_stats[starting_lineup[current_batter].player_name]["PA"] + 1
        if ((at_bat != "BB") and (at_bat != "HBP") and (at_bat != "SH") and (at_bat != "SF")):
            inning_stats[starting_lineup[current_batter].player_name]["AB"] = inning_stats[starting_lineup[current_batter].player_name]["AB"] + 1
        if outs >= 3:
            return inning_stats,current_batter + 1
        current_batter = current_batter + 1
        #turnover the batting order if necessary
        if current_batter > 8:
            current_batter = 0
        at_bat = starting_lineup[current_batter].at_bat()

def main():
    sim_model = batting_model()
    sim_model.setup()
    #########model test full season#############
    #out = full_season_isolated(sim_model)
    #return out
    #########model test from position###########
    #out = hit_run_vals(sim_model)
    #return out
    #########test of simming with lineup########
    names = ["Jerry Potato","Fitz Gerald","Jasper Tarquin","Leo Leopold","Brad Ford","Finnick Ei","Reginald Stewart","Henry Hughe","Barnaby Cosmo"]
    lineup = []
    for i in range(len(names)):
        lineup.append(batting_model(player_name=names[i]))
        lineup[i].setup()
    out = full_season_full_team_batting(lineup)
    return out
    
x = main()
################batting model lineup test###########################
names = ["Jerry Potato","Fitz Gerald","Jasper Tarquin","Leo Leopold","Brad Ford","Finnick Ei","Reginald Stewart","Henry Hughe","Barnaby Cosmo"]
overall_results = {}
split_results = {}
for i in names:
    overall_results[i] = {}
    split_results[i] = []
    for year in range(len(x)):
        overall_results[i][year] = x[year][i]
        
for year in range(len(x)):
    for player in overall_results:
        split_results[player].append(overall_results[player][year]["RBI"])


for player in split_results:
    dataset = split_results[player]
    print(f"{sum(dataset)/len(dataset)} RBIs Per Season for {player}")
    plt.hist(dataset,bins=12,color="skyblue",edgecolor="black",alpha=0.5,label="RBI Distribution")
    plt.xlabel("Runs Scored")
    plt.ylabel("Samples")
    plt.title(f"RBI range for {player}")
    #plt.legend(loc='upper right')
    plt.show()

    


