import Relay from 'react-relay';
import ImageGrid from './ImageGridComponent';

export default Relay.createContainer(ImageGrid, {
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
              scaledAt320X240Url
              scaledAt640X480Url
              shotAt
            }
          }
        }
      }`
  }
});
