const express = require("express");
const app = express();
const cors = require("cors");
const bodyParser = require("body-parser");

app.use(cors({ origin: "http://localhost:80" }));

app.use(bodyParser.json());
app.use(
  bodyParser.urlencoded({
    extended: true,
  })
);

app.get("/:discordId", (req, res) => {
  let userData = require("/root/ValorantSkinChecker/API/userSkinData.json");
  myData = userData.filter((obj) => obj.account == req.params.discordId);
  if (myData.length > 0) {
    res.send(myData[0]);
  } else {
    res.send({});
  }
});

app.listen(8080, () => console.log("Server started on port 8080"));
