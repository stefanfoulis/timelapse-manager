import Relay from 'react-relay';
import ImageGrid from './ImageGridComponent';

export default Relay.createContainer(ImageGrid, {
  fragments: {
    camera: () => Relay.QL`
      fragment on Camera {
        images(first: 9, orderBy: "-shot_at") {
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
