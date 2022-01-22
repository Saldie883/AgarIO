BUFSIZE = 2 ** 12
SCREEN_SIZE = [800, 800]
FPS = 200




a = {'a': 34, 'b': 12, 'c': 100, 'd': 32}
a = {k: v for k, v in sorted(a.items(), key=lambda mass: mass[1], reverse=True)}

print(a)


for pos, (nick, mass) in enumerate(a.items()):
	print(pos, nick, mass)