import React from 'react';
import 'normalize.css/normalize.css';
import 'react-mdl/extra/css/material.cyan-red.min.css';
import Navbar from '../Navbar/NavbarComponent';
import Footer from '../Footer/FooterContainer';
import styles from './App.scss';

import getMuiTheme from 'material-ui/styles/getMuiTheme';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';


var Countdown = require('react-cntdwn');

import CountdownCard from '../CountdownCard/CountdownCardComponent'

export default class App extends React.Component {
  static propTypes = {
    children: React.PropTypes.object.isRequired,
    viewer: React.PropTypes.object.isRequired,
  };
  render() {
    return (
      <MuiThemeProvider muiTheme={getMuiTheme()}>
        <div className={styles.root}>
          <div className={styles.greeting} style={{position: 'relative', background: 'url(' + this.props.viewer.latestImage.scaledAt640X480Url + ') center / cover' }}>
            <div style={{fontSize: '64px'}}>
              <Countdown
                targetDate={new Date('September 30, 2016')}
                startDelay={1000}
                interval={1000}
                timeSeparator={':'}
                leadingZero
                format={{day: 'DD', hour: 'hh', minute: 'mm', second: 'ss'}}
              />
            </div>
            <div style={{position: 'absolute', bottom: 0, width: '100%'}}>
              {this.props.viewer.latestImage.shotAt}
            </div>
          </div>
          <div className={styles.content}>
            {this.props.children}
          </div>
          <Footer viewer={this.props.viewer} />
        </div>
      </MuiThemeProvider>
    );
  }
}
