# Relevant Links
https://developer.spotify.com/dashboard/

http://spotipy.readthedocs.io/en/latest/#api-reference


# How to run locally

Register your app with spotify [here](https://developer.spotify.com/dashboard/) to get the client id and secret. Then go to your app settings and set the redirect url to be http://localhost:8080/ (you can change the port if you want). Make sure you set the client id, secret, and your spotify username as environment variables before running the app.

Right now there's a couple different methods for getting recommendations (they produce fairly similar recommendations actually) as well as a method for creating a playlist given recommendations or a similar playlist given an existing playlist. All the action happens in the index() function for now.

Depending on what you want to do, check the spotify web API reference to see if a different scope is required than the one currently hard-coded as 'playlist_scope'

To actually run it, just pip install the requirements and run spotify_client.py, then go to localhost:8080/auth or whatever you choose to define as your URL for initiating auth and click the link to do oauth and call index()
