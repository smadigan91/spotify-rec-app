import React, { useState } from 'react';
import './App.css';
import 'typeface-roboto';
import { makeStyles } from '@material-ui/core/styles';
import { Button, TextField, FormControl, InputLabel, Select, MenuItem } from '@material-ui/core';
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';

const theme = createMuiTheme({
  palette: {
    type: 'light',
  },
});

const useStyles = makeStyles(theme => ({
  root: {
    '& > *': {
      margin: theme.spacing(1),
      width: 200,
    },
  },
  formControl: {
    margin: theme.spacing(1),
    minWidth: 120,
  },
  selectEmpty: {
    marginTop: theme.spacing(2),
  },
}));

function App() {
  const classes = useStyles();
  const [selection, setSelection] = useState('');

  function handleSubmit() {
    console.log('submitting with selection: ' + selection);
  }

  return (
    <MuiThemeProvider theme={theme}>
      <div className="App">
        <form className={classes.root} noValidate autoComplete="off">
          <TextField id="songer" label="Songer" /><br />
          <TextField id="doodley" label="Doodley" /><br />
          <FormControl className={classes.formControl}>
            <InputLabel id="demo-simple-select-label">Angers</InputLabel>
            <Select
              labelId="demo-simple-select-label"
              id="demo-simple-select"
              value={selection}
              onChange={event => setSelection(event.target.value)}
            >
              <MenuItem value={1}>Banger</MenuItem>
              <MenuItem value={2}>Flanger</MenuItem>
              <MenuItem value={3}>Sanger</MenuItem>
            </Select>
          </FormControl><br />
          <br />

          <Button variant="contained" color="primary" onClick={handleSubmit}>
            Submit
          </Button>
        </form>

      </div>
    </MuiThemeProvider>
  );
}

export default App;
