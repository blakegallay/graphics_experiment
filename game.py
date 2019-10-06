import pygame
import random
from enum import Enum
import math

#import os
#os.environ['SDL_VIDEODRIVER']='windlib'

pygame.init()

width = 500
height = 500

screen = pygame.display.set_mode((width,height))

clock = pygame.time.Clock()

done = False

# Descibes a region on the game screen
# Defined by a boolean function that returns true if
# a pixel i.e. x,y coordinate is in the region.

# Can also return a list of all the pixels inside the region
class region():

	pixels = None

	class Type(Enum):
		RECT = 1
		CIRCLE = 2
		LINE = 3
		
	class rect():
		def __init__(self, args):
			self.bottom_left = args[0]
			self.top_right = args[1]
			
		def contains(self, coord):
			if(coord.x > self.bottom_left.x and coord.x < top_right.x):
				if(coord.y > self.bottom_right.y and coord.y < top_right.y):
					return True
			return False
			
		def draw(self, color, screen):
			pygame.draw.rect(screen, color, pygame.Rect(self.bottom_left.x, self.top_right.y, self.top_right.x - self.bottom_left.x, self.top_right.y - self.bottom_left.y))
		
	class circle():
		def __init__(self, args):
			self.center = args[0]
			self.radius = args[1]
			
		def contains(self, coord):

			if((((coord.x - self.center.x) ** 2) + ((coord.y - self.center.y) ** 2))**(0.5) < self.radius):
				return True
			return False
			
		def draw(self, color, screen):
			pygame.draw.circle(screen, (0, 128, 255), (int(self.center.x), int(self.center.y)), self.radius)
		
	class line():
		def __init__(self, args):
			self.coord1 = args[0]
			self.coord2 = args[1]
			self.thickness = args[2]
			
			self.angle = math.atan((coord2.y - coord1.y) / (coord2.x - coord1.x))
			
			self.length = ((self.coord1.x - self.coord2.x)**2 + (self.coord1.y - self.coord2.y)**2)**0.5
			
			self.region1 = region(region.Type.CIRCLE, self.coord1, self.length)
			self.region2 = region(region.Type.CIRCLE, self.coord2, self.length)
			
		def contains(self, coord):
		
			#transformed_x = coord.x * math.cos(angle) + coord.y * math.sin(angle)
			transformed_y = (coord.y + ( (self.coord1.x * math.tan(self.angle)) - self.coord1.y )) * math.cos(self.angle) - (coord.x) * math.sin(self.angle)
		
			if(abs(transformed_y) < self.thickness):
			
				if(self.region1.contains(coord) and self.region2.contains(coord)):
			
					return True
				
			return False
			
		def draw(self, color, screen):
		
			pygame.draw.line(screen, color, [self.coord1.x, self.coord1.y], [self.coord2.x, self.coord2.y], self.thickness)

	def __init__(self, t, *args):
	
		self.creation_args = args
	
		self.type = t

		self.defining_coords = []
		
		if(self.type == self.Type.RECT):
			self.pixels = self.rect(args)
			self.defining_coords_indices = [0, 1]
			
		elif(self.type == self.Type.CIRCLE):
			self.defining_coords_indices = [0]
			
			self.pixels = self.circle(args)
			
		elif(self.type == self.Type.LINE):
			self.defining_coords_indices = [0, 1]
			self.pixels = self.line(args)
		else:
			print('no type??')
		
	def contains(self, coord):
		return self.pixels.contains(coord)
		
	def move(self, dir, dist):
		new_args = self.creation_args
		
		for index in self.defining_coords_indices:
			new_args[index].x += dist * math.cos(dir)
			new_args[index].y += dist * math.sin(dir)
		
		return region(self.type, *new_args)
		
	def draw(self, color, screen):
		self.pixels.draw(color, screen)

# an object in the gamespace
class object():
	def __init__(self, starting_region, space=None, static=True, solid=False, controllable=False, visible=True, color=(0, 128, 255), gravity=False, weight=1, velocity = [0,0], acceleration=[0,0]):
		self.region = starting_region
		self.static = static
		self.solid = solid 
		self.controllable = controllable
		self.visible = visible
		self.color = color
		self.gravity_enabled = gravity
		self.weight = weight
		self.velocity = velocity
		self.acceleration = velocity
		self.space = space
		
		self.movement_mag = 0
		self.movement_dir = 0
		
	def move(self, dir, dist):
		self.region = self.region.move(dir, dist)
		
	def draw(self, screen):
		if(self.visible):
			self.region.draw(self.color, screen)
			
	def update(self):
	
		# Movement
		if(not self.static):
		
			# Applying gravity
			if(self.gravity_enabled):
				self.velocity[1] += self.weight / 15
			
			# Applying collision
			
			collision = False
			
			if(self.region.type == region.Type.CIRCLE):
			
				for x in range(2 * self.region.pixels.radius):
					x = self.region.pixels.radius - x
					for y in range(2 * self.region.pixels.radius):
						y = self.region.pixels.radius - y
						coord = coordinate(self.region.pixels.center.x + x,self.region.pixels.center.y + y)
						if self.region.contains(coord):
							for obj in self.space.objects:
								if(obj != self):
									if(obj.solid):
										if(obj.region.contains(coord)):
											collision = True
											self.movement_dir = math.atan2( (coord.y - self.region.pixels.center.y), (coord.x - self.region.pixels.center.x) ) + math.pi
											
											self.velocity[0] = 0.8 * self.movement_mag * math.cos(self.movement_dir)
											self.velocity[1] = 0.8 * self.movement_mag * math.sin(self.movement_dir)
											
											break
						if(collision):
							break
					if(collision):
						break
				
			
			
			if(not collision):
				self.movement_dir = math.atan2(self.velocity[1],self.velocity[0])
				
			self.movement_mag = ((self.velocity[0]**2)+(self.velocity[1]**2))**0.5
			
			self.move(self.movement_dir, self.movement_mag)
		
# where objects live
class gameSpace():

	def __init__(self, w, h):
		self.width = w
		self.height = h
		
		self.objects = []

	def add_object(self, obj):
		self.objects.append(obj)
		obj.space = self

# an x,y coordinate in the gamespace
class coordinate():

	def __init__(self, x_coord, y_coord):
		self.x = x_coord
		self.y = y_coord
	
gamespace = gameSpace(width, height)
	
lines_drawn = False
ball_instantiated = False
	
while not done:
		for event in pygame.event.get():
				if event.type == pygame.QUIT:
					done = True 
					
		surfaces = [] # List containing pairs of coordinates that are 
					  # less than 100px away, and have a horizontal 
	
		num_surfaces = 2
		
		if(not lines_drawn):
		
			for n in range(num_surfaces):
				# first coordinate, can be anywhere in the bottom 300px, while
				# not overlapping with a region occupied by another surfaces
				
				space_free = False
				
				while(not space_free):
				
					coord1_x = random.randrange(0, 500)
					coord1_y = random.randrange(0, 500)
					
					coord1 = coordinate(coord1_x, coord1_y)
					
					space_free = True
					
					for obj in gamespace.objects:
						if(obj.solid and obj.region.contains(coord1)):
							space_free = False
							
					valid_region_in = region(region.Type.CIRCLE, coord1, 100)
							
					valid_region_out = region(region.Type.CIRCLE, coord1, 200)
					
				# second coordinate, can be anywhere within 100px of the first
				valid_space = False
				
				while(not valid_space):
					
					coord2_x = random.randrange(0, 500)
					coord2_y = random.randrange(0, 500)
					
					coord2 = coordinate(coord2_x, coord2_y)
					
					valid_space = True
					
					if((valid_region_in.contains(coord2)) or (not valid_region_out.contains(coord2))):
						valid_space = False
						
					for obj in gamespace.objects:
						if(obj.solid and obj.region.contains(coord2)):
							valid_space = False
					
				gamespace.add_object( object(region(region.Type.LINE, coord1, coord2, 5), solid=True) )
				
			coord1 = coordinate(100,100)
			coord2 = coordinate(300,300)
				
			gamespace.add_object( object(region(region.Type.LINE, coord1, coord2, 5), solid=True) )
				
			lines_drawn = True
		
		screen.fill((0,0,0))
		
		if(ball_instantiated):
			ball.update()
		
		if(not ball_instantiated):
			ball = object( region(region.Type.CIRCLE, coordinate(250, 0), 30), static=False,solid=True, gravity=True)
			gamespace.add_object( ball )
			ball_instantiated = True
		
		for obj in gamespace.objects:
			obj.draw(screen)
			
		mouse_pos = coordinate(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])

		for obj in gamespace.objects:
			if(obj.region.contains(mouse_pos)):
			
				obj.color = (255, 128, 0)
				
			else:
				
				obj.color = (0, 128, 255)

		pygame.display.flip()