/* eslint-disable global-require */
import React from 'react';
import Image from '../Image/ImageComponent.js';

export default class Image extends React.Component {
  static propTypes = {
    day: React.PropTypes.object.isRequired
  };

  render() {
    return (
      <img
        src={this.props.image.scaledAt320X240Url}
        srcSet={this.props.image.scaledAt640X480Url + ' 640w, ' + this.props.image.scaledAt320X240Url + ' 320w, ' + this.props.image.scaledAt160X120Url + ' 160w'}
        sizes='50vw'
        style={{width: '100%'}}
      />
    )
  }
}
