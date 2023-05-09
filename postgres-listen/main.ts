import postgres from "https://deno.land/x/postgresjs@v3.3.4/mod.js";

const sql = postgres();

const channel = Deno.env.get("CHANNEL") || "test";
const webhook = Deno.env.get("WEBHOOK") || "test";
console.log(
  `listening on channel ${channel} and sending webhooks to ${webhook}`
);

await sql.listen(Deno.args[0], async (payload) => {
  console.log("Sending payload: " + payload);
  try {
    await fetch(webhook, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: payload,
    });
  } catch (e) {
    console.error("Error sending webhook:", e);
  }
});
