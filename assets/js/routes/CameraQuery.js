import Relay from 'react-relay';

export default {
  camera: () => Relay.QL`
    query { camera(id: "Q2FtZXJhOjhiMjY3YzlhLTIzNTEtNGI3MS04NDc5LTdiZmI1MDBiYWY5ZA==") }
  `
};
