module.exports = {
  devServer: {
    proxy: 'http://localhost:8080'
  }
}

const path = require("path");

module.exports = {
  outputDir: path.resolve(__dirname, "../templates/gen"),
  assetsDir: "../../static/gen"
}
