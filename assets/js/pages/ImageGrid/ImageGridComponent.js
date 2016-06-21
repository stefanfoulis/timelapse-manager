/* eslint-disable global-require */
import React from 'react';
import { Grid, Cell } from 'react-mdl';
import {Card, CardMedia} from 'material-ui/Card';
import Page from '../../core/Page/PageComponent';
import Image from '../../components/Image/ImageComponent';

export default class Feature extends React.Component {
  static propTypes = {
    camera: React.PropTypes.object.isRequired
  };

  render() {
    return (
      <Page heading='Images'>
        <Grid>
          {this.props.camera.images.edges.map(edge => {
            return (
              <Cell col={4} key={edge.node.id}>
                <Card>
                  <CardMedia>
                    <Image image={edge.node} />
                  </CardMedia>
                </Card>
              </Cell>
            );
          })}
        </Grid>
      </Page>
    );
  }
}
