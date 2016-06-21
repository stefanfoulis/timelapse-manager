import React from 'react';
import { Link } from 'react-router';
import { Layout, Header, Navigation, Drawer } from 'react-mdl';
import styles from './Navbar.scss';

export default class Navbar extends React.Component {
  render() {
    const title = 'Weiherstrasse';
    return (
      <Layout className={styles.root}>
        <Header title={<Link to='/'>{title}</Link>} scroll>
        </Header>
      </Layout>
    );
  }
}
