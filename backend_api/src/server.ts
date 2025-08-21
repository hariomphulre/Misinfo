import express from 'express';
import bodyParser, { text } from 'body-parser';


import fetch from 'node-fetch';
import aiplatform, { helpers } from '@google-cloud/aiplatform'
import dotenv from 'dotenv'
import { execSync } from 'child_process';

dotenv.config()
// Env vars (set these in .env or Cloud Run variables)
const PORT = process.env.PORT || 8080;
const PROJECT_ID = process.env.GOOGLE_CLOUD_PROJECT || process.env.PROJECT_ID || 'YOUR_PROJECT_ID';
const LOCATION = process.env.LOCATION || 'us-central1';
const INDEX_ENDPOINT = process.env.INDEX_ENDPOINT || 'projects/PROJECT_ID/locations/LOCATION/indexEndpoints/INDEX_ENDPOINT_ID';
const DEPLOYED_INDEX_ID = process.env.DEPLOYED_INDEX_ID || 'DEPLOYED_INDEX_ID';
const API_ENDPOINT = 'us-central1-aiplatform.googleapis.com'

// Initialize clients
const app = express();
app.use(bodyParser.json());


const { PredictionServiceClient } = aiplatform.v1;
const clientOptions = { apiEndpoint: API_ENDPOINT };
const embeddingModelEndpoint = `projects/${PROJECT_ID}/locations/${LOCATION}/publishers/google/models/gemini-embedding-001`;
const dimensionality = '3072';

async function embedTexts(texts: string[], task: string) {
  const client = new PredictionServiceClient(clientOptions);

  const embeddings: number[][] = [];

  for (const text of texts) {
    const instance = helpers.toValue({ content: text, task_type: task });

    const parameters = helpers.toValue(
      parseInt(dimensionality) > 0 ? { outputDimensionality: parseInt(dimensionality) } : {}
    );

    const request = {
      endpoint: embeddingModelEndpoint,
      instances: [instance],
      parameters
    } as any;

    const [response] = await client.predict(request);

    const predictions = response.predictions as any;
    const values = predictions[0].structValue.fields.embeddings.structValue.fields.values.listValue.values.map((v: any) => v.numberValue);
    embeddings.push(values);
  }
  return embeddings;
}

// EmbedText ( different format )

// async function embedTexts() {
//   const instances = texts
//     .split(';')
//     .map(e => helpers.toValue({ content: e, task_type: task }));

//   const client = new PredictionServiceClient(clientOptions);
//   const parameters = helpers.toValue(
//     parseInt(dimensionality) > 0 ? { outputDimensionality: parseInt(dimensionality) } : {}
//   );
//   const allEmbeddings = []
//   // gemini-embedding-001 takes one input at a time.
//   for (const instance of instances) {
//     const request = { endpoint, instances: [instance], parameters } as any;
//     const [response] = await client.predict(request);
//     const predictions = response.predictions as any;

//     // console.log(predictions)
//     const embeddings = predictions.map((p: any) => {
//       const embeddingsProto = p.structValue.fields.embeddings;
//       const valuesProto = embeddingsProto.structValue.fields.values;
//       return valuesProto.listValue.values.map((v: any) => v.numberValue);
//     });

//     allEmbeddings.push(embeddings[0])
//   }


//   // console.log('Got embeddings: \n' + JSON.stringify(allEmbeddings));
//   return allEmbeddings[0]
// }



// Upserting Index

// async function upsertToIndex() {
//   const client = new IndexServiceClient({
//     apiEndpoint: API_ENDPOINT
//   });
//   const embedding = await callPredict();
//   // Call updateIndex with vector
//   const request = {
//     index: INDEX_ENDPOINT_UPSERT,
//     datapoints: [
//       {
//         datapointId: "doc_1",
//         featureVector: embedding,
//         restricts: [],
//       },

//     ],
//   } as any;
//   console.log(request)
//   const [response] = await client.upsertDatapoints(request);

//   console.log("Upsert response:", response)
// }

// upsertToIndex().catch(console.error);




// Retrieve Facts from index
async function searchIndex(embedding: any) {
  // Get access token using gcloud
  const token = execSync("gcloud auth print-access-token").toString().trim();

  const url = process.env.INDEX_QUERY_URL as string;
  console.log("Searching")
  const body = {
    deployedIndexId: DEPLOYED_INDEX_ID as string,
    queries: [
      {
        datapoint: {
          featureVector: embedding
        },
        neighborCount: 10
      }
    ],
    returnFullDatapoint: true
  };

  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  });

  const data: any = await res.json();
  console.log("Similarity Search: ", data);
  return data?.nearestNeighbors
}




/*
  queryBigQueryFallback: Simple lexical fallback if vector search returns nothing.
  Assumes a table with columns: id, title, url, source, published_at, text
*/
// async function queryBigQueryFallback(claim: string, limit = 5) {
//     const sql = `
//     SELECT title, url, source, SUBSTR(text, 1, 300) AS snippet
//     FROM \`${PROJECT_ID}.${BQ_DATASET}.${BQ_TABLE}\`
//     WHERE LOWER(text) LIKE LOWER(@q)
//     ORDER BY published_at DESC
//     LIMIT ${limit}
//   `;
//     const [rows] = await bq.query({
//         query: sql,
//         params: { q: `%${claim.slice(0, 200)}%` },
//     });
//     return rows.map((r: any) => ({ title: r.title, url: r.url, source: r.source, snippet: r.snippet }));
// }

// Basic heuristic support/oppose scoring using presence of negate words in snippets
// function quickSupportOppose(claim: string, evts: Array<{ snippet: string }>): { support: number; oppose: number } {
//     const c = claim.toLowerCase();
//     const negWords = ['false', 'fake', 'not true', 'hoax', 'misleading', 'no evidence', 'debunk'];
//     let support = 0, oppose = 0;
//     for (const e of evts) {
//         const s = (e.snippet || '').toLowerCase();
//         if (!s) continue;
//         const neg = negWords.some(w => s.includes(w));
//         if (neg) oppose += 1; else support += 0.5; // crude heuristic for MVP
//     }
//     const n = Math.max(1, evts.length);
//     return { support: support / n, oppose: oppose / n };
// }



// Health check
app.get('/health', (_req, res) => res.json({ ok: true }));

// // Verify a claim (main endpoint)
app.post('/api/claims/verify', async (req, res) => {
  try {
    const claim: string = (req.body?.claim || '').trim();
    if (!claim) return res.status(400).json({ error: 'claim is required' });

    const texts = <any>[];
    texts.push(claim)

    // 1) Embed claim
    const embedding = await embedTexts(texts, "RETRIEVAL_QUERY");

    // 2) Vector search (Matching Engine)
    const evidence = await searchIndex(embedding);

    // 3) Fallback to BigQuery if needed
    // if (!evidence || evidence.length === 0) {
    //   evidence = await queryBigQueryFallback(claim, 5);
    // }

    // 4) Compute simple support/oppose heuristics (MVP)
    // const { support, oppose } = quickSupportOppose(claim, evidence);

    // 5) LLM verdict + explanation constrained to evidence
    // const { verdict, explanation } = await generateVerdictExplanation(claim, evidence, support, oppose);

    // Confidence: simple mapping
    // const confidence = Math.min(0.99, Math.max(0.5, Math.max(support, oppose)));



    // return res.json({ claim, verdict, confidence, evidence });
    res.json({ claim, evidence })
  } catch (err: any) {
    console.error(err);
    return res.status(500).json({ error: err.message || 'internal_error' });
  }
});

// // Recent checks (demo-only)
// app.get('/api/claims/history', (_req, res) => {
//     res.json(history);
// });

// // Collect feedback (stub)
// app.post('/api/feedback', (req, res) => {
//     // TODO: persist to Firestore or BigQuery
//     console.log('Feedback:', req.body);
//     res.json({ ok: true });
// });

// ----------------------
// 5) Start server
// ----------------------
app.listen(PORT, () => {
  console.log(`MisinfoGuard backend listening on :${PORT}`);
});
