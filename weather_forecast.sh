#!/bin/bash
python ~/.config/polybar/weather_class.py forecast | yad --text-info --undecorated --mouse --width 1000 --height 375 --no-buttons  --close-on-unfocus  --fontname="Monoid Semi-Condensed 9" --borders=0 --posy=20
