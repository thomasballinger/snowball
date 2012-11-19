import json
import select
import pygame
import pygame.gfxdraw
import socket
import sys
import time

PORT = 1060
CLIENT_PORT = 12345
SCREEN_SIZE = [1200, 500]
RECV_SIZE = 65535
TICK_TIME = .8

pygame_to_protocol = {
    pygame.K_UP : 'UP',
    pygame.K_DOWN : 'DOWN',
    pygame.K_LEFT: 'LEFT',
    pygame.K_RIGHT : 'RIGHT',
    pygame.K_SPACE : 'SPACE',
    }

class Event(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)
    def __repr__(self):
        return object.__repr__(self)[:-1]+' '+', '.join(att+': '+str(getattr(self, att)) for att in vars(self))+'>'

class Listener(object):
    def __init__(self, event_manager):
        self.event_manager = event_manager
        self.event_manager.reg_listener(self)
    def handle_tick(self):
        pass
    def handle_event(self, event):
        pass

class PygameClient(object):
    instance = None
    def __init__(self, address):
        if PygameClient.instance:
            raise Exception('because it uses pygame, you can only instantiate Client once')
        PygameClient.instance = self

        self.port = PORT
        self.server_address = address
        self.is_game_master = False
        self.players = 0
        self.event_manager = EventManager()
        self.game = DumbGameModel(self.event_manager)
        self.network_model = NetworkModel(self.event_manager, self.server_address, self.port)

        pygame.init()
        self.keyboard_controller = PygameKeyboardController(self.event_manager)
        self.view = PygameView(self.event_manager)

    def start(self):
        while True:
            select_start = time.time()
            while True:
                timeout = TICK_TIME - (time.time() - select_start)
                r, w, e = select.select([self.network_model.s], [], [], timeout)
                if r:
                    self.event_manager.post(Event(kind='socket_read', socket=self.network_model.s))
                else:
                    break
            self.event_manager.tick()

class PygameView(Listener):
    def __init__(self, event_manager):
        Listener.__init__(self, event_manager)

        self.window = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption("snowball, the game")

        self.title = pygame.font.Font(None, 100)
        self.msg = pygame.font.Font(None, 40)

class DumbGameModel(Listener):
    pass

def listen_sort_key(x):
    if 'View' in repr(x.__class__): return 1
    if 'Controller' in repr(x.__class__): return -1
    return 0

class EventManager(object):
    """Event dispatcher

    Forwards events to listeners that aren't Controllers.
    Sends ticks to everyone.
    Being a Controller means the string 'Controller' appears in object's class name
    """
    def __init__(self):
        self.listeners = []

    def reg_listener(self, listener):
        """Adds a listener, and keeps maintains order of controllers before views"""
        self.listeners.append(listener)
        self.listeners.sort(key=listen_sort_key)
    def unreg_listener(self, listener):
        self.listeners.remove(listener)
    def tick(self):
        for listener in self.listeners:
            listener.handle_tick()
    def post(self, *events):
        for event in events:
            for listener in self.listeners:
                if not 'Controller' in repr(listener.__class__):
                    listener.handle_event(event)

class NetworkModel(Listener):
    def __init__(self, event_manager, server_address, server_port):
        Listener.__init__(self, event_manager)
        self.server_address = server_address
        self.server_port = server_port
        self.msgs_to_send = []
        self.msgs_to_process = []
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(('', CLIENT_PORT))
        self.s.setblocking(0)

        self.connecting = True
        self.waiting = False
        self.is_master = False

    def handle_tick(self):
        #TODO consider sending messages at in handle_event
        if 'QUIT' in self.msgs_to_send:
            sys.exit()
        if self.msgs_to_send:
            print 'actually sending messages:', self.msgs_to_send
            for msg in self.msgs_to_send:
                s = json.dumps(msg, separators=(',',':'))
                print self, 'sending', s
                self.s.sendto(s, (self.server_address, self.server_port))
            self.msgs_to_send = []

        print 'messages received since last tick:', self.msgs_to_process
        if self.msgs_to_process:
            for msg in self.msgs_to_process:
                print 'processing', msg
                self.connecting = False
                if msg[0] == 'MASTER':
                    self.is_master = True
                    self.waiting = True
                if msg[0] == 'START':
                    self.waiting = False
                    self.connecting = False

    def recv_data(self):
        try:
            data, _ = self.s.recvfrom(RECV_SIZE)
            self.msgs_to_process.append(json.loads(data))
            print self, 'received data'
        except socket.timeout:
            print self, 'tried to read data on our socket but it timed out'

    def handle_event(self, e):
        print self, 'received event:', e
        if e.kind == 'socket_read' and e.socket == self.s:
            self.recv_data()
        elif self.connecting:
            if e.kind == 'space':
                self.msgs_to_send.append('SPACE')
        elif self.waiting and self.is_master:
            if e.kind == 'start':
                self.msgs_to_send.append('SPACE')
        else:
            if e.kind == 'move_request':
                self.msgs_to_send.extend(e.keys)
                print 'keypresses added to buffer:', self.msgs_to_send
            elif e.kind == 'quit':
                self.msgs_to_send.append('QUIT')
                print 'QUIT added to buffer:', self.msgs_to_send
            elif e.kind == 'space' and self.connecting:
                self.msgs_to_send.append('SPACE')

class PygameKeyboardController(Listener):
    def __init__(self, event_manager):
        self.event_manager = event_manager
        self.event_manager.reg_listener(self)
        self.key_state = {}
    def handle_tick(self):
        events = []
        for game_event in pygame.event.get():
            #TODO unhardcode .type == 2
            if game_event.type == pygame.QUIT:
                events.append(Event(kind='quit'))
            if game_event.type == 2:
                keyevents = {
                    pygame.K_ESCAPE : lambda: Event(kind='quit'),
                    pygame.K_SPACE : lambda: Event(kind='space'),
                    pygame.K_s : lambda: Event(kind='start'),
                }
                if game_event.key in keyevents:
                    events.append(keyevents[game_event.key]())

        pressed = pygame.key.get_pressed()
        keys = [pygame_to_protocol[i] for i, x in enumerate(pressed) if x and i in pygame_to_protocol]
        if keys:
            events.append(Event(kind='move_request', keys=keys))
        if events:
            print 'posting', events
        self.event_manager.post(*events)

if __name__ == '__main__':
    c = PygameClient('localhost')
    c.start()
