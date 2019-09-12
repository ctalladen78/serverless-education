// This function uses the Node.js 10.x runtime
const fs = require("fs");

exports.handler = async event => {
  const indexPage = fs.readFileSync("./index.html", "utf8");

  if (event.httpMethod === "GET") {
    return {
      statusCode: 200,
      headers: {
        "Content-Type": "text/html"
      },
      body: indexPage
    };
  }

  function throwError(errorName) {
    throw new Error(errorName);
  }
  const trimAndStringify = input => input.toString().trim();

  if (event.httpMethod === "POST") {
    const parsedBodyContent = JSON.parse(event.body);
    const activityVars = parsedBodyContent["shown"]["0"];
    const userSolution = parsedBodyContent["editable"]["0"];
    let executeUserSolution = "";
    let activityVariables = "";
    let errorMessage = "";
    let results = "";
    try {
      activityVariables = activityVars.split(",");
      activityVariables[0]
        ? activityVariables[1]
          ? activityVariables[2]
            ? null
            : throwError("no third activity variable")
          : throwError("no second activity variable")
        : throwError("no first activity variable");
    } catch (error) {
      errorMessage = error.message;
    }
    try {
      executeUserSolution = eval(userSolution);
    } catch (error) {
      errorMessage = `error executing your code: ${error.message}`;
    }
    if (!errorMessage) {
      executeUserSolution ===
      trimAndStringify(activityVariables[0]).replace(
        trimAndStringify(activityVariables[1]),
        trimAndStringify(activityVariables[2])
      )
        ? (results = "You got the answer!")
        : (results = "You have missed the answer... check your code again?");
    }
    return {
      statusCode: 200,
      headers: {
        "Content-Type": "text/html"
      },
      body: JSON.stringify({
        textFeedback: results || errorMessage
      })
    };
  }
};
