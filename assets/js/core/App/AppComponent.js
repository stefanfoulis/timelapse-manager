import React from 'react';
import 'normalize.css/normalize.css';
import 'react-mdl/extra/css/material.cyan-red.min.css';
import Footer from '../Footer/FooterComponent';
import styles from './App.scss';

import getMuiTheme from 'material-ui/styles/getMuiTheme';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';

var Countdown = require('react-cntdwn');


export default class App extends React.Component {
  static propTypes = {
    children: React.PropTypes.object.isRequired,
    camera: React.PropTypes.object.isRequired,
  };
  render() {
    return (
      <MuiThemeProvider muiTheme={getMuiTheme()}>
        <div className={styles.root}>
          <div className={styles.greeting} style={{position: 'relative', background: 'url(' + this.props.camera.latestImage.scaledAt640X480Url + ') center / cover' }}>
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
              {this.props.camera.latestImage.shotAt}
            </div>
          </div>
          <div className={styles.content}>
            {this.props.children}
          </div>
          <Footer/>
        </div>
      </MuiThemeProvider>
    );
  }
}
