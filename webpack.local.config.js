const webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');

var config = require('./webpack.base.config');

config.devtool = 'eval';

config.entry =  [
    'webpack-dev-server/client?http://timelapse-manager.aldryn.me:3000',
    'webpack/hot/only-dev-server',
    './assets/js/index'
];
// Tell django to use this URL to load packages and not use STATIC_URL + bundle_name
config.output.publicPath = 'http://timelapse-manager.aldryn.me:3000/assets/bundles/';

config.plugins = config.plugins.concat([
    new webpack.HotModuleReplacementPlugin(),
    new webpack.NoErrorsPlugin(), // don't reload if there is an error
    new BundleTracker({filename: './webpack-stats.json'})
]);

config.module.loaders[0] = {
  test: /\.jsx?$/,
  exclude: /node_modules/,
  loaders: ['react-hot', 'babel'],
};

module.exports = config;
