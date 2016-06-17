import React from 'react';
import 'normalize.css/normalize.css';
import 'react-mdl/extra/css/material.cyan-red.min.css';
import Navbar from '../Navbar/NavbarComponent';
import Footer from '../Footer/FooterContainer';
import styles from './App.scss';
var Countdown = require('react-cntdwn');

var handleFinish = function () {
  console.log('Skynet has become self-aware!');
}


export default class App extends React.Component {
  static propTypes = {
    children: React.PropTypes.object.isRequired,
    viewer: React.PropTypes.object.isRequired
  };

  render() {
    return (
      <div className={styles.root}>
        <Navbar />
        <div className={styles.greeting}>
          <h1 className={styles.sawasdee}>Sawasdee, Sawasdee!</h1>
          <Countdown targetDate={new Date('September 30, 2016')}
           startDelay={1000}
           interval={1000}
           timeSeparator={':'}
           leadingZero
           format={{day: 'DD', hour: 'hh', minute: 'mm', second: 'ss'}}
           onFinished={handleFinish} />
        </div>
        <div className={styles.content}>
          {this.props.children}
        </div>
        <Footer viewer={this.props.viewer} />
      </div>
    );
  }
}
