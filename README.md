# How to run

For now, just register your app with spotify [here](https://developer.spotify.com/dashboard/) and get the client id and secret. Then go to your app settings and set the redirect url to be http://localhost:8080/. Then in the app just replace the client id and secret placeholders with your credentials, run it, go to http://localhost:8080/auth, and click the link to get an access token from spotify and do the recommendation stuff.

Right now it's just printing and enumerating the tracks but I'm going to add playlist creating and stuff too.

Code of interest is mostly defined in the index() function

To actually run it, just pip install the requirements and run spotify_client.py

And yeah, I'll abstract the spotify-related static variables to environment variables at some point soon
