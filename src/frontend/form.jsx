import React, {useState, useEffect} from 'react';
import './form.css';
import ReactDOM from 'react-dom';
import {
    BrowserRouter as Router,
    Switch,
    Route,
    Link,
    useHistory
} from "react-router-dom";

function App() {
    return (
        <Router>
            <div>
                <Switch>
                    <Route path="/form">
                        <Form />
                    </Route>
                </Switch>
            </div>
        </Router>
    );
}

ReactDOM.render(<App />, document.getElementById('app'));

function Form() {
    return (
        <>
            <div id="root">
                <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css"
                      integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO"
                      crossOrigin="anonymous"/>
                <meta name="viewport" content="width=device-width, initial-scale=1"/>
                <meta name="theme-color" content="#000000"/>
                <title>Generate Recommendations</title>
                <div data-tip="The title of the playlist to be generated">
                    <a>Playlist Name:</a><br/>
                    <input className="input" type="text" id="playlist-name" size="50" placeholder="My Recommendation Playlist"/><br/>
                </div>

                <div data-tip="The max recommendations per call. Appliies per track if a playlist is given.">
                    <a>Recommendation Limit:</a><br/>
                    <input className="input" type="number" id="rec-limit" size="5" placeholder="100" min="1" max="100"/><br/>
                </div>

                <div
                    data-tip="A url or uri of a seed playlist. Recommendations will be generated for each track in the seed playlist">
                    <a>Seed Playlist:</a><br/>
                    <input className="input" type="text" id="seed-playlist" size="100"
                           placeholder="https://open.spotify.com/playlist/4gyWY4o5xWaGJZGO1KHuhw?si=xhJZfrLUQvOpRIpOwkfD9Q"/><br/>
                </div>

                <div
                    data-tip="A list of comma separated Spotify track ID's, URL's, or URI's to generate recommendations from">
                    <a>Seed Tracks:</a><br/>
                    <input className="input" type="text" id="seed-tracks" size="100"
                           placeholder="spotify:track:6AioOohg4bQZFA4jIYQQ2r, spotify:track:0pwObEOHolQZSldJ2q1wpyr, ..."/><br/>
                </div>

                <div
                    data-tip="A list of comma separated Spotify artist ID's, URL's, or URI's to generate recommendations from">
                    <a>Seed Artists:</a><br/>
                    <input className="input" type="text" id="seed-artists" size="100"
                           placeholder="spotify:artist:2yEwvVSSSUkcLeSTNyHKh8, spotify:artist:4DFhHyjvGYa9wxdHUjtDkc, ..."/><br/>
                </div>

                <div data-tip="A list of comma separated Spotify seed genres to generate recommendations from">
                    <a href="https://developer.spotify.com/console/get-available-genre-seeds/">Seed Genres:</a><br/>
                    <input className="input" type="text" id="seed-genres" size="100"
                           placeholder="alternative, pop, metal, ..."/><br/>
                </div>


                <h2>
                    Filter Information
                </h2>
                <h5 className="attribute-title">Key:</h5>
                <a className="attribute-description">The key the track is in. Integers map to pitches using standard Pitch
                    Class notation. E.g. 0 = C, 1 = C♯/D♭, 2 = D, and so on.</a>
                <br/>
                <a>target:</a>
                <input className="input" type="number" id="target-key" placeholder="0" min="0" max="11"
                       onChange={(e) => updateRangeInput('target-key-display', e.target.value)}/>
                <input className="input-field" type="text" size="30" id="target-key-display" value=""
                       placeholder="None" disabled/><br/>
                <a>min:</a>
                <input className="input" type="number" id="min-key" placeholder="0" min="0" max="11"
                       onChange={(e) => updateRangeInput('min-key-display', e.target.value)}/>
                <input className="input-field" type="text" size="30" id="min-key-display" value=""
                       placeholder="None" disabled/><br/>
                <a>max:</a>
                <input className="input" type="number" id='max-key' placeholder="0" min="0" max="11"
                       onChange={(e) => updateRangeInput('max-key-display', e.target.value)}/>
                <input className="input-field" type="text" size="30" id="max-key-display" value=""
                       placeholder="None" disabled/><br/>


                <h5 className="attribute-title">Mode:</h5>
                <a className="attribute-description">Mode indicates the modality (major or minor) of a track, the type of
                    scale from which its melodic content is derived. Major is represented by 1 and minor is 0.</a>
                <br/>
                <a>target:</a>
                <select className="input" id="target-mode">
                    <option value="None">None</option>
                    <option value="0">Minor</option>
                    <option value="1">Major</option>
                </select>

                <h5 className="attribute-title">Popularity:</h5>
                <a className="attribute-description">The popularity of the track. The value will be between 0 and 100,
                    with 100 being the most popular. The popularity is calculated by algorithm and is based, in the most
                    part, on the total number of plays the track has had and how recent those plays are.</a>
                <br/>
                <a>target:</a>
                <input className="input" type="range" name="points" min="0" max="100" step="1"
                       onChange={(e) => updateRangeInput('target-popularity', e.target.value)}/>
                <input className="input-field" type="text" size="5" id="target-popularity" value="" min="0" max="0"
                       onChange={(e) => updateRangeInput('target-popularity', e.target.value)}/>
                <a>min:</a>
                <input className="input" type="range" name="points" min="0" max="100" step="1"
                       onChange={(e) => updateRangeInput('min-popularity', e.target.value)}/>
                <input className="input-field" type="text" size="5" id="min-popularity" value="" min="0" max="0"
                       onChange={(e) => updateRangeInput('min-popularity', e.target.value)}/>
                <a>max:</a>
                <input className="input" type="range" name="points" min="0" max="100" step="1"
                       onChange={(e) => updateRangeInput('max-popularity', e.target.value)}/>
                <input className="input-field" type="text" size="5" id="max-popularity" value="" min="0"
                       max="0" onChange={(e) => updateRangeInput('max-popularity', e.target.value)}/>

                <h5 className="attribute-title">Duration:</h5>
                <a className="attribute-description">The duration of the track.</a>
                <br/>
                <a>target:</a>
                <input className="input" type="range" name="points" min="0" max="600000" step="1000"
                       onChange={(e) => updateRangeInput('target-duration', e.target.value)}/>
                <input className="input-field" type="text" size="5" id="target-duration" value="" min="0" max="0"
                       onChange={(e) => updateRangeInput('target-duration', e.target.value)}/>
                <a>min:</a>
                <input className="input" type="range" name="points" min="0" max="600000" step="1000"
                       onChange={(e) => updateRangeInput('min-duration', e.target.value)}/>
                <input className="input-field" type="text" size="5" id="min-duration" value="" min="0" max="0"
                       onChange={(e) => updateRangeInput('min-duration', e.target.value)}/>
                <a>max:</a>
                <input className="input" type="range" name="points" min="0" max="600000" step="1000"
                       onChange={(e) => updateRangeInput('max-duration', e.target.value)}/>
                <input className="input-field" type="text" size="5" id="max-duration" value="" min="0" max="0"
                       onChange={(e) => updateRangeInput('max-duration', e.target.value)}/>

                <h5 className="attribute-title">Tempo:</h5>
                <a className="attribute-description">The overall estimated tempo of a track in beats per minute (BPM). In
                    musical terminology, tempo is the speed or pace of a given piece and derives directly from the average
                    beat duration.</a>
                <br/>
                <a>target:</a>
                <input className="input" type="range" name="points" min="0" max="250" step="5"
                       onChange={(e) => updateRangeInput('target-tempo', e.target.value)}/>
                <input className="input-field" type="text" size="5" id="target-tempo" value="" min="0" max="0"
                       onChange={(e) => updateRangeInput('target-tempo', e.target.value)}/>
                <a>min:</a>
                <input className="input" type="range" name="points" min="0" max="250" step="5"
                       onChange={(e) => updateRangeInput('min-tempo', e.target.value)}/>
                <input className="input-field" type="text" size="5" id="min-tempo" value="" min="0" max="0"
                       onChange={(e) => updateRangeInput('min-tempo', e.target.value)}/>
                <a>max:</a>
                <input className="input" type="range" name="points" min="0" max="250" step="5"
                       onChange={(e) => updateRangeInput('max-tempo', e.target.value)}/>
                <input className="input-field" type="text" size="5" id="max-tempo" value="" min="0" max="0"
                       onChange={(e) => updateRangeInput('max-tempo', e.target.value)}/>


                <h5 className="attribute-title">Danceability:</h5>
                <a className="attribute-description">Describes how suitable a track is for dancing based on a combination of
                    musical elements including tempo, rhythm stability, beat strength, and overall regularity. A value of
                    0.000 is least danceable and 1.000 is most danceable. </a>
                <br/>
                <a>target:</a>
                <input className="input" type="range" name="points" min="0" max="1" step="0.001"
                       onChange={(e) => updateRangeInput('target-danceability', e.target.value)}/>
                <input className="input-field" type="text" size="5" id="target-danceability" value="" min="0" max="0"
                       onChange={(e) => updateRangeInput('target-danceability', e.target.value)}/>
                <a>min:</a>
                <input className="input" type="range" name="points" min="0" max="1" step="0.001"
                       onChange={(e) => updateRangeInput('min-danceability', e.target.value)}/>
                <input className="input-field" type="text" size="5" id="min-danceability" value="" min="0" max="0"
                       onChange={(e) => updateRangeInput('min-danceability', e.target.value)}/>
                <a>max:</a>
                <input className="input" type="range" name="points" min="0" max="1" step="0.001"
                       onChange={(e) => updateRangeInput('max-danceability', e.target.value)}/>
                <input className="input-field" type="text" size="5" id="max-danceability" value="" min="0"
                       max="0" onChange={(e) => updateRangeInput('max-danceability', e.target.value)}/>

                <h5 className="attribute-title">Energy:</h5>
                <a className="attribute-description">A measure from 0.000 to 1.000 and represents a
                    perceptual measure of intensity and activity. Typically, energetic tracks feel fast,
                    loud, and noisy. For example, death metal has high energy, while a Bach prelude scores
                    low on the scale. Perceptual features contributing to this attribute include dynamic
                    range, perceived loudness, timbre, onset rate, and general entropy. </a>
                <br/>
                <a>target:</a>
                <input className="input" type="range" name="points" min="0" max="1" step="0.001"
                       onChange={(e) => updateRangeInput('target-energy', e.target.value)}/>
                <input className="input-field" type="text" size="5" id="target-energy" value="" min="0"
                       max="0" onChange={(e) => updateRangeInput('target-energy', e.target.value)}/>
                <a>min:</a>
                <input className="input" type="range" name="points" min="0" max="1" step="0.001"
                       onChange={(e) => updateRangeInput('min-energy', e.target.value)}/>
                <input className="input-field" type="text" size="5" id="min-energy" value="" min="0"
                       max="0" onChange={(e) => updateRangeInput('min-energy', e.target.value)}/>
                <a>max:</a>
                <input className="input" type="range" name="points" min="0" max="1" step="0.001"
                       onChange={(e) => updateRangeInput('max-energy', e.target.value)}/>
                <input className="input-field" type="text" size="5" id="max-energy" value=""
                       min="0" max="0" onChange={(e) => updateRangeInput('max-energy', e.target.value)}/>


                <h5 className="attribute-title">Valence:</h5>
                <a className="attribute-description">A measure from 0.000 to 1.000 describing the musical positiveness
                    conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric),
                    while tracks with low valence sound more negative (e.g. sad, depressed, angry). </a>
                <br/>
                <a>target:</a>
                <input className="input" type="range" name="points" min="0" max="1" step="0.001"
                       onChange={(e) => updateRangeInput('target-valence', e.target.value)}/>
                <input className="input-field" type="text" size="5" id="target-valence" value="" min="0" max="0"
                       onChange={(e) => updateRangeInput('target-valence', e.target.value)}/>
                <a>min:</a>
                <input className="input" type="range" name="points" min="0" max="1" step="0.001"
                       onChange={(e) => updateRangeInput('min-valence', e.target.value)}/>
                <input className="input-field" type="text" size="5" id="min-valence" value="" min="0" max="0"
                       onChange={(e) => updateRangeInput('min-valence', e.target.value)}/>
                <a>max:</a>
                <input className="input" type="range" name="points" min="0" max="1" step="0.001"
                       onChange={(e) => updateRangeInput('max-valence', e.target.value)}/>
                <input className="input-field" type="text" size="5" id="max-valence" value="" min="0" max="0"
                       onChange={(e) => updateRangeInput('max-valence', e.target.value)}/>

                <h5 className="attribute-title">Acousticness:</h5>
                <a className="attribute-description">A confidence measure from 0.000 to 1.000 of whether the
                    track is acoustic. 1.0 represents high confidence the track is acoustic. </a>
                <br/>
                <a>target:</a>
                <input className="input" type="range" name="points" min="0" max="1" step="0.001"
                       onChange={(e) => updateRangeInput('target-acousticness', e.target.value)}/>
                <input className="input-field" type="text" size="5" id="target-acousticness" value=""
                       min="0" max="0" onChange={(e) => updateRangeInput('target-acousticness', e.target.value)}/>
                <a>min:</a>
                <input className="input" type="range" name="points" min="0" max="1" step="0.001"
                       onChange={(e) => updateRangeInput('min-acousticness', e.target.value)}/>
                <input className="input-field" type="text" size="5" id="min-acousticness" value=""
                       min="0" max="0" onChange={(e) => updateRangeInput('min-acousticness', e.target.value)}/>
                <a>max:</a>
                <input className="input" type="range" name="points" min="0" max="1" step="0.001"
                       onChange={(e) => updateRangeInput('max-acousticness', e.target.value)}/>
                <input className="input-field" type="text" size="5" id="max-acousticness"
                       value="" min="0" max="0"
                       onChange={(e) => updateRangeInput('max-acousticness', e.target.value)}/>


                <h5 className="attribute-title">Speechiness:</h5>
                <a className="attribute-description"> Speechiness detects the presence of spoken words in a track. The more
                    exclusively speech-like the recording (e.g. talk show, audio book, poetry), the closer to 1.0 the
                    attribute value. Values above 0.66 describe tracks that are probably made entirely of spoken words.
                    Values between 0.33 and 0.66 describe tracks that may contain both music and speech, either in sections
                    or layered, including such cases as rap music. Values below 0.33 most likely represent music and other
                    non-speech-like tracks. </a>
                <br/>
                <a>target:</a>
                <input className="input" type="range" name="points" min="0" max="1" step="0.001"
                       onChange={(e) => updateRangeInput('target-speechiness', e.target.value)}/>
                <input className="input-field" type="text" size="5" id="target-speechiness" value="" min="0" max="0"
                       onChange={(e) => updateRangeInput('target-speechiness', e.target.value)}/>
                <a>min:</a>
                <input className="input" type="range" name="points" min="0" max="1" step="0.001"
                       onChange={(e) => updateRangeInput('min-speechiness', e.target.value)}/>
                <input className="input-field" type="text" size="5" id="min-speechiness" value="" min="0" max="0"
                       onChange={(e) => updateRangeInput('min-speechiness', e.target.value)}/>
                <a>max:</a>
                <input className="input" type="range" name="points" min="0" max="1" step="0.001"
                       onChange={(e) => updateRangeInput('max-speechiness', e.target.value)}/>
                <input className="input-field" type="text" size="5" id="max-speechiness" value="" min="0"
                       max="0" onChange={(e) => updateRangeInput('max-speechiness', e.target.value)}/>

                <h5 className="attribute-title">Instrumentalness:</h5>
                <a className="attribute-description">Predicts whether a track contains no vocals. “Ooh” and
                    “aah” sounds are treated as instrumental in this context. Rap or spoken word tracks are
                    clearly “vocal”. The closer the instrumentalness value is to 1.0, the greater likelihood
                    the track contains no vocal content. Values above 0.5 are intended to represent
                    instrumental tracks, but confidence is higher as the value approaches 1.0</a>
                <br/>
                <a>target:</a>
                <input className="input" type="range" name="points" min="0" max="1" step="0.001"
                       onChange={(e) => updateRangeInput('target-instrumentalness', e.target.value)}/>
                <input className="input-field" type="text" size="5" id="target-instrumentalness"
                       value="" min="0" max="0"
                       onChange={(e) => updateRangeInput('target-instrumentalness', e.target.value)}/>
                <a>min:</a>
                <input className="input" type="range" name="points" min="0" max="1" step="0.001"
                       onChange={(e) => updateRangeInput('min-instrumentalness', e.target.value)}/>
                <input className="input-field" type="text" size="5" id="min-instrumentalness"
                       value="" min="0" max="0"
                       onChange={(e) => updateRangeInput('min-instrumentalness', e.target.value)}/>
                <a>max:</a>
                <input className="input" type="range" name="points" min="0" max="1" step="0.001"
                       onChange={(e) => updateRangeInput('max-instrumentalness', e.target.value)}/>
                <input className="input-field" type="text" size="5" id="max-instrumentalness"
                       value="" min="0" max="0"
                       onChange={(e) => updateRangeInput('max-instrumentalness', e.target.value)}/>

                <h5 className="attribute-title">Liveness:</h5>
                <a className="attribute-description"> Detects the presence of an audience in the recording. Higher liveness
                    values represent an increased probability that the track was performed live. A value above 0.8 provides
                    strong likelihood that the track is live.</a>
                <br/>
                <a>target:</a>
                <input className="input" type="range" name="points" min="0" max="1" step="0.001"
                       onChange={(e) => updateRangeInput('target-liveness', e.target.value)}/>
                <input className="input-field" type="text" size="5" id="target-liveness" value="" min="0" max="0"
                       onChange={(e) => updateRangeInput('target-liveness', e.target.value)}/>
                <a>min:</a>
                <input className="input" type="range" name="points" min="0" max="1" step="0.001"
                       onChange={(e) => updateRangeInput('min-liveness', e.target.value)}/>
                <input className="input-field" type="text" size="5" id="min-liveness" value="" min="0" max="0"
                       onChange={(e) => updateRangeInput('min-liveness', e.target.value)}/>
                <a>max:</a>
                <input className="input" type="range" name="points" min="0" max="1" step="0.001"
                       onChange={(e) => updateRangeInput('max-liveness', e.target.value)}/>
                <input className="input-field" type="text" size="5" id="max-liveness" value="" min="0" max="0"
                       onChange={(e) => updateRangeInput('max-liveness', e.target.value)}/>

                <h2>
                    Custom Filters
                </h2>
                <div
                    data-tip="The maximum number of songs per artist you want on the generated playlist. A smaller value means a more diverse but potentially sparse playlist.">
                    <a>Maximum Tracks Per Artist:</a><br/>
                    <input className="input" type="number" id="max-tracks-per-artist" size="5"
                           placeholder="100" min="1" max="100"/><br/>
                </div>
            </div>

            <a href="#" role="button" className="btn btn-primary" onClick={() => generateRecs(window.base_url)}>Generate</a>
        </>
    )
}



var pitchNotationMap = new Map([
    [0, "C/B♯, D double flat"],
    [1, "C♯, D♭, B double sharp"],
    [2, "D, C double sharp, E double flat"],
    [3, "D♯, E♭, F double flat"],
    [4, "E, D double sharp, F♭"],
    [5, "F, E♯, G double flat"],
    [6, "F♯, G♭, E double sharp"],
    [7, "G, F double sharp, A double flat"],
    [8, "G♯, A♭"],
    [9, "A, G double sharp, B double flat"],
    [10, "A♯, B♭, C double flat"],
    [11, "B, A double sharp, C♭"]
])

function clearValue(id) {
    var target = document.getElementById(id)
    if (target.value) {
        target.value = ''
    }
}

function millisToMinutesAndSeconds(millis) {
    var minutes = Math.floor(millis / 60000);
    var seconds = ((millis % 60000) / 1000).toFixed(0);
    return minutes + ":" + (seconds < 10 ? '0' : '') + seconds;
}

function minutesAndSecondsToMillis(minSecs) {
    var timeParts = minSecs.split(':')
    minutes = timeParts[0]
    seconds = timeParts[1]
    return (minutes * 60000) + (seconds * 1000)
}

function updateRangeInput(id, val) {
    var idParts = id.split('-')
    var key = false
    var keyDisplay = pitchNotationMap.get(parseInt(val))
    if (!keyDisplay) {
        keyDisplay = "None"
    }
    if (id.includes('duration')) {
        if (val.includes(":")) {
            val = minutesAndSecondsToMillis(val)
        }
        val = millisToMinutesAndSeconds(val);
    }
    if (id.includes('key')) {
        key = true
    }
    if (id.includes('target')) {
        clearValue('min-'+idParts[1])
        clearValue('max-'+idParts[1])
        document.getElementById(id).value=val;
        if (key) {
            document.getElementById(id).value=keyDisplay;
            clearValue('min-'+idParts[1]+'-display')
            clearValue('max-'+idParts[1]+'-display')
        }
    } else if (id.includes('min')) {
        clearValue('target-'+idParts[1])
        var max = document.getElementById('max-'+idParts[1])
        if (!max.value || parseFloat(max.value) > parseFloat(val)) {
            if (!key) {
                document.getElementById(id).value=val;
            } else {
                clearValue('target-'+idParts[1] +'-display')
                document.getElementById('min-'+idParts[1] +'-display').value=keyDisplay;
            }
        } else {
            max.value = val
            if (!key) {
                document.getElementById(id).value=val;
            } else {
                document.getElementById('min-'+idParts[1] +'-display').value=keyDisplay;
                document.getElementById('max-'+idParts[1]+'-display').value=keyDisplay;
            }
        }
    } else if (id.includes('max')) {
        clearValue('target-'+idParts[1])
        var min = document.getElementById('min-'+idParts[1])
        if (!min.value || parseFloat(min.value) < parseFloat(val)) {
            if (!key) {
                document.getElementById(id).value=val;
            } else {
                clearValue('target-'+idParts[1] +'-display')
                document.getElementById('max-'+idParts[1] +'-display').value=keyDisplay;
            }
        } else {
            min.value = val
            if (!key) {
                document.getElementById(id).value=val;
            } else {
                document.getElementById('max-'+idParts[1]+'-display').value=keyDisplay;
                document.getElementById('min-'+idParts[1]+'-display').value=keyDisplay;
            }
        }
    }
}

function getStringValue(value) {
    if (value) {
        return ""+value
    } else {
        return null
    }
}

function getIntValue(value) {
    const intVal = parseInt(value)
    if (intVal) {
        return intVal
    } else {
        return null
    }
}

function getKeyOrMode(value) {
    if (value == "0") {
        return 0
    }
    const intVal = parseInt(value)
    if (intVal) {
        return intVal
    } else {
        return null
    }
}

function getFloatValue(value) {
    const floatVal = parseFloat(value)
    if (floatVal) {
        return floatVal
    } else {
        return null
    }
}

function getMilliseconds(value) {
    if (value) {
        return minutesAndSecondsToMillis(value)
    } else {
        return null
    }
}

function generateRecs(baseUrl) {
    let seedTracks = getStringValue(document.getElementById("seed-tracks").value)
    if (seedTracks) {
        seedTracks = seedTracks.split(',').map(function(item) {
            return item.trim();
        });
    }
    let seedArtists = getStringValue(document.getElementById("seed-artists").value)
    if (seedArtists) {
        seedArtists = seedArtists.split(',').map(function(item) {
            return item.trim();
        });
    }
    let seedGenres = getStringValue(document.getElementById("seed-genres").value)
    if (seedGenres) {
        seedGenres = seedGenres.split(',').map(function(item) {
            return item.trim();
        });
    }
    var data = {
        playlist_name: getStringValue(document.getElementById("playlist-name").value),
        seed: {
            recommendation_limit: getIntValue(document.getElementById("rec-limit").value),
            playlist: getStringValue(document.getElementById("seed-playlist").value),
            tracks: seedTracks,
            artists: seedArtists,
            genres: seedGenres
        },
        filters: {
            target: {
                track_attributes: {
                    duration_ms: getMilliseconds(document.getElementById("target-duration").value),
                    key: getKeyOrMode(document.getElementById("target-key").value),
                    mode: getKeyOrMode(document.getElementById("target-mode").value),
                    popularity: getIntValue(document.getElementById("target-popularity").value),
                    tempo: getIntValue(document.getElementById("target-tempo").value),
                    danceability: getFloatValue(document.getElementById("target-danceability").value),
                    energy: getFloatValue(document.getElementById("target-energy").value),
                    valence: getFloatValue(document.getElementById("target-valence").value),
                    acousticness: getFloatValue(document.getElementById("target-acousticness").value),
                    speechiness: getFloatValue(document.getElementById("target-speechiness").value),
                    instrumentalness: getFloatValue(document.getElementById("target-instrumentalness").value),
                    liveness: getFloatValue(document.getElementById("target-liveness").value)
                }
            },
            min: {
                track_attributes: {
                    duration_ms: getMilliseconds(document.getElementById("min-duration").value),
                    key: getKeyOrMode(document.getElementById("min-key").value),
                    popularity: getIntValue(document.getElementById("min-popularity").value),
                    tempo: getIntValue(document.getElementById("min-tempo").value),
                    danceability: getFloatValue(document.getElementById("min-danceability").value),
                    energy: getFloatValue(document.getElementById("min-energy").value),
                    valence: getFloatValue(document.getElementById("min-valence").value),
                    acousticness: getFloatValue(document.getElementById("min-acousticness").value),
                    speechiness: getFloatValue(document.getElementById("min-speechiness").value),
                    instrumentalness: getFloatValue(document.getElementById("min-instrumentalness").value),
                    liveness: getFloatValue(document.getElementById("min-liveness").value)
                }
            },
            max: {
                track_attributes: {
                    duration_ms: getMilliseconds(document.getElementById("max-duration").value),
                    key: getKeyOrMode(document.getElementById("max-key").value),
                    popularity: getIntValue(document.getElementById("max-popularity").value),
                    tempo: getIntValue(document.getElementById("max-tempo").value),
                    danceability: getFloatValue(document.getElementById("max-danceability").value),
                    energy: getFloatValue(document.getElementById("max-energy").value),
                    valence: getFloatValue(document.getElementById("max-valence").value),
                    acousticness: getFloatValue(document.getElementById("max-acousticness").value),
                    speechiness: getFloatValue(document.getElementById("max-speechiness").value),
                    instrumentalness: getFloatValue(document.getElementById("max-instrumentalness").value),
                    liveness: getFloatValue(document.getElementById("max-liveness").value)
                }
            },
            custom: {
                max_tracks_per_artist: getIntValue(document.getElementById("max-tracks-per-artist").value)
            }
        }
    }

    var xhr = new XMLHttpRequest()
    xhr.open('POST', baseUrl + '/generate', true)
    xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
    xhr.send(JSON.stringify(data))
    xhr.onreadystatechange = processRequest

    function processRequest(e) {
        if (xhr.readyState == 4 && xhr.status == 200) {
            window.alert('Success!')
        }
        else if (xhr.readyState == 4 && xhr.status == 401) {
            window.alert('Your session has expired!')
        }
        else if (xhr.readyState == 4 && xhr.status == 500) {
            window.alert('Something went wrong')
        }
        else if (xhr.readyState == 4 && xhr.status != 201) {
            window.alert('Something went wrong, status was: ' + xhr.status)
        }
    }
}