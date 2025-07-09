
import { tool } from "ai";
import { listAllWebhookSubscriptionForToolProxyDataSchema } from "./aitm.schema.ts";
import { listAllWebhookSubscriptionForToolProxy, ListAllWebhookSubscriptionForToolProxyData } from "..";

export default tool({
  description: `
  List all Webhook Subscription for a tool proxy
This endpoint returns a paginated list with a default
limit of 100 items per result set.
You can retrieve the next result set by setting a 'StartKey'
header in your next request
with the value of the 'EndKey' header in the response.

Example use of a
'StartKey' header object:
{
"Id":"71d6dfba-0547-477d-b41d-db8cb528c6d1","DeveloperKey":"10000000000001" }
    `,
  parameters: listAllWebhookSubscriptionForToolProxyDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListAllWebhookSubscriptionForToolProxyData, "url"> ) => {
    try {
      const { data } = await listAllWebhookSubscriptionForToolProxy(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    