import foursquare
import pandas as pd

client_id = ""
client_secret = ""
user_id = ""


client = foursquare.Foursquare(client_id = client_id, client_secret = client_secret, redirect_uri="http://fondu.com/oauth/authorize")

# paste auth_uri into browser and capture the access_code to be used to the variable below
auth_uri = client.oauth.auth_url()
access_code = ""
access_token = client.oauth.get_token(access_code)
client.set_access_token(access_token)

all_checkins = client.users.all_checkins()

checkins = []
while True:
    checkins.append(next(all_checkins))

checkins_df = pd.json_normalize(checkins)
checkins_df = checkins_df.iloc[:,[1,7,10,11,15]]
checkins_df["createdAt"] = pd.to_datetime(checkins_df["createdAt"], unit = "s").dt.date
checkins_df.to_csv("fq_checkins.csv",index = False, header = True, sep = ";", encoding = "UTF-8")
