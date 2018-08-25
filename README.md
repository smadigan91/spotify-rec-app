# Spoticli

As of now, this is just a runnable app (its not even command-line ready as the name implies lol I'll get there) for generating recommendations and recommended playlists in spotify, as well as fetching some user metadata that wouldn't otherwise be available. Currently it can create playlists given seed tracks and a few different recommendation techniques, generate a new playlist given an existing playlist as a seed, and fetch a user's top tracks/artists over a period of time.

# Relevant Links
https://developer.spotify.com/dashboard/

http://spotipy.readthedocs.io/en/latest/#api-reference


# How to run locally

Register your app with spotify [here](https://developer.spotify.com/dashboard/) to get the client id and secret. Then go to your app settings and set the redirect url to be http://localhost:8080/ (you can change the port if you want). Make sure you set the client id, secret, and your spotify username as environment variables before running the app.

Right now there's a couple different methods for getting recommendations (they produce fairly similar recommendations actually) as well as a method for creating a playlist given recommendations or a similar playlist given an existing playlist. All the action happens in the index() function for now.

Depending on what you want to do, check the spotify web API reference to see if a different scope is required than the one currently hard-coded as 'scope'. Note that multiple scopes can be used at once so long as they are delimited by a space.

To actually run it, pip install the requirements, make sure you have the proper environment variables set, and run spotify_app.py. The app should open up the auth url in your browser automatically, and you just click the "Login to Spotify" link to run the index() function. That's about it really.
