import React from 'react';
import Relay from 'react-relay';
import ReactDOM from 'react-dom';
import { browserHistory, applyRouterMiddleware, Router } from 'react-router';
import useRelay from 'react-router-relay';

import '../../node_modules/react-mdl/extra/material.js';
import Route from './routes/Route';

const rootNode = document.getElementById('react-app');

import injectTapEventPlugin from 'react-tap-event-plugin';
// Needed for onTouchTap
// http://stackoverflow.com/a/34015469/988941
injectTapEventPlugin();


Relay.injectNetworkLayer(
  new Relay.DefaultNetworkLayer('/graphql', {
    credentials: 'same-origin',
  })
);


ReactDOM.render(
  <Router history={browserHistory} routes={Route} render={applyRouterMiddleware(useRelay)} environment={Relay.Store} />,
  rootNode
);
