
import { tool } from "ai";
import { showSingleWebhookSubscriptionDataSchema } from "./aitm.schema.ts";
import { showSingleWebhookSubscription, ShowSingleWebhookSubscriptionData } from "..";

export default tool({
  description: `
  Show a single Webhook Subscription
    `,
  parameters: showSingleWebhookSubscriptionDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowSingleWebhookSubscriptionData, "url"> ) => {
    try {
      const { data } = await showSingleWebhookSubscription(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    