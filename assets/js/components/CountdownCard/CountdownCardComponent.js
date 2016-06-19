/* eslint-disable global-require */
import React from 'react';
import Countdown from 'react-cntdwn';
import {Card, CardTitle, CardActions, CardText, Button} from 'react-mdl';
import styles from './CountdownCard.scss';

var handleFinish = function () {
  console.log('Skynet has become self-aware!');
}

export default class CountdownCard extends React.Component {
  static propTypes = {
    title: React.PropTypes.string.isRequired,
    subTitle: React.PropTypes.string.isRequired,
    targetDate: React.PropTypes.instanceOf(Date).isRequired
  };

  render() {
    return (
      <Card shadow={0} style={{width: '512px', margin: 'auto'}} className={styles.countdownCard}>
        <CardText>
          {this.props.title}
          <div style={{fontSize: '42px', lineHeight: '50px', marginTop: '30px'}}>
            <Countdown
              targetDate={this.props.targetDate}
              startDelay={1000}
              interval={1000}
              timeSeparator={':'}
              leadingZero
              format={{day: 'DD', hour: 'hh', minute: 'mm', second: 'ss'}}
              onFinished={handleFinish}
              />
          </div>
        </CardText>
        <CardActions>
          {this.props.subTitle}
        </CardActions>
      </Card>
    )
  }
}
