# This activity requires Python 3.7 runtime
# -*- coding: utf-8 -*-
import json
import traceback
import doctest

import re

import signal
import time

    
def lambda_handler(event, context):
    
    def run_local(requestDict):
      byteCodeChecker = "\ndef byteCodeChecker(function, field, value):\n import dis\n byteCode = dis.Bytecode(function)\n fields = {'OPNAME':0, 'ARGREPR':3} \n for instruction in byteCode:\n  if instruction[fields[field]] == value:\n   return f'found {value}'\n else:\n  return f'{value} not found'"
      codeInfoChecker = "\ndef codeInfoChecker(function, value):\n import dis\n codeInfo = dis.code_info(function)\n if value in codeInfo:\n  return f'found {value}'\n else:\n  return f'{value} not found'"
      solution = requestDict['solution'] + codeInfoChecker + byteCodeChecker
      tests = requestDict['tests']  
      import io
      import sys
      output = io.StringIO()
      sys.stdout = output
      
      try:
        namespace = {}
        compiled = compile('import json', 'submitted code', 'exec')
        exec(compiled, namespace)
        compiled = compile(solution, 'submitted code', 'exec')
        exec(compiled, namespace)
        namespace['YOUR_SOLUTION'] = solution.strip()
        namespace['LINES_IN_YOUR_SOLUTION'] = len(solution.strip().splitlines())
        test_cases = doctest.DocTestParser().get_examples(tests)
        execute_test_cases(test_cases, namespace)
        results, solved = execute_test_cases(test_cases, namespace)
        printed = output.getvalue()
        responseDict = {"solved": solved , "results": results, "printed":printed}
        responseJSON = json.dumps(responseDict)
        return responseJSON
      except:
        errors = traceback.format_exc()
        responseDict = {'errors': '%s' % errors}
        responseJSON = json.dumps(responseDict)
        return responseJSON
    
    def execute_test_cases(testCases, namespace):
      resultList = []
      solved = True
      for e in testCases:
        if not e.want:
          exec(e.source) in namespace
          continue
        call = e.source.strip()
        got = eval(call, namespace)
        expected = eval(e.want, namespace)
        correct = True
        if got == expected:
          correct = True
        else:
          correct = solved = False
        resultDict = {'call': call, 'expected': expected, 'received': "%(got)s" % {'got': got}, 'correct': correct}
        resultList.append(resultDict)
      return resultList, solved
    
    method = event.get('httpMethod',{}) 
        
    indexPage="""
    <html>
    <head>
    <meta charset="utf-8">
    <meta content="width=device-width,initial-scale=1,minimal-ui" name="viewport">
    <link rel="stylesheet" href="https://unpkg.com/vue-material@beta/dist/vue-material.min.css">
    <link rel="stylesheet" href="https://unpkg.com/vue-material@beta/dist/theme/default.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.32.0/codemirror.min.css" />
  </head>
    <body>
         <h1>Pythonic Code Activity</h1>
        <div id="app">
            <md-tabs>
                <md-tab v-for="question in questions" :key=question.name v-bind:md-label=question.name+question.status>
                    <doctest-activity v-bind:layout-things=question.layoutItems v-bind:question-name=question.name  @questionhandler="toggleQuestionStatus"/>
                </md-tab>
            </md-tabs>
            </div>
        </div>
    </body> 
    <script src="https://unpkg.com/vue"></script>
    <script src="https://unpkg.com/vue-material@beta"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.32.0/codemirror.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.48.4/mode/python/python.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/vue-codemirror@4.0.6/dist/vue-codemirror.min.js"></script>
    <script>
    Vue.use(VueMaterial.default)
    Vue.use(window.VueCodemirror)
    
    Vue.component('doctest-activity', {
        props: ['layoutThings', 'questionName'],
        data: function () {
            return {
            answer:"",
            layoutItems: this.layoutThings,
            cmOptions: {
              mode: 'python',
              lineNumbers: true
            },
            cmReadOnly: {
              lineNumbers: true,
              mode:  "python",
              readOnly: true
            }
        }
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
            return this.$emit('questionhandler',{data, questionName:this.questionName})
            })
         }
        },
        template: 
        `<div class="md-layout  md-gutter">
            <div id="cardGroupCreator" class="md-layout-item md-size-50">
              <md-card>
                    <md-card-header>
                        <md-card-header-text>
                            <div class="md-title">{{layoutItems[2].header}}</div>
                            <div class="md-subhead">{{layoutItems[2].subHeader}}</div>
                        </md-card-header-text>
                    </md-card-header>
                    <md-card-content>
                        <md-field>
                            <md-textarea v-model="layoutItems[2].vModel" readonly></md-textarea>
                        </md-field>
                    </md-card-content>
                </md-card>
                <md-card>
                    <md-card-header>
                        <md-card-header-text>
                            <div class="md-title">{{layoutItems[1].header}}</div>
                            <div class="md-subhead">{{layoutItems[1].subHeader}}</div>
                        </md-card-header-text>
                            <md-card-media>
                                <md-button class="md-raised md-primary" v-on:click="postContents">Submit</md-button>
                            </md-card-media>
                    </md-card-header>
                    <md-card-content>
                        <md-field>
                            <codemirror class="editableTextarea" v-model="layoutItems[1].vModel" :options="cmOptions"></codemirror>
                        </md-field>
                    </md-card-content>
                </md-card>
            </div>
            <div id="cardGroupPreview" class="md-layout-item md-size-50">
                 <md-card>
                    <md-card-header>
                        <md-card-header-text>
                            <div class="md-title">{{layoutItems[0].header}}</div>
                            <div class="md-subhead">{{layoutItems[0].subHeader}}</div>
                        </md-card-header-text>
                    </md-card-header>
                    <md-card-content>
                        <md-field>
                             <codemirror class="editableTextarea" v-model="layoutItems[0].vModel" :options="cmReadOnly"></codemirror>
                        </md-field>
                    </md-card-content>
                </md-card>
                <md-card>
                    <md-card-header>
                        <md-card-header-text>
                            <div class="md-title">Output</div>
                            <div class="md-subhead">Test results</div>
                        </md-card-header-text>
                    </md-card-header>
                    <md-card-content>
                        <md-field>
                            <md-tabs>
                                <md-tab id="tab-htmlResults" md-label="HTML results">
                                    <div v-html="answer.htmlFeedback"></div>
                                </md-tab>
                                <md-tab id="tab-jsonResults" md-label="JSON results">
                                    <md-textarea v-model="answer.jsonFeedback" readonly></md-textarea>
                                </md-tab>
                                <md-tab id="tab-textResults" md-label="Text results">
                                    <md-textarea v-model="answer.textFeedback" readonly></md-textarea>
                                </md-tab>
                            </md-tabs>
                        </md-field>
                    </md-card-content>
                </md-card>
            </div>
        </div>
        `
    })
    
    new Vue({
        el: '#app',
        data: function () {
            return {
            questions:[
                {name:"question 1", layoutItems: [
                {header:"Tests", subHeader:'byteCodeChecker() and codeInfoChecker() are our functions used in these tests', vModel:">>> ifFunc(True,2)\\n2 \\n>>> ifFunc(bool('a'),11)\\n11 \\n>>> byteCodeChecker(ifFunc, 'ARGREPR', '==')\\n'== not found'"},
                {header:"Editable Code Block", subHeader:'Your code goes below. Avoid double quotes.', vModel:"def ifFunc(a,b):\\n if a == True:  \\n  return b\\n"},
                {header:"Introduction", subHeader:'', vModel:"When checking if a condition is True, prefer relying on the implicit “truthiness” of the object in the conditional statement using \\nif object:\\nthan\\nif object == True:"}
                ], status:" 🔴"},
                {name:"question 2", layoutItems: [
                {header:"Tests", subHeader:'byteCodeChecker() and codeInfoChecker() are our functions used in these tests', vModel:">>> forLoop([1,2,3])\\n6 \\n>>> forLoop([1,2,3,4,5])\\n15 \\n>>> byteCodeChecker(forLoop, 'OPNAME', 'FOR_ITER')\\n'found FOR_ITER'"},
                {header:"Editable Code Block", subHeader:'Your code goes below. Avoid double quotes.', vModel:"def forLoop(listOfNumbers):\\n total = 0 \\n index = 0 \\n while index < len(listOfNumbers):\\n  total += listOfNumbers[index]\\n  index += 1\\n return total"},
                {header:"Introduction", subHeader:'', vModel:"Use a for-in loop to iterate through elements of an iterable like a list/dictionary than creating an index and incrementing that index after every loop."}
                ], status:" 🔴"},
                {name:"question 3", layoutItems: [
                {header:"Tests", subHeader:'byteCodeChecker() and codeInfoChecker() are our functions used in these tests', vModel:">>> useEnumerate(['bunnyA','bunnyB'])\\n'bunnyA is at index 0 bunnyB is at index 1 ' \\n>>> useEnumerate(['crabbyA','crabbyB'])\\n'crabbyA is at index 0 crabbyB is at index 1 ' \\n>>> codeInfoChecker(useEnumerate, 'enumerate')\\n'found enumerate'"},
                {header:"Editable Code Block", subHeader:'Your code goes below. Avoid double quotes.', vModel:"def useEnumerate(list):\\n locationOfItems = '' \\n for index in range(len(list)): \\n  value = list[index]\\n  locationOfItems += f'{value} is at index {index} '\\n return locationOfItems"},
                {header:"Introduction", subHeader:'', vModel:"We can use the enumerate function to obtain the index that the loop is in. The range(len()) solution below works but it is more pythonic to use enumerate"}
                ], status:" 🔴"},
                {name:"question 4", layoutItems: [
                {header:"Tests", subHeader:'byteCodeChecker() and codeInfoChecker() are our functions used in these tests', vModel:">>> useZip(['pikachu','bulbasaur'],['lightning type','grass type'])\\n'pikachu is lightning type bulbasaur is grass type ' \\n>>> useZip(['Barney','Pooh'],['T-rex','teddy bear'])\\n'Barney is T-rex Pooh is teddy bear ' \\n>>> codeInfoChecker(useZip, 'zip')\\n'found zip'"},
                {header:"Editable Code Block", subHeader:'Your code goes below. Avoid double quotes.', vModel:"def useZip(list1, list2):\\n resultString = ''\\n for index, value in enumerate(list1):\\n  resultString += f'{value} is {list2[index]} '\\n return resultString"},
                {header:"Introduction", subHeader:'', vModel:"The zip function pairs the first elements of each iterator together then pairs the second elements together and so on. If the iterables in the zip function are not the same length, then the smallest length iterable decides the length of the generated output."}
                ], status:" 🔴"},
                {name:"question 5", layoutItems: [
                {header:"Tests", subHeader:'byteCodeChecker() and codeInfoChecker() are our functions used in these tests', vModel:">>> eat()\\n'I ate burger I ate fries '\\n>>> codeInfoChecker(foodGenerator, 'GENERATOR')\\n'found GENERATOR'"},
                {header:"Editable Code Block", subHeader:'Your code goes below. Avoid double quotes.', vModel:"# generator function which yields data values\\ndef foodGenerator():\\n yield 'ice cream'\\n\\n# eat() function calls foodGenerator() and iterates over the yielded values\\ndef eat():\\n foodEaten = ''\\n for food in foodGenerator():\\n  foodEaten += f'I ate {food} '\\n return foodEaten"},
                {header:"Introduction", subHeader:'', vModel:"Using something called generators, we can handle large amounts of data or computation easily.\\n\\nThis is because how ever large the amount of data, generators represent it as a stream of data and provide one data value at a time out of the data stream. This means we can run intensive computation without crashing our computer since it works with just one value at a time.\\n\\nA generator function consists of one or more yield statements. Calling the generator function creates an iterable, and iterating it runs the code in the function. Each yield statement executed produces another value in the stream."}
                ], status:" 🔴"}
            ]
        }
        },
         methods: {
            toggleQuestionStatus (response) {
                const {data, questionName} = response
                if (data.htmlFeedback) {
                    const searchText = data.htmlFeedback
                    searchText.search(/b2d8b2/) !== -1 ?
                        searchText.search(/#ff9999/) == -1 ?
                        this.questions.find(item => item.name === questionName).status = " ✔️"
                        :
                        this.questions.find(item => item.name === questionName).status = " 🤨"
                    :
                    this.questions.find(item => item.name === questionName).status = " 🔴"
                }
            }
        }
      })
    </script>
    <style lang="scss" scoped>
    .md-card {
        width: 90%;
        margin: 20px;
        display: inline-block;
        vertical-align: top;
        min-height:200px
    }
    .md-card-content {
        padding-bottom: 16px !important;
    }
    button {
        display:block;
        margin: 20px 60px 20px 60px;
        width:200px !important;
    }
    #cardGroupCreator {
        display:flex;
        flex-direction:column;
        padding-right: 0px
    }
    #cardGroupPreview .md-card {
        width: 90%;
    }
    #cardGroupPreview{
        padding-left: 0px
    }
    #cardGroupPreview .md-tab{
        height:100%
    }
    textarea {
        font-size: 1rem !important;
        min-height: 175px !important
    }
    .md-tabs{
        width:100%;
    }
    .md-tab{
        overflow-x: auto;
    }
    .md-tab::-webkit-scrollbar {
    width: 0px;
    }
    html {
        width:95%;
        margin:auto;
        mix-blend-mode: darken
    }
    h1{
        padding:20px;
        margin:auto;
        text-align: center
    }
    .md-content{
        min-height:300px
    }
    .md-tabs-container, .md-tabs-container .md-tab textarea, .md-tabs-content{
        height:100% !important
    }
    .md-field{
        margin:0px;
        padding:0px
    }
    .md-tabs-navigation{
        justify-content:center !important
    }
    .md-card-media{
        width:400px !important
    }
    .md-button{
        margin:10px !important
    }
    .cm-s-default{
        height:100%
    }
    .md-card-header{
        padding:0 16px 16px 16px
    }
    </style>
    </html>
    """
    
    if method == 'GET':
        return {
            "statusCode": 200,
            "headers": {
            'Content-Type': 'text/html',
            },
            "body": indexPage
        }
        
    if method == 'POST':
        import re
        bodyContent = event.get('body',{}) 
        parsedBodyContent = json.loads(bodyContent)
        testCases = re.sub('&zwnj;.*&zwnj;','',parsedBodyContent["shown"]["0"], flags=re.DOTALL) 
        solution = parsedBodyContent["editable"]["0"] 

        timeout = False
        # handler function that tell the signal module to execute
        # our own function when SIGALRM signal received.
        def timeout_handler(num, stack):
            print("Received SIGALRM")
            raise Exception("processTooLong")

        # register this with the SIGALRM signal    
        signal.signal(signal.SIGALRM, timeout_handler)
        
        # signal.alarm(10) tells the OS to send a SIGALRM after 10 seconds from this point onwards.
        signal.alarm(10)

        # After setting the alarm clock we invoke the long running function.
        try:
            jsonResponse = run_local({"solution": solution, "tests": testCases})
        except Exception as ex:
            if "processTooLong" in ex:
                timeout = True
                print("processTooLong triggered")
        # set the alarm to 0 seconds after all is done
        finally:
            signal.alarm(0)

        jsonResponseData = json.loads(jsonResponse)
        
        solvedStatusText = expectedText = receivedText = callText = textResults = tableContents = ""
        overallResults = """<span class="md-subheading">All tests passed: {0}</span><br/>""".format(str(jsonResponseData.get("solved")))
        numTestCases = len(re.findall('>>>', testCases))
        resultContent = jsonResponseData.get('results') 
        textBackgroundColor = "#ffffff"
        
        if resultContent:
            for i in range(len(resultContent)):
                expectedText = resultContent[i]["expected"]
                receivedText = resultContent[i]["received"]
                correctText = resultContent[i]["correct"]
                callText = resultContent[i]["call"]
                if str(expectedText) == str(receivedText):
                    textResults = textResults + "\nHurray! You have passed the test case. You called {0} and received {1} against the expected value of {2}.\n".format(callText, receivedText, expectedText)
                    textBackgroundColor = "#b2d8b2"
                else:
                    textResults = textResults + "\nThe test case eludes your code so far but try again! You called {0} and received {1} against the expected value of {2}.\n".format(callText, receivedText, expectedText)
                    textBackgroundColor = "#ff9999"
                tableContents = tableContents + """
                <tr bgcolor={4}>
                    <td>{0}</td>
                    <td>{1}</td>
                    <td>{2}</td>
                    <td>{3}</td>
                </tr>
                """.format(callText,expectedText,receivedText,correctText,textBackgroundColor)
        solvedStatusText = str(jsonResponseData.get("solved")) or "error"
        textResults = """All tests passed: {0}\n""".format(solvedStatusText) + textResults
        if not resultContent:
            textResults = "Your test is passing but something is incorrect..."
            
        if timeout or jsonResponseData.get("errors"):
            textResults = "An error - probably related to code syntax - has occured. Do look through the JSON results to understand the cause."
            tableContents = """
                <tr>
                    <td></td>
                    <td></td>
                    <td>error</td>
                    <td></td>
                </tr>
                """
        htmlResults="""
            <html>
                <head>
                    <meta charset="utf-8">
                    <meta content="width=device-width,initial-scale=1,minimal-ui" name="viewport">
                </head>
                <body>
                    <div>
                        {0}
                        <span class="md-subheading tableTitle">Tests</span>
                        <table>
                             <thead>
                                <tr>
                                    <th>Called</th>
                                    <th>Expected</th>
                                    <th>Received</th>
                                    <th>Correct</th>
                                </tr>
                            </thead>
                            <tbody>
                                {1}
                            </tbody>
                        </table>
                    </div>
                </body>
                <style>
                br {{
                    display:block;
                    content:"";
                    margin:1rem
                }}
                table{{
                    text-align:center
                }}
                .tableTitle{{
                    text-decoration:underline
                }}
                </style>
            </html>
            """.format(overallResults,tableContents)
        return {
            "statusCode": 200,
            "headers": {
            "Content-Type": "application/json",
                },
            "body":  json.dumps({
                "isComplete":jsonResponseData.get("solved"),
                "jsonFeedback": jsonResponse,
                "htmlFeedback": htmlResults,
                "textFeedback": textResults
            })
            }