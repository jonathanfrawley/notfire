#!/usr/bin/env python

import random, os.path

import pygame
from pygame.locals import *

#see if we can load more than standard BMP
if not pygame.image.get_extended():
	raise SystemExit("Sorry, extended image module required")


#Constants
MAX_SHOTS      = 20      #most player bullets onscreen
ALIEN_ODDS     = 22     #chances a new alien appears
BOMB_ODDS      = 60    #chances a new bomb will drop
ALIEN_RELOAD   = 12     #frames between new aliens
SCREENRECT     = Rect(0, 0, 640, 480)
SCORE          = 0

main_dir = os.path.split(os.path.abspath(__file__))[0]

def loadImage(file):
	"loads an image, prepares it for play"
	file = os.path.join(main_dir, '../media', file)
	try:
		surface = pygame.image.load(file)
	except pygame.error:
		raise SystemExit('Could not load image "%s" %s'%(file, pygame.get_error()))
	return surface.convert()

def loadImages(*files):
	imgs = []
	for file in files:
		imgs.append(loadImage(file))
	return imgs

class dummySound:
	def play(self): pass

def loadSound(file):
	if not pygame.mixer: return dummysound()
	file = os.path.join(main_dir, '../media', file)
	try:
		sound = pygame.mixer.Sound(file)
		return sound
	except pygame.error:
		print ('Warning, unable to load, %s' % file)
	return dummysound()

# each type of game object gets an init and an
# update function. the update function is called
# once per frame, and it is when each object should
# change it's current position and state. the Player
# object actually gets a "move" function instead of
# update, since it is passed extra information about
# the keyboard
class Player(pygame.sprite.Sprite):
	speed = 10
	bounce = 24
	gun_offset = 25
	images = []
	fallingSpeed = 4
	jumpSpeed = 4

	jumpTimeAmountDefault = 100
	jumpTimeAmount = 200
	jumpTimeAmountDelta = 21


	def __init__(self):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.reloading = 0
		self.facing = -1
		self.hasGun = True
		self.imageOffset = 0
		if(self.hasGun):
			self.imageOffset = 2
		else:
			self.imageOffset = 0
		self.image = self.images[self.imageOffset]
		self.rect = self.image.get_rect(midbottom=SCREENRECT.midbottom)
		self.origtop = self.rect.top
		self.jumpUpTime = -1
		self.jumpUpTimer = None
		self.jumpDownTimer = None
		self.falling = False
		self.secondLastYPos = self.rect.bottom 
		self.lastYPos = self.rect.bottom

	def isFalling(self):
		if(self.secondLastYPos == self.lastYPos):
			return False
		else:
			return True

	def increaseJumpTime(self):
		self.jumpTimeAmount = self.jumpTimeAmount + self.jumpTimeAmountDelta
	
	def update(self):
		if(not (self.jumpUpTimer == None)):
			#Check timer for fullness
			self.jumpUpTimer.tick()
			self.jumpUpTime = self.jumpUpTime + self.jumpUpTimer.get_time()
			self.rect.move_ip(0, -self.jumpSpeed)
			if(self.jumpUpTime > self.jumpTimeAmount):
				self.jumpUpTimer = None
		else:
			self.rect.move_ip(0, self.fallingSpeed)

		self.secondLastYPos = self.lastYPos
		self.lastYPos = self.rect.bottom

	def jump(self):
		if((self.jumpUpTimer == None) and (not self.isFalling())):
			self.jumpTimeAmount = self.jumpTimeAmountDefault
			self.jumpUpTimer = pygame.time.Clock()
			self.jumpUpTime = 0

	def move(self, directionHorizontal):
		if(self.hasGun):
			self.imageOffset = 2
		else:
			self.imageOffset = 0
		if directionHorizontal: 
			self.facing = directionHorizontal
		'''
		if(not (self.jumpTimer == None)):
			print "self.jumpTimer.get_time()" + str(self.jumpTimer.get_time())

		if((self.jumpTimer == None) and (not self.falling)):
			if(directionVertical != 0):
				self.jumpTimer = pygame.time.Clock()
				self.jumpTime = 0
				self.falling = True
			self.rect.move_ip(directionHorizontal*self.speed, directionVertical*self.speed)
		elif(self.jumpTime >= self.jumpTimeAmount):
#			self.jumpTime = -1
			self.jumpTimer = None
			self.rect.move_ip(directionHorizontal*self.speed, directionVertical*self.speed)
#		elif(self.jumpTime < self.jumpTimeAmount):
		else:
			self.rect.move_ip(directionHorizontal*self.speed, 0)
		'''
		self.rect.move_ip(directionHorizontal*self.speed, 0)

		self.rect = self.rect.clamp(SCREENRECT)

		if directionHorizontal < 0:
			self.image = self.images[self.imageOffset + 0]
		elif directionHorizontal > 0:
			self.image = self.images[self.imageOffset + 1]
#		self.rect.top = self.origtop - (self.rect.left//self.bounce%2)

	def gunpos(self):
		'''
		pos = self.facing*self.gun_offset + self.rect.centerx
		return pos, self.rect.top
		'''
		pos = self.facing*self.gun_offset + self.rect.centerx
#		return pos, self.rect.top
		return pos, (self.rect.centery-6)

	def direction(self):
		return self.facing

	def toggleGun(self):
		self.hasGun = not self.hasGun

class Shot(pygame.sprite.Sprite):
	images = []

	def __init__(self, pos, speed):
		pygame.sprite.Sprite.__init__(self, self.containers)
		if(speed > 0):
			self.image = pygame.transform.flip(self.images[0], 1, 0)
		else:
			self.image = self.images[0]

		self.rect = self.image.get_rect(midbottom=pos)
		self.speed = speed 

	def update(self):
		self.rect.move_ip(self.speed, 0)
		if self.rect.top <= 0:
			self.kill()

class Bomb(pygame.sprite.Sprite):
	speed = 9
	images = []
	def __init__(self, alien):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.image = self.images[0]
		self.rect = self.image.get_rect(midbottom=
				alien.rect.move(0,5).midbottom)

		def update(self):
			self.rect.move_ip(0, self.speed)
		if self.rect.bottom >= 470:
			Explosion(self)
			self.kill()


class Score(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.font = pygame.font.Font(None, 20)
		self.font.set_italic(1)
		self.color = Color('white')
		self.lastscore = -1
		self.update()
		self.rect = self.image.get_rect().move(10, 450)

	def update(self):
		if SCORE != self.lastscore:
			self.lastscore = SCORE
			msg = "Score: %d" % SCORE
			self.image = self.font.render(msg, 0, self.color)


class GameApp:
	def __init__(self):
		self.upPressed = False

	def initialize(self):
		pygame.init()
		if pygame.mixer and not pygame.mixer.get_init():
			print ('Warning, no sound')
			pygame.mixer = None

		winstyle = 0  # |FULLSCREEN
		bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
		self.screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

		img = loadImage('man.gif')
		img2 = loadImage('mangun.gif')
		Player.images = [img, pygame.transform.flip(img, 1, 0), img2, pygame.transform.flip(img2, 1, 0)]

		shotImg = loadImage('shot.gif')
		Shot.images = [shotImg]

		pygame.mouse.set_visible(0)

		#create the background, tile the bgd image
		bgdtile = loadImage('background.gif')
		self.background = pygame.Surface(SCREENRECT.size)
		for x in range(0, SCREENRECT.width, bgdtile.get_width()):
			self.background.blit(bgdtile, (x, 0))
		self.screen.blit(self.background, (0,0))
		pygame.display.flip()
		# Initialize Game Groups
		self.shots = pygame.sprite.Group()
		self.all = pygame.sprite.RenderUpdates()

		#assign default groups to each sprite class
		Player.containers = self.all
		Shot.containers = self.shots, self.all
		self.clock = pygame.time.Clock()

		#Our starting sprites
		self.player = Player()

	def update(self):
		if(not self.player.alive()):
			return False
		else:
			#get input
			for event in pygame.event.get():
				if event.type == QUIT or \
						(event.type == KEYDOWN and event.key == K_ESCAPE):
							return False
			keystate = pygame.key.get_pressed()

			# clear/erase the last drawn sprites
			self.all.clear(self.screen, self.background)

			#update all the sprites
			self.all.update()

			#handle player input
			directionHorizontal = keystate[K_RIGHT] - keystate[K_LEFT]
#			directionVertical = - keystate[K_UP]
			if(keystate[K_UP]):
				if(not self.upPressed):
					self.player.jump();
				self.upPressed = True
				self.player.increaseJumpTime()
			else:
				self.upPressed = False
			self.player.move(directionHorizontal)

			firing = keystate[K_SPACE]
			if not self.player.reloading and firing and len(self.shots) < MAX_SHOTS:
				Shot(self.player.gunpos(), self.player.direction() * 20)
	#            shoot_sound.play()
			self.player.reloading = firing

			#Remove shots that go outside the screen
			shotsCopy = self.shots.sprites()[:]
			for shot in shotsCopy:
				if( not SCREENRECT.contains(shot.rect) ):
					self.shots.remove(shot)
			#cap the framerate
			self.clock.tick(40)
			return True

	def render(self):
		#draw the scene
		dirty = self.all.draw(self.screen)
		pygame.display.update(dirty)


	def shutdown(self):
		'''
		if pygame.mixer:
			pygame.mixer.music.fadeout(1000)
			pygame.time.wait(1000)
		'''
		pygame.quit()

def main(winstyle = 0):
	gameApp = GameApp()
	gameApp.initialize()
	while(gameApp.update()):
		gameApp.render()
	gameApp.shutdown()

if __name__ == '__main__': 
	main()
