'''

{
    "top_primary_attribute": {
        "averages": {
            "avg_attribute_1": avg_1,
            ...
        }
        "primaries": {
            "primary_1": {
                top_primary_value : num_occurrences
                ...
            },
            ...
        }
    },
    ...
}

primary attributes:
key
mode
genre
artist


average attributes:
danceability
energy
loudness
speechiness
acousticness
instrumentalness
liveness
valence
tempo


1. get all tracks for a playlist
2. get all audio features for tracks
3. get all genres for track artists
4. coalesce data

store a separate map for counting primary attribute occurences, sort via ordered dict and use those keys in order to pull from the analysis dict
'''