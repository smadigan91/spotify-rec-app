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
  intVal = parseInt(value)
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
  intVal = parseInt(value)
  if (intVal) {
  	return intVal
  } else {
  	return null
  }
}

function getFloatValue(value) {
  floatVal = parseFloat(value)
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
  seedTracks = getStringValue(document.getElementById("seed-tracks").value)
  if (seedTracks) {
  	seedTracks = seedTracks.split(',')
  }
  seedArtists = getStringValue(document.getElementById("seed-artists").value)
  if (seedArtists) {
  	seedArtists = seedArtists.split(',')
  }
  seedGenres = getStringValue(document.getElementById("seed-genres").value)
  if (seedGenres) {
  	seedGenres = seedGenres.split(',')
  }
  var data = {
  	playlist_name: getStringValue(document.getElementById("playlist-name").value),
  	seed: {
      recommendation_limit: getIntValue(document.getElementById("rec-limit").value),
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