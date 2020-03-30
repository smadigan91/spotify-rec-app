
var pitchNotationMap = new Map([
  [0, "C/B♯, D double flat"],
  [1, "C♯, D♭, also B double sharp"],
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
  var display = pitchNotationMap.get(parseInt(val))
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
    	document.getElementById(id).value=display;
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
          document.getElementById('min-'+idParts[1] +'-display').value=display;
        }
    } else {
      max.value = val
    	if (!key) {
      	document.getElementById(id).value=val;
      } else {
        document.getElementById('min-'+idParts[1] +'-display').value=display;
        document.getElementById('max-'+idParts[1]+'-display').value=display;
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
        document.getElementById('max-'+idParts[1] +'-display').value=display;
      }
    } else {
      min.value = val
    	if (!key) {
      	document.getElementById(id).value=val;
      } else {
        document.getElementById('max-'+idParts[1]+'-display').value=display;
        document.getElementById('min-'+idParts[1]+'-display').value=display;
      }
    }
  }
}


function getKey(id, val){
  updateRangeInput(id, val)
}