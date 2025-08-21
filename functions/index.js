const { GoogleGenerativeAI } = require("@google/generative-ai");
const {setGlobalOptions} = require("firebase-functions");
const {onRequest} = require("firebase-functions/https");
const {onValueCreated} = require("firebase-functions/database");
const {getDatabase}=require("firebase-admin/database");
const logger = require("firebase-functions/logger");
const genfunc = require("firebase-functions");
setGlobalOptions({maxInstances: 10});


const admin=require("firebase-admin");
admin.initializeApp();

const genAI = new GoogleGenerativeAI(genfunc.config().gemini.key);
console.log("Gemini key exists:", !!genfunc.config().gemini.key);

async function check_content(textContent) {

  const model = genAI.getGenerativeModel({ model: "gemini-2.5-flash" });
  const result = await model.generateContent(`(${textContent}) if there is any misinfo/threat/scam/fake news/etc. then respond with corrected content/news, otherwise do not respond with any word.`);

  return result.response.candidates[0].content.parts[0].text || "";
}
// const genai = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
// function check_content(textContent) {
//   const response = genai.models.generateContent({
//     model: "gemini-1.5-flash",
//     contents: [{
//       role: "user",
//       parts: [{ text: `(${textContent}) if there is any misinfo/threat/scam/fake news/etc. then respond with corrected content/news, otherwise do not respond with any word.` }]
//     }]
//   });
//   return response.text;
// }
exports.helloWorld = onRequest((request, response) => {
  logger.info("Hello logs!", {structuredData: true});
  response.send("Hello from Firebase!");
});

exports.trigger = onValueCreated("/content/{pushId}",async (event)=>{
  const newData= event.data.val();
  const id=event.params.pushId;
  const db=getDatabase();
  logger.info(id, " New Data Triggered");
  if(newData && newData.content_text && newData.content_text.trim().length>0){
    const response=await check_content(newData.content_text);
    if(response.trim().length>0){
      await db.ref(`/content/${id}/verdict`).set("unauthorized content");
      await db.ref(`/content/${id}/reason`).set(response);
    }
    else{
      await db.ref(`/content/${id}/verdict`).set("authorized content");
    }
  }
  else {
    await db.ref(`/content/${id}/verdict`).set("content not found");
  }
  return db.ref(`/content/${id}/status`).set("checked");
});