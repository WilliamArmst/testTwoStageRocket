#!/usr/bin/env python3

import sys
from rocketpy import Environment, SolidMotor, Rocket, Flight, Function
import datetime
# to read a saved environment file:
import numpy as np
import json
import re

def main():
  global printedErrors

  printedErrors = 0

  ################## Environment Setup ##################
  print_blue("Starting environment setup...")
  tomorrow = datetime.date.today() + datetime.timedelta(days=1)
  pathName = f"environment_{tomorrow.month}-{tomorrow.day}-{tomorrow.year}" # ToDo: make this user defined

  try:
    # read environment from file
    #? does rocketpy come with an import function?
    # I hope not... this took way too long to make

    data = json.load(open(pathName + ".json"))
    # structure found at https://github.com/RocketPy-Team/RocketPy/blob/master/rocketpy/environment/environment.py#L2510
    print_blue(f"Reading environment conditions from {pathName}.json...")

    # location and time
    env: Environment = Environment(
      date = data["date"],
      latitude = data["latitude"],
      longitude = data["longitude"],
      elevation = float(data["elevation"]),
      datum = data["datum"],
      timezone = data["timezone"],
      max_expected_height = data["max_expected_height"]
    )

    # meteorological conditions
    pressure_func = Function(np.array([re.split(r' +', x.strip(" []")) for x in data["atmospheric_model_pressure_profile"].split('\n')], dtype = float))
    temperature_func = Function(np.array([re.split(r' +', x.strip(" []")) for x in data["atmospheric_model_temperature_profile"].split('\n')], dtype = float))
    wind_u_func = Function(np.array([re.split(r' +', x.strip(" []")) for x in data["atmospheric_model_wind_velocity_x_profile"].split('\n')], dtype = float))
    wind_v_func = Function(np.array([re.split(r' +', x.strip(" []")) for x in data["atmospheric_model_wind_velocity_y_profile"].split('\n')], dtype = float))

    env.set_atmospheric_model(
      type = "custom_atmosphere",
      pressure = pressure_func,
      temperature = temperature_func,
      wind_u = wind_u_func,
      wind_v = wind_v_func,
    )

  except:
    print_blue(f"Could not find/read an environment file, generating...")
    # find environment
    env = Environment(latitude=39.01549201631338, longitude=-105.71103788653403, elevation=2962) # Hartsel Launch Site

    # set date
    env.set_date(
        (tomorrow.year, tomorrow.month, tomorrow.day, 12)
    )  # Hour given in UTC time
    env.set_atmospheric_model(type="Forecast", file="GFS")

    env.export_environment(filename = pathName)

  print_green("Environment setup complete!\n")
  # env.plots.atmospheric_model()


  ################## Motors ##################
  print_blue("Initializing motors...")

  boostStageMotor = SolidMotor( # Aerotech I59WN
    thrust_source = "AeroTech_I59WN.eng",
    dry_mass = 215 / 1000,
    dry_inertia = (0.125, 0.125, 0.002), # how find
    nozzle_radius= 0 / 1000, # how find
    grain_number = 1, # how find
    grain_density = 1432, # how find
    grain_outer_radius = 38 / 2000, # how find
    grain_initial_inner_radius = 10 / 1000, # how find
    grain_initial_height = 232 / 1000, # how find
    grain_separation = 5 / 1000, # how find
    grains_center_of_mass_position = 11.6 / 100, # how find
    center_of_dry_mass_position = 11.6 / 100, # this is the wet COM
    nozzle_position = 0,
    burn_time = 8.15,
    throat_radius = 0 / 1000, # found from the .rse file on thrustcurve.org?
    coordinate_system_orientation = "nozzle_to_combustion_chamber",
  )
  # boostStageMotor.info()

  sustainerMotor = SolidMotor( # Aerotech J510W-P123
    thrust_source = "AeroTech_J510W.eng",
    dry_mass = 418 / 1000,
    dry_inertia = (0.125, 0.125, 0.002), # how find
    nozzle_radius= 0 / 1000, # how find
    grain_number = 1, # how find
    grain_density = 296, # how find
    grain_outer_radius = 38 / 2000, # how find
    grain_initial_inner_radius = 10 / 1000, # how find
    grain_initial_height = 584 / 1000, # how find
    grain_separation = 5 / 1000, # how find
    grains_center_of_mass_position = 29.2 / 100, # how find
    center_of_dry_mass_position = 29.2 / 100,
    nozzle_position = 0,
    burn_time = 2.15,
    throat_radius = 0 / 1000,
    coordinate_system_orientation = "nozzle_to_combustion_chamber",
  )
  # sustainerMotor.info()

  print_green("Motors initialized!\n")

  
  ################## Rocket(s) ##################
  print_blue("Initializing Rocket(s)...")

  fullRocket = Rocket(
    radius = 5 / 200,
    mass = 1490 / 1000,
    inertia = (6.321, 6.321, 0.034),
    power_off_drag = "../certRocket/rocketpyTest/powerOffDragCurve.csv", # ToDo
    power_on_drag = "../certRocket/rocketpyTest/powerOnDragCurve.csv", # ToDo
    center_of_mass_without_motor = -45.5 / 100,
    coordinate_system_orientation = "tail_to_nose",
  )
  fullRocket.add_motor(boostStageMotor, position = -105 / 100)
  fullRocket.set_rail_buttons(
    upper_button_position = -90/100,
    lower_button_position = -102/100,
    angular_position=45,
  )
  fullRocket.add_nose(
    length = 0.15, kind = "ogive", position = 0
  )
  fullRocket.add_trapezoidal_fins(
      n = 4,
      root_chord = 8 / 100,
      tip_chord = 4 / 100,
      span = 3 / 100,
      sweep_length = 4 / 100,
      position = -65 / 100,
      cant_angle = 0,
  )
  fullRocket.add_trapezoidal_fins(
      n = 4,
      root_chord = 5 / 100,
      tip_chord = 2 / 100,
      span = 3 / 100,
      sweep_angle = 50,
      position = -99 / 100,
      cant_angle = 0,
  )
  # fullRocket.draw()
  # fullRocket.plots.static_margin()

  sustainer = Rocket(
    radius = 5 / 200,
    mass = 321 / 1000,
    inertia = (6.321, 6.321, 0.034), # ToDo
    power_off_drag = "../certRocket/rocketpyTest/powerOffDragCurve.csv", # ToDo
    power_on_drag = "../certRocket/rocketpyTest/powerOnDragCurve.csv", # ToDo
    center_of_mass_without_motor = -32.1 / 100,
    coordinate_system_orientation = "tail_to_nose",
  )
  sustainer.add_motor(sustainerMotor, position = -75/100)
  sustainer.add_nose(
    length=0.15, kind = "ogive", position = 0
  )
  sustainer.add_trapezoidal_fins(
      n = 4,
      root_chord = 8 / 100,
      tip_chord = 4 / 100,
      span = 3 / 100,
      sweep_length = 4 / 100,
      position = -65 / 100,
      cant_angle = 0,
  )
  sustainer.add_parachute(
    name = "main",
    cd_s = 0.162146393311, # pi * d/2 ^2 * 0.8
    trigger = 250,      # ejection altitude in meters
    sampling_rate = 105,
    lag = 1.5,
    noise = (0, 8.3, 0.5),
  )
  sustainer.add_parachute(
      name = "drogue",
      cd_s = 0.0145166713337,
      trigger = "apogee",  # ejection at apogee
      sampling_rate = 105,
      lag = 1.5,
      noise = (0, 8.3, 0.5),
  )
  # sustainer.draw()
  # sustainer.plots.static_margin()

  booster = Rocket(
    radius = 5 / 200,
    mass = 98.6 / 1000,
    inertia = (6.321, 6.321, 0.034), # ToDo
    power_off_drag = "../certRocket/rocketpyTest/powerOffDragCurve.csv", # ToDo
    power_on_drag = "../certRocket/rocketpyTest/powerOnDragCurve.csv", # ToDo
    center_of_mass_without_motor = -15.1 / 100,
    coordinate_system_orientation = "tail_to_nose",
  )
  booster.add_motor(boostStageMotor, position = -30 / 100)
  booster.set_rail_buttons(
    upper_button_position = -17/100, # guesses, probably doesn't match with fullRocket
    lower_button_position = -25/100,
    angular_position=45,
  )
  booster.add_trapezoidal_fins(
    n = 4,
    root_chord = 5 / 100,
    tip_chord = 2 / 100,
    span = 3 / 100,
    sweep_angle = 50,
    position = -24 / 100,
    cant_angle = 0,
  )
  booster.add_parachute(
    name = "main",
    cd_s = 0.0565486677646, # pi * d/2 ^2 * 0.8
    trigger = "apogee",      # ejection altitude in meters
    sampling_rate = 105,
    lag = 1.5,
    noise = (0, 8.3, 0.5),
  )
  # booster.draw()
  # booster.plots.static_margin()

  print_green("Rocket(s) initialized!\n")


  ################## Simulations ##################
  print_blue("Starting simulations...")
  mainFlight = Flight(
    rocket = fullRocket, environment = env, rail_length = 4, inclination = 85, heading = 0
  )
  # mainFlight.altitude.plot()
  mainFlight.prints.apogee_conditions()

  print()

  if printedErrors > 0:
    print_error(f"\nFailed with {printedErrors} errors.")
  else:
    print_green("\nSimulations Completed with 0 errors.")

################## Pretty Colors ##################

# Copyright (c) André Burgaud
# http://www.burgaud.com/bring-colors-to-the-windows-console-with-python/
if sys.platform == "win32":

  from ctypes import windll, Structure, c_short, c_ushort, byref

  SHORT = c_short
  WORD = c_ushort

  class COORD(Structure):
    """struct in wincon.h."""
    _fields_ = [
      ("X", SHORT),
      ("Y", SHORT)]

  class SMALL_RECT(Structure):
    """struct in wincon.h."""
    _fields_ = [
      ("Left", SHORT),
      ("Top", SHORT),
      ("Right", SHORT),
      ("Bottom", SHORT)]

  class CONSOLE_SCREEN_BUFFER_INFO(Structure):
    """struct in wincon.h."""
    _fields_ = [
      ("dwSize", COORD),
      ("dwCursorPosition", COORD),
      ("wAttributes", WORD),
      ("srWindow", SMALL_RECT),
      ("dwMaximumWindowSize", COORD)]

  # winbase.h
  STD_INPUT_HANDLE = -10
  STD_OUTPUT_HANDLE = -11
  STD_ERROR_HANDLE = -12

  # wincon.h
  FOREGROUND_BLACK     = 0x0000
  FOREGROUND_BLUE      = 0x0001
  FOREGROUND_GREEN     = 0x0002
  FOREGROUND_CYAN      = 0x0003
  FOREGROUND_RED       = 0x0004
  FOREGROUND_MAGENTA   = 0x0005
  FOREGROUND_YELLOW    = 0x0006
  FOREGROUND_GREY      = 0x0007
  FOREGROUND_INTENSITY = 0x0008 # foreground color is intensified.

  BACKGROUND_BLACK     = 0x0000
  BACKGROUND_BLUE      = 0x0010
  BACKGROUND_GREEN     = 0x0020
  BACKGROUND_CYAN      = 0x0030
  BACKGROUND_RED       = 0x0040
  BACKGROUND_MAGENTA   = 0x0050
  BACKGROUND_YELLOW    = 0x0060
  BACKGROUND_GREY      = 0x0070
  BACKGROUND_INTENSITY = 0x0080 # background color is intensified.

  stdout_handle = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
  SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute
  GetConsoleScreenBufferInfo = windll.kernel32.GetConsoleScreenBufferInfo

def get_text_attr():
  """Returns the character attributes (colors) of the console screen
  buffer."""
  csbi = CONSOLE_SCREEN_BUFFER_INFO()
  GetConsoleScreenBufferInfo(stdout_handle, byref(csbi))
  return csbi.wAttributes

def set_text_attr(color):
  """Sets the character attributes (colors) of the console screen
  buffer. Color is a combination of foreground and background color,
  foreground and background intensity."""
  SetConsoleTextAttribute(stdout_handle, color)
###############################################################################

def color(color):
  """Set the color. Works on Win32 and normal terminals."""
  if sys.platform == "win32":
    if color == "green":
        set_text_attr(FOREGROUND_GREEN | get_text_attr() & 0x0070 | FOREGROUND_INTENSITY)
    elif color == "yellow":
      set_text_attr(FOREGROUND_YELLOW | get_text_attr() & 0x0070 | FOREGROUND_INTENSITY)
    elif color == "red":
      set_text_attr(FOREGROUND_RED | get_text_attr() & 0x0070 | FOREGROUND_INTENSITY)
    elif color == "blue":
      set_text_attr(FOREGROUND_BLUE | get_text_attr() & 0x0070 | FOREGROUND_INTENSITY)
    elif color == "reset":
      set_text_attr(FOREGROUND_GREY | get_text_attr() & 0x0070)
    elif color == "grey":
      set_text_attr(FOREGROUND_GREY | get_text_attr() & 0x0070)
  else :
    if color == "green":
      sys.stdout.write('\033[92m')
    elif color == "red":
      sys.stdout.write('\033[91m')
    elif color == "blue":
      sys.stdout.write('\033[94m')
    elif color == "reset":
      sys.stdout.write('\033[0m')

def print_error(msg):
  color("red")
  print("ERROR: {}".format(msg))
  color("reset")
  global printedErrors
  printedErrors += 1

def print_green(msg):
  color("green")
  print(msg)
  color("reset")

def print_blue(msg):
  color("blue")
  print(msg)
  color("reset")

def print_yellow(msg):
  color("yellow")
  print(msg)
  color("reset")

if __name__ == "__main__":
  startTime = datetime.datetime.now()
  main()
  print_blue(f"Total Program time elapsed: {datetime.datetime.now() - startTime}")
