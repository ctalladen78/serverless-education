// This function uses the Node.js 10.x runtime
const fs = require("fs");

exports.handler = async (event) => {
    
    const indexPage= fs.readFileSync("./index.html", "utf8")
    
    if (event.httpMethod === 'GET'){
        return {
            "statusCode": 200,
            "headers": {
            'Content-Type': 'text/html',
            },
            "body": indexPage
        }
    }
    
    const trimAndStr = input => input.toString().trim()
    
    if (event.httpMethod === 'POST'){
        const parsedBodyContent = JSON.parse(event.body)
        let activityVars = parsedBodyContent["shown"]["0"]
        const userSolution = parsedBodyContent["editable"]["0"]
        let results = ""
        
        activityVars = activityVars.split(",")
        const expectedSolution = `"${trimAndStr(activityVars[0])}".replace("${trimAndStr(activityVars[1])}","${trimAndStr(activityVars[2])}")`
        userSolution ===  expectedSolution ? (results = "You got the answer!") : results = "You have missed the answer."
        
        return {
            "statusCode": 200,
            "headers": {
            'Content-Type': 'text/html',
            },
            "body": JSON.stringify({
                "textFeedback": results
            })
        }
    }
};