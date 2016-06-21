/* eslint-disable global-require */
import React from 'react';
import Relay from 'react-relay';

class DayList extends React.Component {
  static propTypes = {
    days: React.PropTypes.object.isRequired
  };

  render() {
    return (
      <ul>
         {this.props.days.edges.map(edge => {
           return (
             <li key={edge.node.id}>{edge.node.date}</li>
           );
         })}
      </ul>
    );
  }
}


export default Relay.createContainer(DayList, {
  fragments: {
    days: () => Relay.QL`
      fragment on Camera {
        days(first: 10, orderBy: "-date") {
          edges {
            node {
              id
              date
            }
          }
        }
      }`
  }
});
