__author__ = 'Mark'

# https://www.youtube.com/watch?v=pZD66AVzQRY

import socket
import select
import sys
from random import randint
import json
import sys
# Messages:
#  Client->Server
#   One or two characters. First character is the command:
#     c: connect
#     u: update position
#     d: disconnect
#   Second character only applies to position and specifies direction (udlr)
#
#  Server->Client
#   '|' delimited pairs of positions to draw the players (there is no
#     distinction between the players - not even the client knows where its
#     player is.

class GameServer(object):
    def __init__(self, port=9009, max_num_players=5):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Bind to localhost - set to external ip to connect from other computers
        self.listener.bind(("127.0.0.1", port))
        self.read_list = [self.listener]
        self.write_list = []

        self.stepsize = 5
        self.players = {}
        self.seinad = []
        self.plokid = []
        self.ruudukülg = 45



    def loo_maailm(self):
        for i in range(19):  # Lisan plokid ja seinad listidesse
            for j in range(15):
                if i == 0 or i == 18:
                    self.plokid.append((i*self.ruudukülg, j*self.ruudukülg))
                else:
                    if i % 2 == 0 and j % 2 == 0:
                        self.plokid.append((i*self.ruudukülg, j*self.ruudukülg))
                    elif j == 0 or j == 14:
                        self.plokid.append((i*self.ruudukülg, j*self.ruudukülg))
                    else:
                        if randint(1, 9) < 8 and not ((i == 1 or i == 17) and (j < 4 or j > 10) or (j == 1 or j == 13) and (i < 4 or i > 13)):
                            self.seinad.append((i*self.ruudukülg, j*self.ruudukülg))
        return self.plokid, self.seinad


    """def do_movement(self, mv, player):
        pos = self.players[player]
        print(player)
        if mv == "u":
          pos = (pos[0], max(0, pos[1] - self.stepsize))
        elif mv == "d":
          pos = (pos[0], min(300, pos[1] + self.stepsize))
        elif mv == "l":
          pos = (max(0, pos[0] - self.stepsize), pos[1])
        elif mv == "r":
          pos = (min(400, pos[0] + self.stepsize), pos[1])

        self.players[player] = pos


    def run(self):
        print ("Waiting...")
        try:
            while True:
                readable, writable, exceptional = (
              select.select(self.read_list, self.write_list, [])
            )
            for f in readable:
              if f is self.listener:
                msg, addr = f.recvfrom(32)
                if len(msg) >= 1:
                  cmd = msg[0]
                  if cmd == "c":  # New Connection
                    self.players[addr] = (0,0)
                  elif cmd == "u":  # Movement Update
                    if len(msg) >= 2 and addr in self.players:
                      # Second char of message is direction (udlr)
                      self.do_movement(msg[1], addr)
                  elif cmd == "d":  # Player Quitting
                    if addr in self.players:
                      del self.players[addr]
                  else:
                    print ("Unexpected: {0}".format(msg))
            for player in self.players:
              send = []
              for pos in self.players:
                print self.players[pos]
                print "{0},{1}".format(*self.players[pos])
                send.append("{0},{1}".format(*self.players[pos]))
              self.listener.sendto('|'.join(send), player)
        except KeyboardInterrupt as e:
          pass"""

    def encode(self, data):
        data = json.dumps(data)
        data = data.encode()
        return data

    def decode(self, data):
        data = data.decode()
        data = json.loads(data)
        return data

    def do_movement(self, cmd, player):
        pass

    def lisa_uus_mängija(self, addr):
        if len(self.players) < 1:
            self.players[addr] = ["sinine", ""]
        elif len(self.players) < 2:
            self.players[addr] = ["punane", ""]

    def run(self):

        print("Waiting...")
        self.plokid, self.seinad = self.loo_maailm()
        try:
            while True:
                readable, writable, exceptional = (
              select.select(self.read_list, self.write_list, [])
            )
                for f in readable:
                  if f is self.listener:
                    msg, addr = f.recvfrom(4048)
                    msg = self.decode(msg)
                    if len(msg) >= 1:
                      cmd = msg[0]
                      if cmd == "c":  # New Connection
                        self.lisa_uus_mängija(addr)
                        send = ["w",self.plokid, self.seinad]

                        self.listener.sendto(self.encode(send), addr)


                        for player in self.players:
                            send = []
                            for player in self.players:
                                send.append(self.players[player])
                            self.listener.sendto(self.encode(send), player)

                      elif cmd == "u":
                        if len(msg) >= 2 and addr in self.players:
                            värv = self.players[addr][0]
                            self.players[addr] = [värv, msg[1]]
                        elif len(msg) == 1 and addr in self.players:
                            värv = self.players[addr][0]
                            self.players[addr] = [värv, ""]
                      elif cmd == "d":  # Player Quitting
                        if addr in self.players:
                          del self.players[addr]
                      else:
                        print ("Unexpected: {0}".format(msg))
                for player in self.players:
                    send = []
                    for player in self.players:
                        send.append(self.players[player])
                    print(send)
                    self.listener.sendto(self.encode(send), player)
        except KeyboardInterrupt as e:
          pass


if __name__ == "__main__":
  g = GameServer()
  g.run()
