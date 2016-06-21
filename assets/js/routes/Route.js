import React from 'react';
import { IndexRoute, Route, Redirect } from 'react-router';

import CameraQuery from './CameraQuery';
import AppContainer from '../core/App/AppContainer';
import ImageGrid from '../pages/ImageGrid/ImageGridContainer';
import SignupComponent from '../pages/Signup/SignupComponent';
import LoginComponent from '../pages/Login/LoginComponent';

export default (
  <Route path='/' component={AppContainer} queries={CameraQuery}>
    <IndexRoute component={ImageGrid} queries={CameraQuery} />
    <Route path='/signup' component={SignupComponent} />
    <Route path='/login' component={LoginComponent} />
    <Redirect from='*' to='/' />
  </Route>
);

