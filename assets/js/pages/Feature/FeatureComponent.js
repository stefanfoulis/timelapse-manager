/* eslint-disable global-require */
import React from 'react';
import { Grid, Cell, Card, CardTitle, CardText, CardActions, Button } from 'react-mdl';
import Page from '../../core/Page/PageComponent';
import styles from './Feature.scss';

export default class Feature extends React.Component {
  static propTypes = {
    viewer: React.PropTypes.object.isRequired
  };

  render() {
    return (
      <Page heading='Images'>
        <Grid>
          {this.props.viewer.images.edges.map(edge => {
            return (
              <Cell col={4} key={edge.node.id}>
                <Card className={styles.card}>
                  <CardTitle expand className={styles.image} style={{ backgroundImage: `url(${edge.node.scaledAt160X120Url})` }} />
                  <CardActions className={styles.name}>
                    <Button colored href={edge.node.originalUrl}>{edge.node.name}</Button>
                  </CardActions>
                  <CardText className={styles.description}>
                    {edge.node.shotAt}
                  </CardText>
                </Card>
              </Cell>
            );
          })}
        </Grid>
      </Page>
    );
  }
}
