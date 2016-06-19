/* eslint-disable no-var, func-names, prefer-arrow-callback, global-require */

var getbabelRelayPlugin = require('babel-relay-plugin');
var schema = require('./schema.json');

module.exports = getbabelRelayPlugin(schema.data);
