# import fatima
from furhat import connect_to_iristk
import pika
# from .. import Player
from threading import Thread
import json
import sys,os,re
import random
import csv
sys.path.append('..')
import Environment
sys.path.append('../..')
from shared import MessageQueue
# etc..


class Agent(object):
    """docstring for Agent."""

    FURHAT_IP = '192.168.0.117'
    FURHAT_AGENT_NAME = 'furhat6'
    RABBITMQ_CONNECTION = {'host': 'localhost', 'port': 32777}
    FURHAT_HOME = '/Users/jdlopes/enterface17/'

    def __init__(self, environment):
        super(Agent, self).__init__()
        self.environment = environment

        # TODO: Move this to separate thread later... but for now listen for wizard events

        self.thread = Thread(target = self.listen_to_wizard_events)
        self.thread.deamon = True
        self.thread.start()

    def listen_to_wizard_events(self):
        mq = MessageQueue('wizard_listener')

        #getting system prompts
        prompts_dict = {}
        spoken_prompt_list = []

        for root,dir,files in os.walk(os.path.join(self.FURHAT_HOME,'NLG/wizard/')):
            for file in files:
                if file.endswith('.prompts'):
                    with open(os.path.join(root,file),'r') as prompt_file:
                        if not file.split('.prompts')[0] in prompts_dict:
                            prompts_dict[file.split('.prompts')[0]] = []
                        for row in csv.reader(prompt_file,delimiter=';'):
                            try:
                                #print(row[1])
                                prompts_dict[file.split('.prompts')[0]].append(row[1])
                            except:
                                print(row)

        def get_prompt(action, prompts_dict, participant=None):

            if participant == 'general' and action != 'accuse':
                selected_prompt = random.choice(prompts_dict['%s.general' % action])
                while selected_prompt in spoken_prompt_list:
                    selected_prompt = random.choice(prompts_dict['%s.general' % action])
            elif participant == 'self':
                selected_prompt = random.choice(prompts_dict['%s.self' % action])
                while selected_prompt in spoken_prompt_list:
                    selected_prompt = random.choice(prompts_dict['%s.self' % action])
            else:
                selected_prompt = re.sub('<user_id>', participant, random.choice(prompts_dict['%s.user' % action]))
                while selected_prompt in spoken_prompt_list:
                    selected_prompt = re.sub('<user_id>', participant, random.choice(prompts_dict['%s.user' % action]))

            try:
                return selected_prompt
            except:
                print('no prompt available')
                return False

        def get_summary():

            selected_prompt = random.choice(prompts_dict['summary'])
            while selected_prompt in spoken_prompt_list:
                selected_prompt = random.choice(prompts_dict['summary'])
            return selected_prompt

        # Callback for wizard events. map to furhat actions
        def callback(_mq, get_shifted_time, routing_key, body):
            action = routing_key.rsplit('.', 1)[1]
            msg = body
            if action == 'say':
                self.say(msg['text'])
            if action == 'accuse':
                if get_prompt(action,prompts_dict,msg['participant']):
                    self.say(get_prompt(action,prompts_dict,msg['participant']))
                    location = self.environment.get_participant(msg['participant']).get_furhat_angle()
                    self.gaze_at(location)
            if action == 'defend':
                if get_prompt(action,prompts_dict,msg['participant']):
                    spoken_prompt_list.append(get_prompt(action,prompts_dict,msg['participant']))
                    self.say(get_prompt(action,prompts_dict,msg['participant']))
                    if random.choice(['last_speaker','defendee']) == 'last_speaker':
                        self.gaze_at({'x':0,'y':0,'z':0})
                    else:
                        location = self.environment.get_participant(msg['participant']).get_furhat_angle()
                        self.gaze_at(location)

            if action == 'support':
                if get_prompt(action,prompts_dict,msg['participant']):
                    spoken_prompt_list.append(get_prompt(action,prompts_dict,msg['participant']))
                    self.say(get_prompt(action,prompts_dict,msg['participant']))
                if msg['participant'] == 'general':
                    self.gaze_at({'x':0,'y':0,'z':0})
                else:
                    location = self.environment.get_participant(msg['participant']).get_furhat_angle()
                    self.gaze_at(location)

            if action == 'vote':
                if get_prompt(action,prompts_dict,msg['participant']):
                    spoken_prompt_list.append(get_prompt(action,prompts_dict,msg['participant']))
                    self.say(get_prompt(action,prompts_dict,msg['participant']))
                    location = self.environment.get_participant(msg['participant']).get_furhat_angle()
                    self.gaze_at(location)

            if action == 'small_talk':
                if get_prompt(action,prompts_dict,msg['participant']):
                    spoken_prompt_list.append(get_prompt(action,prompts_dict,msg['participant']))
                    self.say(get_prompt(action,prompts_dict,msg['participant']))
                    if msg['participant']:
                        location = self.environment.get_participant(msg['participant']).get_furhat_angle()
                        self.gaze_at(location)
                    else:
                        self.gaze_at({'x':0,'y':0,'z':0})

            if action == 'summary':
                self.say(get_summary())
                spoken_prompt_list.append(get_summary())

        mq.bind_queue(
            exchange='wizard', routing_key='action.*', callback=callback
        )

        print('[*] Waiting for messages. To exit press CTRL+C')
        mq.listen()

    def update_belief(self):

        mq = MessageQueue('fatima_agent')

        for player in self.environment.get_participants():
            mq.publish(
                exchange='fatima_agent',
                routing_key='belief_update',
                body={'participant': player.name,
                      'belief': player.properties['belief_is_werewolf']},
                no_time=True
            )

    def get_suggest_action(self):

        mq = MessageQueue('fatima_agent')
        suggested_action = 'accuse pink'
        #suggested_action = get_fatima_action(env)

        mq.publish(
            exchange='fatima_agent',
            routing_key='suggest_action',
            body = {'action':suggested_action}
        )

    def get_vote_suggestion(self):

        mq = MessageQueue('fatima_agent')
        suggested_participant = 'blue'
        #suggested_action = get_fatima_vote(env)

        mq.publish(
            exchange='fatima',
            routing_key='suggest_vote',
            body={'participant' : suggested_participant}
        )

    def say(self, text):
        with connect_to_iristk(self.FURHAT_IP) as furhat_client:
            furhat_client.say(self.FURHAT_AGENT_NAME, text)

    def gaze_at(self, location):
        with connect_to_iristk(self.FURHAT_IP) as furhat_client:
            furhat_client.gaze(self.FURHAT_AGENT_NAME, location)

env = Environment.Environment()
a = Agent(env)
