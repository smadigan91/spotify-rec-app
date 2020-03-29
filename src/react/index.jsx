import React, {useState} from 'react';
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
                <Route path="/main">
                    <Main />
                </Route>
                <Route path="/page2">
                    <Page2 />
                </Route>
            </Switch>
        </div>
    </Router>
    );
}

ReactDOM.render(<App />, document.getElementById('app'));

function Main() {
    const [count, setCount] = useState(0);
    const history = useHistory();
    return (
        <div>
            <div>My Flask React App!{count}</div>
            <button onClick={() => setCount(count + 1)}>count up</button>
            <button onClick={() => history.push("/page2")}>go to other page</button>
        </div>
    );
}

function Page2() {
    const history = useHistory();

    return <button onClick={() => history.push("/main")}>go to main page</button>
}