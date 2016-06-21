import Relay from 'react-relay';
import App from './AppComponent';

import poll from 'relay-decorators/lib/poll';

export default Relay.createContainer(poll(15000)(App), {
  fragments: {
    camera: () => Relay.QL`
      fragment on Camera {
        name
        latestImage {
          scaledAt640X480Url
          shotAt
        }
      }`
  }
});
