import requests
from PIL import Image, ImageEnhance, ImageDraw, ImageFont

API_WEATHER = ""
url_and_params_rain = f"https://tile.openweathermap.org/map/precipitation_new/8/129/95?appid={API_WEATHER}"
url_and_params_clouds = f"https://tile.openweathermap.org/map/clouds_new/8/129/95?appid={API_WEATHER}"

response_rain = requests.get(url_and_params_rain, stream=True).raw
response_clouds = requests.get(url_and_params_clouds, stream=True).raw

# Background image
background_src = "/home/hammett/Downloads/Barcelona_map.png"
background_img = Image.open(background_src).convert("RGB")
background_img = ImageEnhance.Color(background_img).enhance(0)
#background_img = ImageEnhance.Brightness(background_img).enhance(0.88)
#background_img = ImageEnhance.Contrast(background_img).enhance(2.5)

# Rain foreground and reduce transparency
foreground_img_rain = Image.open(response_rain)
foreground_img_rain_alpha = foreground_img_rain.copy()
foreground_img_rain_alpha.putalpha(180)
foreground_img_rain.paste(foreground_img_rain_alpha, foreground_img_rain)

# Clouds foreground and reduce transparency
foreground_img_clouds = Image.open(response_clouds)
foreground_img_clouds_alpha = foreground_img_clouds.copy()
foreground_img_clouds_alpha.putalpha(200)
foreground_img_clouds.paste(foreground_img_clouds_alpha, foreground_img_clouds)

# Background copies
background_rain = background_img.copy()
background_clouds = background_img.copy()

# Define font
myFont = ImageFont.truetype("VictorMonoNerdFont-Regular.ttf", 18)

# Merge backgrounds and foregrounds and add text
background_rain.paste(foreground_img_rain, (0, 0), foreground_img_rain)
background_rain_text = ImageDraw.Draw(background_rain)
background_rain_text.text((256/2, 243), "Rain", font=myFont, fill=(0, 0, 0), anchor="mm")

background_clouds.paste(foreground_img_clouds, (0, 0), foreground_img_clouds)
background_clouds_text = ImageDraw.Draw(background_clouds)
background_clouds_text.text((256/2, 243), "Clouds", font=myFont, fill=(0, 0, 0), anchor="mm")

# Combine images side-by-side
background_img = Image.new('RGB', (522, 256), color=(255, 255, 255))
background_img.paste(background_rain, (0, 0))
background_img.paste(background_clouds, (275, 0))

# Save final image
background_img.save("/tmp/precip.png")
