import Relay from 'react-relay';
import Feature from './FeatureComponent';

export default Relay.createContainer(Feature, {
  fragments: {
    viewer: () => Relay.QL`
      fragment on User {
        images(first: 10) {
          edges {
            node {
              id
              name
              originalUrl
              scaledAt160X120Url
              shotAt
            }
          }
        }
      }`
  }
});
