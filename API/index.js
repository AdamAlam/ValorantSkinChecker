const express = require("express");
const app = express();
const cors = require("cors");
const bodyParser = require("body-parser");
const fs = require("fs/promises");

app.use(cors({ origin: "http://localhost:80" }));

app.use(bodyParser.json());
app.use(
  bodyParser.urlencoded({
    extended: true,
  })
);

app.get("/:discordId", (req, res) => {
  myData = readData(req.params.discordId).then((myData) => {
    if (Object.keys(myData).length > 0) {
      res.send(myData).status(200);
    } else {
      res.send({}).status(200);
    }
  });
});

const readData = (discordId) => {
  return fs
    .readFile("/root/ValorantSkinChecker/API/userSkinData.json")
    .then((data) => {
      return JSON.parse(data).filter((obj) => obj.account == discordId).length >
        0
        ? JSON.parse(data).filter((obj) => obj.account == discordId)[0]
        : [];
    });
};

app.listen(8080, () => console.log("Server started on port 8080"));
