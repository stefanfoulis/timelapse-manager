const path = require("path");
const webpack = require('webpack');
const autoprefixer = require('autoprefixer');
const precss = require('precss');


module.exports = {
  context: __dirname,
  entry: [
    './assets/js/index'
  ],
  output: {
      path: path.resolve('./assets/bundles/'),
      filename: "[name]-[hash].js",
  },

  plugins: [
  ],

  module: {
    loaders: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        loaders: ['babel'],
      },
      {
        test: /\.css$/,
        loaders: ['style', 'css']
      },
      {
        test: /\.scss$/,
        loaders: [
          'style',
          'css?modules&importLoaders=1' +
            '&localIdentName=[name]__[local]___[hash:base64:5]!postcss'
        ]
      },
      {
        test: /\.(png|jpg|jpeg|gif|svg|woff|woff2)$/,
        loader: 'url-loader?limit=10000&name=assets/[hash].[ext]'
      }
    ]
  },
  resolve: {
    modulesDirectories: ['node_modules', 'bower_components'],
    extensions: ['', '.js', '.jsx']
  },
  postcss: () => [precss, autoprefixer]
}
