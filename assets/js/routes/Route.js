import React from 'react';
import { IndexRoute, Route, Redirect } from 'react-router';

import ViewerQuery from './ViewerQuery';
import AppContainer from '../core/App/AppContainer';
import ImageGrid from '../pages/ImageGrid/ImageGridContainer';
import FeatureContainer from '../pages/Feature/FeatureContainer';
import SignupComponent from '../pages/Signup/SignupComponent';
import LoginComponent from '../pages/Login/LoginComponent';

export default (
  <Route path='/' component={AppContainer} queries={ViewerQuery}>
    <IndexRoute component={ImageGrid} queries={ViewerQuery} />
    <Route path='/oldimages' component={FeatureContainer} queries={ViewerQuery} />
    <Route path='/signup' component={SignupComponent} />
    <Route path='/login' component={LoginComponent} />
    <Redirect from='*' to='/' />
  </Route>
);

