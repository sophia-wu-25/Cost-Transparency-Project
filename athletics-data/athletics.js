//import commands
const fs = require("fs");
const { parse } = require("csv-parse");

fs.createReadStream("./athletics/athletics cost.csv");
const athelticsData = []; // textbook price bible (holds all textbook information)
//const ll = new LinkedList();

//reads into textbookData array
fs.createReadStream("./athletics/athletics cost.csv")
  .pipe(
    parse({
      delimiter: ",",
      from_line: 1, //starts @ line 1
      columns: true, //makes columns into key
      ltrim: true //removes white space
    })
  )
  // push specific columns into array
  .on("data", function (row) {
    const desiredColumns = {
        "Girls/Boys":row["Girls or Boys"],
        "Thirds/JV/V": row["Thirds / JV / V"],
        "Sport": row["Sport"],
        "Shoe Cost": row["What is the average cost of shoes?"],
        "Clothing Required By Sport": row["List any clothing required by the sport that a player must purchase."],
        "Sport Clothing Price": row["What is the estimated cost of these sports requirements?"],
        "Clothing Required By Coach": row["List any clothing requirements you, as a coach, want your players to have."],
        "Coach Clothing Price": row["What is the estimated cost of these coach requirements?"],
        "Equipment Required": row["What equipment is required for a player to purchase in order to participate on the team?"],
        "Required Equipment Price": row["What is the average cost of this equipment?"],
        "Training Trip Costs": row["If your team goes on any training trips, please estimate the cost each player would pay."],
        "Additional Expenses": row["Are there any additional expenses not covered by the previous questions? If so, please note them below."],
        "Cost Of Additional Expenses": row["What is the average cost of these addional expenses?"]
    }
    athelticsData.push(desiredColumns);
  })
  // in case of errors
  .on("error", function (error) {
    console.log(error.message);
  })
  // result array
  .on("end", function () {
    console.log("parsed athletics data:");
    console.log(athelticsData);
    module.exports = athelticsData; // Exports array
  }); 

