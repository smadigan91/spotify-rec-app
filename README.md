# Spotify Recommender App

The initial plan here is to build a basic webapp that wraps Spotify's [recommendations API](https://developer.spotify.com/documentation/web-api/reference/browse/get-recommendations/), allowing anyone to easily tune how they would like their spotify recommendations to be generated, and generating a playlist in their account with the recommendations in it. The plan is to also allow more flexibility with how the recommendations are seeded, for example allowing the user to specify a playlist they want recommendations generated from.

# Relevant Links
https://developer.spotify.com/dashboard/

http://spotipy.readthedocs.io/en/latest/#api-reference


# How to run locally

### Setting up react (post-login page)
1. In src, run `npm install` (generate node_modules) and then `npm run start` so that new changes get updated in the bundle.js for auto-deploy
2. Test out /main and /page2 routes (they nav to each other with buttons)

### Running with docker-compose
As long as you have a decrypted secrets file, you can run the app locally using docker-compose.

If you don't have a decrypted secrets file, you will first need to install [ansible-vault](https://docs.ansible.com/ansible/latest/user_guide/vault.html). Once you've installed it, you will need to ask Sean for the decryption key, and then you can decrypt secrets.yml.enc to the file secrets.yml.dec, which is what the docker-compose environment is expecting.

1. In root directory, run `docker-compose up`
