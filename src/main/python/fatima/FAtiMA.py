import sys
import clr
from collections import Counter

fatima_lib_path = r"fatima"
sys.path.append(fatima_lib_path)
clr.AddReference("IntegratedAuthoringTool")

from System import Array
from IntegratedAuthoringTool import IntegratedAuthoringToolAsset
from IntegratedAuthoringTool import IATConsts
from IntegratedAuthoringTool.DTOs import CharacterSourceDTO
from RolePlayCharacter import RolePlayCharacterAsset
from RolePlayCharacter import EventHelper

# Load the Scenario Configuration
rpc_file = 'scenarios/werewolf_player.rpc'
outputFile = 'scenarios/output.rpc'

# Loading the First Character From the Scenario
rpc = RolePlayCharacterAsset.LoadFromFile(rpc_file)
rpc.LoadAssociatedAssets()

def action_event(a1, a2, a3): 
	evt = EventHelper.ActionEnd(a1, a2, a3)
	rpc.Perceive(evt)
	rpc.SaveToFile(outputFile)
	rpc.Update()

def property_change(a1, a2):
	evt = EventHelper.PropertyChange(a1, a2, 'world')
	rpc.Perceive(evt)
	rpc.SaveToFile(outputFile)
	rpc.Update()

def get_accusals():
	accusals = Counter([str(d.Target) for d in rpc.Decide()])
	if len(accusals) > 0:
		print "Accusals: ", accusals
	else:
		print "No accusals"

def update_knowledge_base(timestep, participants):
	action_event("White", "vote", "Red")
	property_change('GazeMostAt(Blue)', 'Red')
	property_change('GazeMostAt(Red)', 'Blue')
	property_change('IsDead(Blue)', 'false')
	property_change('IsDead(Red)', 'false')
	property_change('IsDead(White)', 'true')
	property_change('ClosedMouth(Blue)', 'true')
	property_change('EyesOpen(Blue)', 'true')

update_knowledge_base(0, {"Blue":{"GazeMostAt":"Red", "MouthOpen":0.25}})
get_accusals()
