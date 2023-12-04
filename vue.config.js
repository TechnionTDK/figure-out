const { defineConfig } = require("@vue/cli-service");
module.exports = defineConfig({
  lintOnSave: false,
  transpileDependencies: ["vuetify"],
  devServer: {
    port: 80
  }
});
