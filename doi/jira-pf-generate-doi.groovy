import groovy.json.*

Boolean DEBUG = true
String URL = "https://pubsub.googleapis.com/v1/projects/czk-tools/topics/doi-request:publish"
// FIXME: change it to final key after moving to Cloud Endpoints
String TOKEN = "ya29.A0AVA9y1scGIsS-xdmHttr1XZx45pvI4jYHGJrZzYhsAtQhHUiXTvUf5M1DzBuVKUmaYj_flNodu17D2HMYY52vSDO4USksoJ-IbbXTvxxk12JdAi5Ll9z9NwUIaVxxhpZB8XnK9NugDI9natEwT8r0KnkZBx4AhEfIF2H0t0aCgYKATASATASFQE65dr8pjVL5RfSF8EyHWgPydWJ1w0174"

class PubSubBody {
    List<PubSubMessage> messages = []
}
class PubSubMessage {
    String data

    public PubSubMessage(def data) {
        if(!(data instanceof String)) {
            data = JsonOutput.toJson(data)
        }
        this.data = data.toString().bytes.encodeBase64().toString()
    }
}
class DOIRequest {
    String issueKey;
    String baseUrl;
}
DOIRequest doiRequest = new DOIRequest(issueKey: issue.key, baseUrl: baseUrl);
PubSubBody body = new PubSubBody();
body.messages.add(new PubSubMessage(doiRequest));

String logComment = "h1. Wywołanie 'Generuj DOI'\n*URL:* ${URL}"
logComment += "\n*Request body:*\n{code:JSON}${JsonOutput.prettyPrint(JsonOutput.toJson(body))}{code}";

HttpResponse<JsonNode> response = Unirest.post(URL)
    .header("Content-Type", "application/json; charset=utf-8")
    .header("Authorization", "Bearer $TOKEN")
    .body(body)
    .asJson();

if(response) {
    logComment += response.status==200 ? "\n(/)" : "\n(x)";
    if(response.body) {
        logComment += " *Response status code ${response.status} with body:*\n{code:JSON}${JsonOutput.prettyPrint(response.body.toString())}{code}";
    } else {
        logComment += " *Response status code: ${response.status})*. No body."
    }
} else {
    logComment += "\n (!) *Response is empty...*";
}


if(DEBUG || response?.status != 200) {
    Unirest.post("/rest/api/2/issue/${issue.key}/comment")
        .header("Content-Type", "application/json")
        .body([body: logComment])
        .asObject(Map);
}
