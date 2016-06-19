import Relay from 'react-relay';
import App from './AppComponent';
import Footer from '../Footer/FooterContainer';

import poll from 'relay-decorators/lib/poll';

export default Relay.createContainer(poll(15000)(App), {
  fragments: {
    viewer: () => Relay.QL`
      fragment on User {
        ${Footer.getFragment('viewer')}
        latestImage {
          scaledAt640X480Url
          shotAt
        }
      }`
  }
});
