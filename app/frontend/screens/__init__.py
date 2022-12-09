from . import StartScreen, GalleryScreen, CalendarScreen
import tkinter as tk


# page that shows when user installs
start_screen = StartScreen.StartPage

gallery_screen = GalleryScreen.GalleryScreen
calendar_screen = CalendarScreen.CalendarScreen


screen_list = list()
screen_list.append(start_screen)
screen_list.append(gallery_screen)
screen_list.append(calendar_screen)
