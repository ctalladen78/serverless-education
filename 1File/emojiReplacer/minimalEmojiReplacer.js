// This function uses the Node.js 10.x runtime

exports.handler = async event => {
  const indexPage = `
    <html>
    <head>
    <meta charset="utf-8">
    <meta content="width=device-width,initial-scale=1,minimal-ui" name="viewport">
    </head>
    <body>
        <div id="app">
            <h1>Emoji replacement activity</h1>
            <p>Activity variables: {{layoutItems[0].subHeader}}</p>
            <textarea v-model="layoutItems[0].vModel" readonly></textarea>
            <p>Editable Code Block: {{layoutItems[1].subHeader}}</p>
            <textarea v-model="layoutItems[1].vModel"></textarea>
            <p>status: {{status}}</p>
            <button v-on:click="postContents">Submit</button>
        </div>
    </body> 
    <script src="https://unpkg.com/vue"></script>
    <script>
    
    new Vue({
        el: '#app',
        data: function () {
            return {
            layoutItems: [
                {subHeader:'comma-separated sequence comprising a string, replaced character(s), replacement characters(s)', vModel:"hello,h,hoho"},
                {subHeader:'Your code goes below', vModel:\`"hello".replace("h","hoho")\`}
                ], status:" 🔴"}
        },
        methods: {
            postContents: function () {
                // comment: leaving the gatewayUrl empty - API will post back to itself
                const gatewayUrl = '';
                fetch(gatewayUrl, {
                    method: "POST",
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({shown:{0:this.layoutItems[0].vModel},editable:{0:this.layoutItems[1].vModel}})
                }).then(response => {
                        return response.json()
                    }).then(data => {
                        this.answer = JSON.parse(JSON.stringify(data))
                        return this.toggleQuestionStatus(data)
                    })
            },        
            toggleQuestionStatus (data) {
                if (data.textFeedback) {
                    const searchText = data.textFeedback
                    if (searchText.includes("You got the answer")) this.status = " ✔️";
                    else if (searchText.includes("You have missed")) this.status = " 🤨";
                }
            }
        }
      })
    </script>
    </html>
    `;

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
