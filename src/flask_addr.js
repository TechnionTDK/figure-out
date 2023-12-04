// the address is taken from file .env
// this file is not commited to git and should be created manually
// also in the production environment.
console.log("VUE_APP_FLASK_SERVER: " + process.env.VUE_APP_FLASK_SERVER);
console.log("VUE_APP_FLASK_SERVER_PORT: " + process.env.VUE_APP_FLASK_SERVER_PORT);
export var flaskAddr = `${process.env.VUE_APP_FLASK_SERVER}:${process.env.VUE_APP_FLASK_SERVER_PORT}` + "/";
console.log("flaskAddr: " + flaskAddr);