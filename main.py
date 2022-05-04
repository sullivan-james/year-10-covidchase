#importing all necessary requirements
import pygame, sys, random
import math
#initialising pygame
pygame.init()



black = (0, 0, 0)
white = (255,255,255)
yellow = (255, 255, 0)
blue = (0,0,255)
pink = (255,182,193)
green = (0,128,0)
light_green = (0,200,0)
red = (255,0,0)
grey = (80,80,80)
dark_grey = (25,25,25)
colour_scheme = [white, black, grey] #light mode scheme (menu background light, text dark, gameplay: road grey)


#Tile/object width and height
obj_width = 80
obj_height = 80


columns = 7 #NEEDS TO BE AN ODD NUMBER

#initializing the background images (the grass for either boundary on the screen)
backgroundImage = pygame.image.load('images/grass_background.jpg')
backgroundImage_width = backgroundImage.get_rect().width #retreiving the width of the picture

#Calculating the size of the screen (taking into account both the widths of the grass background images - also adding the columns by using the columns variable and the width of the tiles)
size = width, height = backgroundImage_width*2 + obj_width*columns, 400

#setting the screen, and the clock (used for framerates)
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

#FUNCTION: To create prediction objects (small red bars predicting the next obstacles)
#IN: The x position of said tile
#OUT: The new prediction tile
def create_prediction(position):
  prediction =  pygame.sprite.Sprite()
  prediction.image = pygame.Surface((obj_width, 5))
  prediction.rect = prediction.image.get_rect()
  prediction.image.fill(red)
  prediction.rect.top = 0
  prediction.rect.left = position #spawning the player in the middle of the screen
  return prediction

#FUNCTION: To create a new obstacle
#IN:  A list of the x values of all the colums (the obstacle NEEDS to spawn in one of these)
#     Height is the screen height
#OUT: A new obstacle sprite
def create_obstacle(tile_list, height):
  obs = pygame.sprite.Sprite()
  #There are 4 sprites to choose from at random
  obs.image = random.choice([pygame.image.load('images/Obstacle1.png'),pygame.image.load('images/Obstacle2.png'),pygame.image.load('images/Obstacle3.png'),pygame.image.load('images/Obstacle4.png')])
  obs.rect = obs.image.get_rect()
  #Spawn it in a random position
  random_position = random.choice(tile_list)
  obs.rect.left = random_position
  #Ensure that it is spawned a little off the screen to give the player time
  obs.rect.bottom = height + 500
  return obs


#FUNCTION: To create a health bar sprite
#IN:  The current health of the player (as an integer between 1 and 100)
#OUT: A new health object    
def healthBar(health):
  #To ensure the health never goes negative (and potentially causes an error)
  if health < 1:
    health = 0


  health_height = 12
  health_obj =  pygame.sprite.Sprite()
  #The sprite is very simply just a red line, with the width being the current health (converted to pixels)
  health_obj.img = pygame.Surface((int(health), int(health_height)))
  health_obj.rect = health_obj.img.get_rect()
  health_obj.img.fill(red)
  #Position the health bar in the box at the bottom right of the screen
  health_obj.rect.left = 20
  health_obj.rect.bottom = height-20

  return health_obj


#FUNCTION: To create a bar to notify the player how long their health will regenerate for
#IN: The current mask value (in between 1 and 25)
#OUT: A mask sprite
def maskBar(mask):
  mask_height = 12
  mask_obj =  pygame.sprite.Sprite()
  mask_obj.img = pygame.Surface((int(mask*4), int(mask_height)))
  mask_obj.rect = mask_obj.img.get_rect()
  mask_obj.img.fill(green)
  #Placing it underneath the player
  mask_obj.rect.left = width - backgroundImage_width - 150 
  mask_obj.rect.bottom = 200

  return mask_obj


#FUNCTION: To create a stamina bar sprite to notify the player how much stamina they have
#IN:  A stamina value
#     The current multiplier
#OUT: A stamina sprite
#     A new stamina width
def create_stamina_bar(stamina_width, multiplier):
  stamina_height = 12
  stamina =  pygame.sprite.Sprite()
  stamina.img = pygame.Surface((int(stamina_width), int(stamina_height)))
  stamina.rect = stamina.img.get_rect()
  stamina.img.fill(blue)
  #Placing it in the bottom left box
  stamina.rect.left = 20
  stamina.rect.bottom = height-70
  #Adding to the stamina width (The higher the multiplier, the faster the stamina bar will fill up)
  stamina_width += multiplier/8
  return stamina, stamina_width


#FUNCTION: Creates the tiles that surround an obstacle to 'mimick' social distancing - this is called whenever the obstacles are moved/created
#OUT: A social distancing tile for each of the four positions; bottom, left, right and top
def create_distancing():
  #initialising all the 'social distancing' tiless
  obs_left,obs_right,obs_front,obs_back = pygame.sprite.Sprite(),pygame.sprite.Sprite(),pygame.sprite.Sprite(),pygame.sprite.Sprite()
  #Setting the images of these tiles
  obs_left.image, obs_right.image, obs_front.image, obs_back.image = pygame.Surface((obj_width,obj_height)),pygame.Surface((obj_width,obj_height)),pygame.Surface((obj_width,obj_height)),pygame.Surface((obj_width,obj_height))
  #Setting the rectangle of these tiles
  obs_left.rect, obs_right.rect, obs_front.rect, obs_back.rect = obs_left.image.get_rect(), obs_right.image.get_rect(), obs_front.image.get_rect(), obs_back.image.get_rect()
  return obs_left,obs_right, obs_front, obs_back


#called every frame to move the obstacles that are coming down the screen
#obs = the current obstacle coming down the screen
#new_obs = the predicted tile
#tile_list = the list of social distancing tiles

#FUNCTION: To move/create obstacles that come down the screen - also call other functions to create social distancing tiles
#IN:  The obstacle being changed
#     A list of columns
#     The current obstacle speed
#OUT: The new obstacle
#     All the social distancing tiles
#     The prediction obstect for the next obstacle coming down the screen
#     Whether the obstacle has reached the bottom of the screen
def move_obstacles(obs, tile_list, obstacle_speed):
  left_tile,right_tile,front_tile,back_tile = create_distancing() #Creating 4 social distancing sprites
  prediction_obj = create_prediction(obs.rect.left) #Create a red bar at the top of the screen, to predict the next obstacle
  bottom_screen = False 
  #only make a new obstacle if the old one has reached the bottom of the screen - an extra 2 times the height of the player is added on the bottom to make for smooth transitions
  if obs.rect.bottom >= height + obj_height*2:
    bottom_screen = True
    obs.rect.bottom = 0-obj_height*5 #resetting the height of the obstacles - adding an extra 5 times the height of the player on top for smooth transition
    obs.image = random.choice([random.choice([pygame.image.load('images/Obstacle1.png'),pygame.image.load('images/Obstacle2.png'),pygame.image.load('images/Obstacle3.png'),pygame.image.load('images/Obstacle4.png')])])
    new_position = None
    position = None

    #Creating a new posiiton for the sprite to come down from
    position = random.choice(tile_list)

    new_position = random.choice(tile_list)

    prediction_obj = create_prediction(new_position)
    obs.rect.left = int(position)
          
  #adding the speed (multiplied by 2.5) to the y position of the obstacle
  obs.rect.bottom += int(obstacle_speed*2.5) #adding the speed to the height of the obstacle

  #offsetting the location of the social distancing tiles (left and right need to get their x value changed and y value the same, and top and bottom need to get theur y value changed and the x value stays the same)
  left_tile.rect.left, right_tile.rect.left, front_tile.rect.left , back_tile.rect.left  = obs.rect.left - obj_width, obs.rect.left + obj_width, obs.rect.left, obs.rect.left

  left_tile.rect.bottom, right_tile.rect.bottom, front_tile.rect.bottom, back_tile.rect.bottom = obs.rect.bottom, obs.rect.bottom, obs.rect.bottom-obj_height, obs.rect.bottom+obj_height

  return obs,left_tile,right_tile,front_tile,back_tile, prediction_obj, bottom_screen

#FUNCTION: creates the powerup sprite whenever the event is called
#IN: A list of all the tiles/columns x values
#OUT: The new power sprite
#     The index of the sprite (0=mask, 1=soap)
def initialise_power(tile_list):
  #initialising the power sprite
  power =  pygame.sprite.Sprite()

  image_list = [pygame.image.load('images/mask.png'), pygame.image.load('images/soap.png')]
  random_choice = random.choice(range(0,len(image_list)))
  random_image = image_list[random_choice]
  power.img = random_image
  power.rect = power.img.get_rect()
  random_position = random.choice(tile_list)
  power.rect.left = random_position
  power.rect.bottom = 0-obj_height*2
  return power, random_choice



#FUNCTION: To check the key presses, and do actions accordingly
#IN:  The player object, power object, power index (i.e. which power is being shown), stamina value, bool to show whether a power is on the screen, the power spawn event which when triggered, shows a new power to the screen, whether shift is pressed, the current obstacle speed, and a list of all the columns
#OUT: Basically everything above but may have been modified
def check_key_presses(player, power_obj,power_indx, stamina, power_on_screen, power_spawn_event, shift_pressed, obstacle_speed, tile_list):
  new_power_indx = None
  x_change = 0 #records the amount that x needs to change
  
  for event in pygame.event.get():
    if event.type == pygame.QUIT: sys.exit() #exit the program

    #If the random timer is complete, and a power object needs to be spawned, call initialise_power()
    if event.type == power_spawn_event:
      power_obj, new_power_indx = initialise_power(tile_list)

      #Record this object has been created in a boolean
      power_on_screen = True

      #creating a new event timer for when the power is supposed to drop down the screen again
      milliseconds_delay = random.randint(5000,10000)
      power_spawn_event = pygame.USEREVENT + 1
      pygame.time.set_timer(power_spawn_event, milliseconds_delay)
    
    #Keeps track of whether shift is being pressed (will influence the characters strafing ability)
    if event.type == pygame.KEYUP:
      if event.key == pygame.K_LSHIFT: shift_pressed = False
      if event.key == pygame.K_RSHIFT: shift_pressed = False
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_LSHIFT: shift_pressed = True
      if event.key == pygame.K_RSHIFT: shift_pressed = True
      
      #IF both an arrow key and shift is pressed, either move the player left OR right three tiles (Also remove 50 stamina)
      if event.key == pygame.K_LEFT and shift_pressed == True: 
        if stamina >= 50:
          x_change = -obj_width*3
          stamina -= 50
      elif event.key == pygame.K_RIGHT and shift_pressed == True: 
        if stamina >= 50:
          x_change = obj_width*3
          stamina -= 50
      
      #If just left or right has been pressed, move the player one tile accordingly
      elif event.key == pygame.K_LEFT: x_change = -obj_width
      elif event.key == pygame.K_RIGHT: x_change = obj_width

  #The new x value of the player
  new_player_left = player.rect.left + x_change
  player.rect.left += x_change

  #Stop the player if they hit grass borders
  if(player.rect.left > width-backgroundImage_width-obj_width):
        player.rect.left = width-backgroundImage_width-obj_width
  elif(player.rect.left < backgroundImage_width):
        player.rect.left = backgroundImage_width


          
  #IF the power is currently on the screen
  if power_on_screen == True:
    if power_indx != None:
      #If the power index (recording which power is on the screen), is not equal to None, then set the new power index (what will be returned later) to the current power index
      new_power_indx = power_indx

    #Move that power down the screen
    power_obj.rect.bottom += int(obstacle_speed)

    #If the power reaches the bottom of the screen, then record this in the boolean variable
    if power_obj.rect.bottom > height + obj_height*2:
      power_on_screen = False

  else:
    new_power_indx = None

  #Cap the stamina variable/bar at 100
  if stamina >100:
    stamina = 100
  
  return player, power_obj, new_power_indx, stamina, power_on_screen, shift_pressed, power_spawn_event





#Function checks for collisions between two objects using the Pygame colliderect function
def is_collided_with(player, obj):
  if player.rect.colliderect(obj.rect):
      return True
  else:
      return False






def update_obstacles(obs_list, health, collided, player, tile_list, obstacle_speed):
  '''This function updates all the obstacles, and their respective social distancing squares (it also resets them to the top once the obstacles reach the bottom of the screen)

  IN:
  #obs_list: A list of all the obstacles currently on the screen (gets overwritten each time on return)
  #health: A value from 1-100 containing the health of the player
  #collided: A boolean recording whether the player has collided with the social distancing squares of an obstacle. This is used to ensure the health is only subtracted once

  OUT:
  #obs_list: a new list of obstacles that have either been reset to the top of the screen, or have been moved down the screen
  #distancing_list: a new list of social distancing tiles that surround the tiles in the obs_list
  #health: an updated value for health (if the player has collided with social distancing). If not, then health just stays the same
  #collided: Records if the player has collided with a social distancing tile. This is recorded so that health isn't subtracted twice'''

  #A list of the left and right "social distancing" square
  distancing_side_list = pygame.sprite.Group()
  #A list of the top and bottom "social distancing" square
  distancing_front_list = pygame.sprite.Group()
  
  prediction_list = pygame.sprite.Group()


  #cycling through each obstacle item currently on the screen
  #the x values of all of the obstacles currently on the screen - is used to ensure there is no overlapping
  current_obstactles_x_values = []
  for item in obs_list:
    #new_obstacle is the new obstacle which is overriding the old one
    new_obstacle, left_tile, right_tile, front_tile, back_tile, prediction_obj, bottom_screen = move_obstacles(item,tile_list, obstacle_speed)
    prediction_list.add(prediction_obj)
    
    current_obstactles_x_values.append(new_obstacle.rect.left)
    obs_list.add(new_obstacle) #adding the new obstacle to the obstacle list

    #adding the new social distancing tiles to respective lists
    #side list is for the left and right tiles
    #front list if for the front and back tiles
    distancing_side_list.add(left_tile)
    distancing_side_list.add(right_tile)
    distancing_front_list.add(front_tile)
    distancing_front_list.add(back_tile)


  distancing_list = pygame.sprite.Group()

  for tile in distancing_side_list:
    #If the player hasnt collided with the distancing sprite
    if collided == False:
      #If the player is currently collided with the distancing sprite
      if is_collided_with(player, tile):
        #Remember this so that there arent any duplicate health losses
        collided = True
        #subtract 15 from the health
        health = health - 15
    
    #If the tile is not overlapping with other obstacles, then add it to a master list of all the social distancing tiles
    if tile.rect.left not in current_obstactles_x_values:
      distancing_list.add(tile)

   

  #Same logic as above. However, seen as these tiles will never collide with other obstacles, there is no reason to check if they have collided 
  for tile in distancing_front_list:
    if collided == False:
      if is_collided_with(player, tile):
        collided = True
        health = health - 15
    distancing_list.add(tile)

  #Once the player reaches the bottom of the screen, set collided to True so that the player can once again lose health
  if bottom_screen == True:
    collided = False

  return obs_list, distancing_list, prediction_list, health, collided

#FUNCTION: To check if the power object has collided with the player - and do what is required according to which power the player has hit
def check_power_collisions(player, power_obj, power_on_screen, power_collided, mask, soap, power_indx,health, fps):
  mask_bar = pygame.sprite.Sprite()
  mask_sprite = pygame.sprite.Sprite()

  if power_on_screen == True:
    if is_collided_with(player, power_obj) == True:
      power_collided = True

      #The power index will be different according to the type of power being shown on the screen
      if power_indx == 0: #Mask - The mask variable is essentially a countdown timer because you get health gradually
        mask = 15
    
      elif power_indx == 1: #soap - The soap vairable ensures the player only gets the 10 health provided once (0 means that the soap has not been hit yet by the player, 1 means the soap has been hit by the player, 2 means the health has been added - soap is always reset back to 0 once it reaches the bottom of the screen)
        if soap == 0:
          soap = 1
    
  else:
    power_collided = False
    soap = 0

  if mask > 2:
    health += 0.1/(30/fps)
    mask -= 0.1/(30/fps)
    
    mask_bar = maskBar(mask)
    mask_sprite = pygame.sprite.Sprite()
    mask_img = pygame.image.load('images/mask.png')
    mask_sprite.img = pygame.transform.scale(mask_img, (40, 40))
    mask_sprite.rect = mask_sprite.img.get_rect()


  if soap == 1:
    health += 10
    soap = 2
  
  #Cap health at 100
  if health > 100:
    health = 100

  return power_collided, mask, mask_bar, mask_sprite, soap, health, mask

#FUNCTION: To blit/print all elements to the screen
def print_screen(screen, fps, tutorial, score, multiplier, boxes, player, obs_list, obstacle_speed,  collided, prediction_list, distancing_list, player_images, walkCount, power_obj, power_collided, power_on_screen, mask, mask_bar, mask_sprite, health, health_obj, width, height, stamina_bar, stamina, multiplier_rbg_value, divider, backgroundImage, backgroundImage_width, grass_and_divider_y_value):
  global colour_scheme

  #resetting the screen
  screen.fill(colour_scheme[2])

   
  #generating the new "y" position of the grass
  grass_and_divider_y_value += obstacle_speed
  new_grass_divider_y=grass_and_divider_y_value%100 #resetting the y position if it gets to the bottom of the screen
  #blitting the grass background images to the screen
  screen.blit(backgroundImage, (0, int(new_grass_divider_y-100)))
  screen.blit(backgroundImage, (int(width-backgroundImage_width), int(new_grass_divider_y-100)))


  divider.fill(colour_scheme[1])
  #printing the white divider lines in the middle of the screen
  for i in range(-100, height, 100):
    screen.blit(divider, (int(width/2), int(i + new_grass_divider_y)))
  
  #Drawing the mask bar & image to the screen if player has run into it
  if mask > 2:
    screen.blit(mask_bar.img, (int(player.rect.left), int(player.rect.bottom+obj_height)))
    screen.blit(mask_sprite.img,(int(player.rect.left-obj_width/2-5), int(player.rect.bottom+65)))

  #If a power item should be shown on the screen (and the player hasn't collided into it)
  if power_collided == False and power_on_screen == True:
    screen.blit(power_obj.img, (power_obj.rect.left, power_obj.rect.bottom))
    


  #Draw the information box outlines
  boxes.draw(screen)

  #Print a value for the health
  health_text_colour = (255,255,255)
  if health >= 100:
    health_text_colour = (255,223,0)
  
  font = pygame.font.Font(None, 36)
  
  #Print the multiplier
  multiplier_text = font.render('X' + str(multiplier), True, (255,multiplier_rbg_value[0],0))
  #Changing the multiplier shade of yellow
  if multiplier_rbg_value[1] == 'UP':
    multiplier_rbg_value[0] += multiplier
    if multiplier_rbg_value[0] >255:
      multiplier_rbg_value[0] = 254
      multiplier_rbg_value[1] = 'DOWN'
  else:
    multiplier_rbg_value[0] -= multiplier
    if multiplier_rbg_value[0] <160:
      multiplier_rbg_value[0] = 161
      multiplier_rbg_value[1] = 'UP'

  text_rect = multiplier_text.get_rect(centerx = int(backgroundImage_width/2), centery = 30)
  screen.blit(multiplier_text, text_rect)

  prediction_list.draw(screen) #Printing the prediction red bars at the top of the screen


 
  #drawing the obstacles to the screen
  for obstacle in obs_list:
    if collided == True:
      obstacle.image.fill(red)
    screen.blit(obstacle.image, (obstacle.rect.left, obstacle.rect.top))

  
  #Drawing and blitting other self explanatory elements to the screen
  health_obj = healthBar(health)
  screen.blit(health_obj.img, (health_obj.rect.left, health_obj.rect.top))
  health_text = font.render(str(round(health)), True, health_text_colour)
  text_rect = health_text.get_rect(centerx = health_obj.rect.left+130, centery = health_obj.rect.bottom - 6)
  screen.blit(health_text, text_rect)

  stamina_colour = white
  if stamina >= 100:
    stamina_colour = yellow
  screen.blit(stamina_bar.img, (stamina_bar.rect.left,stamina_bar.rect.bottom))
  stamina_text = font.render(str(math.floor(stamina/50)), True, stamina_colour)
  text_rect = stamina_text.get_rect(centerx = stamina_bar.rect.left+130, centery = stamina_bar.rect.bottom + 6)
  screen.blit(stamina_text, text_rect)


  score += 1/(30/fps)*multiplier
  score_text = font.render(str(round(score)), True, (255,255,255))
  text_rect = score_text.get_rect(centerx = int(backgroundImage_width/2), centery = 65)
  screen.blit(score_text, text_rect)


  screen.blit(player_images[walkCount//4], (player.rect.left, player.rect.bottom))
  walkCount += 1
  
  #Looping through the player pixel art to make it look like they are running
  if walkCount >= 12: 
    walkCount = 0

  return screen, walkCount, score, grass_and_divider_y_value







def begin_program(screen):
  global colour_scheme
  fps = 30 #WARNING CHANGING FPS FROM 30 IS CURRENTLY UNSTABLE



  global obj_width
  global obj_height
  global columns
  global backgroundImage
  global backgroundImage_width


  numberOfObstacles = round(columns/3)

  obstacle_speed = 1/(fps/30)

  score = 0
 
  tile_list = [] #An array of each column - randomly selected when spawning new objects

  

  #The size of the white stripes that are printed in the middle
  divider_width, divider_height = 5, 40
  divider = pygame.Surface((divider_width, divider_height))
  
  #Initialising other lists, sprites and groups
  prediction_list = pygame.sprite.Group()

  boxes = pygame.sprite.Group()
  btm_lft_box = pygame.sprite.Sprite()
  btm_lft_box.image = pygame.Surface((200, 90))
  btm_lft_box.rect = btm_lft_box.image.get_rect()
  btm_lft_box.image.fill(dark_grey)
  btm_lft_box.image.set_alpha(128)

  btm_lft_box.rect.bottom = height
  btm_lft_box.rect.left = 0 #spawning the player in the middle of the screen

  tp_rt_box = pygame.sprite.Sprite()
  tp_rt_box.image = pygame.Surface((backgroundImage_width, 90))
  tp_rt_box.rect = tp_rt_box.image.get_rect()
  tp_rt_box.image.fill(dark_grey)
  btm_lft_box.image.set_alpha(128)
  tp_rt_box.rect.top = 0
  tp_rt_box.rect.left = 0 #spawning the player in the middle of the screen

  boxes.add(btm_lft_box)
  boxes.add(tp_rt_box)


  playerY = height-obj_height-50 #the y value of where the player will spawn

  player_images = [pygame.image.load('images/player-state1.png'),pygame.image.load('images/player-state2.png'),pygame.image.load('images/player-state3.png')]


  #initialising the player's sprite
  player =  pygame.sprite.Sprite()
  player.img = player_images[0]
  player.rect = player.img.get_rect()
  player.rect.left = int(width/2-obj_width/2) #spawning the player in the middle of the screen
  player.rect.bottom = height-player.rect.height-100


  #creating an event timer for when the power is supposed to drop down the screen
  milliseconds_delay = 8000
  power_spawn_event = pygame.USEREVENT + 1
  pygame.time.set_timer(power_spawn_event, milliseconds_delay)
  
  tutorial_event = pygame.USEREVENT + 1
  pygame.time.set_timer(tutorial_event, 6000)

  #initialising the power sprite
  power =  pygame.sprite.Sprite()
  power.img = pygame.Surface((obj_width, obj_height))
  power.rect = power.img.get_rect()
  power.img.fill(blue)
  power.rect.left = int(width/2-obj_width/2)


  health = 100
  health_height = 12
  health_obj =  pygame.sprite.Sprite()
  health_obj.img = pygame.Surface((health, health_height))
  health_obj.rect = health_obj.img.get_rect()
  health_obj.img.fill(red)
  health_obj.rect.left = 20
  health_obj.rect.bottom = height-20


  status = 0
  stamina = 0

  #list of all the obstacles
  obs_list = pygame.sprite.Group()

  prediction_list = pygame.sprite.Group()


  #Variables to keep track of what is happening on screen (self explanatory)
  grass_and_divider_y_value = 0
  shift_pressed = False
  power_on_screen = False
  power_obj = pygame.sprite.Sprite()
  power_collided = False
  collided = False
  walkCount = 0
  mask = 0
  soap = 0
  power_indx = None
  collided_tile = pygame.sprite.Sprite()
  original_speed = obstacle_speed


  i = backgroundImage_width
  while i < width-backgroundImage_width:
        tile_list.append(i)
        i+=obj_width


  i=0
  while i<numberOfObstacles:
    obs_list.add(create_obstacle(tile_list, height))
    i += 1


  multiplier_rbg_value = [190, 'UP']

  tutorial = 'BEGIN'


  while True:

    #The multiplier that is shown on screen is calculated by comparing the current speed to the original speed
    multiplier = math.ceil(obstacle_speed/original_speed)
    if multiplier < 14: #As long as the multiplier is less than 12 (the highest), then slightly increase obstacle speed
      obstacle_speed += 0.02/multiplier/(fps/30) #divided by multiplier because otherwise the speed would increase too quickly. This slows it down as you get better

    
    #checking all the key presses
    player, power_obj, power_indx, stamina, power_on_screen, shift_pressed, power_spawn_event = check_key_presses(player, power_obj, power_indx, stamina, power_on_screen, power_spawn_event, shift_pressed, obstacle_speed, tile_list)
    
    
    #Creating a new stamina bar, and updating the stamina value (done in the function)
    stamina_bar, stamina = create_stamina_bar(stamina, multiplier)
    

    obs_list, distancing_list, prediction_list, health, collided = update_obstacles(obs_list, health, collided, player, tile_list, obstacle_speed)
  

    power_collided, mask, mask_bar, mask_sprite, soap, health, mask = check_power_collisions(player, power_obj, power_on_screen,power_collided, mask, soap, power_indx,health, fps)

    
    screen, walkCount, score, grass_and_divider_y_value = print_screen(screen, fps, 'MOVE_LEFT', score, multiplier, boxes, player, obs_list, obstacle_speed, collided, prediction_list, distancing_list, player_images, walkCount, power_obj, power_collided, power_on_screen, mask, mask_bar, mask_sprite, health, health_obj, width, height, stamina_bar, stamina, multiplier_rbg_value, divider, backgroundImage, backgroundImage_width, grass_and_divider_y_value)

    if health < 1:
      game_complete(screen, score)
    
    clock.tick(fps) #esuring the game is capped at 60fps
    pygame.display.flip() #push everything to the screen
      


#This function can create a button given some paramaters below
def button(txt, x, y, w, h, type):
  global colour_scheme
  
  #Current mouse and click location
  mouse = pygame.mouse.get_pos()
  click = pygame.mouse.get_pressed()

  #If the mouse if hovering over the given coordinates, then draw a button to the screen made from a lighter colour (to indicate hovering)
  if x+w > mouse[0] > x and y+h > mouse[1]>y:
    pygame.draw.rect(screen, light_green, (int(x), int(y), int(w), int(h)))
    
    #The following if statements check if the player has clicked on any of the buttons, and sending them to the function provided in the "type" variable
    if click[0] == 1 and type == 'START':
      begin_program(screen)
    elif click[0] == 1 and type == 'MENU':
      start_screen()
    elif click[0] == 1 and type == 'QUIT':
      pygame.quit()
      quit()
    elif click[0] == 1 and type == 'DARK_MODE':
      colour_scheme = [black, white, black]
      start_screen()
    elif click[0] == 1 and type == 'LIGHT_MODE':
      colour_scheme = [white, black, grey]
      start_screen()
    elif click[0] == 1 and type == 'INSTRUCTIONS':
      instructions(screen)

  else: #Draw a button to the screen wiht a darker colour
    pygame.draw.rect(screen, green, (int(x), int(y), int(w), int(h)))
  
  smallFont = pygame.font.Font(None, 26)
  restart_button_text = smallFont.render(txt, True, colour_scheme[1])
  restart_button_text_rect = restart_button_text.get_rect(centerx = int(x+w/2), centery = int(y+h/2))
  screen.blit(restart_button_text, restart_button_text_rect)



def instructions(screen):
  global colour_scheme
  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        quit()
    
    screen.fill(colour_scheme[0])


    #Creating text for the instructions (the title used largeFont, and the body text uses font)
    font_size = 23
    font = pygame.font.Font(None, font_size)
    largeFont = pygame.font.Font(None, 36)
    title = largeFont.render('Instructions for COVID-Chase', True, colour_scheme[1])
    text1 = font.render('1. The aim of the game is to last as long as possible by avoiding all people coming down the screen,', True, colour_scheme[1])
    text1_2 = font.render('and pickup power-ups such as soap and masks. The game ends once your health gets to 0.', True, colour_scheme[1])
    text2 = font.render('2. If you enter the "social distancing" area of a person coming down the screen,' , True, colour_scheme[1])
    text2_2 = font.render('your health will decrease, and you will eventually you lose.' , True, colour_scheme[1])
    text3 = font.render('3. Move left and right using the arrow keys on your keyboard. You can also hold shift with an ', True, colour_scheme[1])
    text3_2 = font.render('arrow key to strafe to the left or right. The amount of strafes you can do is indicated ', True, colour_scheme[1])
    text3_3 = font.render('by the blue stamina bar at the bottom left of the screen', True, colour_scheme[1])
    text4 = font.render('4. The top left of the screen shows your score and multiplier (how fast you are going compared ', True, colour_scheme[1])
    text4_2 = font.render('to the starting speed. The multiplier will gradually increase until it hits X14). ', True, colour_scheme[1])
    text4_3 = font.render('Go back to the main menu and press "Start" to begin!', True, colour_scheme[1])




    #Position the title on the top middle
    title_rect = title.get_rect(centerx = int(width/2), centery = 15)
    

    starting_text_loaction = 60 #The position of the body text items are ALL relative to starting_text_location
    text1_rect = text1.get_rect(centerx = int(width/2), centery = int(starting_text_loaction))
    text1_2_rect = text1_2.get_rect(centerx = int(width/2), centery = int(starting_text_loaction+font_size))
    text2_rect = text2.get_rect(centerx = int(width/2), centery = int(starting_text_loaction+50+font_size))
    text2_2_rect = text2_2.get_rect(centerx = int(width/2), centery = int(starting_text_loaction+50+font_size*2))
    text3_rect = text3.get_rect(centerx = int(width/2), centery = int(starting_text_loaction+100+font_size*2))
    text3_2_rect = text3.get_rect(centerx = int(width/2), centery = int(starting_text_loaction+100+font_size*3))
    text3_3_rect = text3.get_rect(centerx = int(width/2), centery = int(starting_text_loaction+100+font_size*4))
    text4_rect = text4.get_rect(centerx = int(width/2), centery = int(starting_text_loaction+150+font_size*4))
    text4_2_rect = text4.get_rect(centerx = int(width/2), centery = int(starting_text_loaction+150+font_size*5))
    text4_3_rect = text4.get_rect(centerx = int(width/2), centery = int(starting_text_loaction+150+font_size*6))

    screen.blit(title, title_rect)
    screen.blit(text1, text1_rect)
    screen.blit(text1_2, text1_2_rect)
    screen.blit(text2, text2_rect)
    screen.blit(text2_2, text2_2_rect)
    screen.blit(text3, text3_rect)
    screen.blit(text3_2, text3_2_rect)
    screen.blit(text3_3, text3_3_rect)
    screen.blit(text4, text4_rect)
    screen.blit(text4_2, text4_2_rect)
    screen.blit(text4_3, text4_3_rect)


    #Creating buttons using the button function I have made
    #button(button_message, x_value, y_value, width, height, code used for calling other functions)
    button('Main Menu',25,15,100,30, 'MENU')
    button('Quit',width-25-100,15,100,30, 'QUIT')
    

    pygame.display.update()


#Screen is shown when the game ends
def game_complete(screen, score):
  global colour_scheme
  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        quit()
    
    screen.fill(colour_scheme[0])

    #Showing some information such as the score through text at the top of the screen
    font = pygame.font.Font(None, 36)
    end_text = font.render('You infected too many people by not social distancing!', True, colour_scheme[1])
    score_text = font.render('Your score is: ' + str(round(score)), True, colour_scheme[1])
    end_text_rect = end_text.get_rect(centerx = int(width/2), centery = 50)
    score_text_rect = score_text.get_rect(centerx = int(width/2), centery = 100)
    screen.blit(end_text, end_text_rect)
    screen.blit(score_text, score_text_rect)

    #Creating buttons using the button function I have made
    #button(button_message, x_value, y_value, width, height, code used for calling other functions)
    button('Restart',width/2-50,150,120,70, 'START')
    button('Main Menu',width/2-50,230,120,70, 'MENU')
    button('Quit',width/2-50,310,120,70, 'QUIT')
    
    pygame.display.update()



#Function called to load the start screen
def start_screen():
  global colour_scheme
  
  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        quit()

    #Begin printing items on the screen  
    screen.fill(colour_scheme[0])

    #Creating welcome text
    font = pygame.font.Font(None, 36)
    welcome_text = font.render('Welcome to COVID-Chase!', True, colour_scheme[1])
    text_rect = welcome_text.get_rect(centerx = int(width/2), centery = 80)
    screen.blit(welcome_text, text_rect)
    
    #Creating buttons using the button function I have made
    #button(button_message, x_value, y_value, width, height, code used for calling other functions)
    button('Start!',width/2-60,150,120,60, 'START')
    button('Quit',width/2-60,300,120,60, 'QUIT')
    button('Dark Mode',20,height-80,200,60, 'DARK_MODE')
    button('Light Mode',20,height-150,200,60, 'LIGHT_MODE')
    button('Instructions',width/2-60,220,120,70, 'INSTRUCTIONS')
    
    pygame.display.update()

#The start screen is the first screen to be called when the program is opened
while True:
  start_screen()

