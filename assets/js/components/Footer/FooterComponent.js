import React from 'react';
import { Footer as MDLFooter, FooterSection } from 'react-mdl';
import styles from './Footer.scss';

export default class Footer extends React.Component {
  static propTypes = {
    viewer: React.PropTypes.object.isRequired,
  };

  render() {
    return (
      <MDLFooter className={styles.root} size='mini'>
        <FooterSection type='middle'>
          <span>Handcrafted with ♥, blood and gore. And more. by {this.props.viewer.username}</span>
        </FooterSection>
      </MDLFooter>
    );
  }
}
